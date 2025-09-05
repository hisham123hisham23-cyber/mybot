import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# التوكن
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6153632775  # ID بتاعك

# قاعدة بيانات الكتب
BOOKS = {
    "فيزياء": {
        "نيوتن فيزيا ⚛️": "https://t.me/Htalta26/209?single",
        "التفوق فيزياء": "https://t.me/Htalta26/75?single",
    },
    "كيمياء": {
        "افوجادرو كيمياء شرح 🧪": "https://t.me/Htalta26/7",
        "التفوق اسئلة كيمياء": "https://t.me/Htalta26/144?single",
    }
}

# حالات الإدمن
ADMIN_STATES = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        if update.effective_user.id == ADMIN_ID:
            keyboard = [
                [InlineKeyboardButton("➕ إضافة كتاب", callback_data="admin_add")],
                [InlineKeyboardButton("❌ حذف كتاب", callback_data="admin_remove")]
            ]
            await update.message.reply_text(
                "اهلا يا ادمن 👑.\nاختار اللي تحب تعمله:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text("للتواصل مع المطور: @HESHVM1")
    else:
        await update.message.reply_text("اهلا بيكم في بوت الكتب 📚")

# زرار الأدمن
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        return

    if query.data == "admin_add":
        ADMIN_STATES[user_id] = {"mode": "add", "step": "subj"}
        await query.message.reply_text("➕ اكتب اسم المادة:")
    elif query.data == "admin_remove":
        ADMIN_STATES[user_id] = {"mode": "remove", "step": "subj"}
        await query.message.reply_text("❌ اكتب اسم المادة:")

# متابعة محادثة الأدمن
async def admin_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID or user_id not in ADMIN_STATES:
        return False  # مش أدمن أو مفيش حالة

    state = ADMIN_STATES[user_id]
    text = update.message.text.strip()

    # إضافة كتاب
    if state["mode"] == "add":
        if state["step"] == "subj":
            state["subj"] = text
            state["step"] = "name"
            await update.message.reply_text("📘 اكتب اسم الكتاب:")
        elif state["step"] == "name":
            state["name"] = text
            state["step"] = "link"
            await update.message.reply_text("🔗 ابعت لينك الكتاب:")
        elif state["step"] == "link":
            subj, name, link = state["subj"], state["name"], text
            if subj not in BOOKS:
                BOOKS[subj] = {}
            BOOKS[subj][name] = link
            await update.message.reply_text(f"✅ اتضاف كتاب {name} في {subj}")
            del ADMIN_STATES[user_id]

    # حذف كتاب
    elif state["mode"] == "remove":
        if state["step"] == "subj":
            state["subj"] = text
            state["step"] = "name"
            await update.message.reply_text("📘 اكتب اسم الكتاب اللي عايز تحذفه:")
        elif state["step"] == "name":
            subj, name = state["subj"], text
            if subj in BOOKS and name in BOOKS[subj]:
                del BOOKS[subj][name]
                await update.message.reply_text(f"✅ اتحذف {name} من {subj}")
            else:
                await update.message.reply_text("❌ الكتاب مش موجود")
            del ADMIN_STATES[user_id]

    return True

# عرض كل المواد
async def all_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(subj, callback_data=f"subj:{subj}")] for subj in BOOKS.keys()]
    await update.message.reply_text("اختر المادة:", reply_markup=InlineKeyboardMarkup(keyboard))

# لما يدوس على مادة
async def button_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("subj:"):
        subj = query.data.split(":")[1]
        books = BOOKS.get(subj, {})
        keyboard = [[InlineKeyboardButton(name, url=link)] for name, link in books.items()]
        keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="back")])
        await query.edit_message_text(f"كتب {subj}:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "back":
        keyboard = [[InlineKeyboardButton(subj, callback_data=f"subj:{subj}")] for subj in BOOKS.keys()]
        await query.edit_message_text("اختر المادة:", reply_markup=InlineKeyboardMarkup(keyboard))

# بحث بالاسم
async def search_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    for subj, books in BOOKS.items():
        if text == subj:
            keyboard = [[InlineKeyboardButton(name, url=link)] for name, link in books.items()]
            await update.message.reply_text(f"كتب {subj}:", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        for name, link in books.items():
            if text in name:
                keyboard = [[InlineKeyboardButton(name, url=link)]]
                await update.message.reply_text(f"لقيت الكتاب في {subj}:", reply_markup=InlineKeyboardMarkup(keyboard))
                return

# main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(button_subject, pattern="^(subj:|back)"))
    app.add_handler(MessageHandler(filters.Regex("كتب"), all_books))

    # الأول يتشيك إذا الأدمن في محادثة
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        done = await admin_conversation(update, context)
        if not done:  # لو مش إدمن أو مفيش حالة
            await search_books(update, context)

    app.add_handler(MessageHandler(filters.TEXT, handler))

    app.run_polling()

if __name__ == "__main__":
    main()