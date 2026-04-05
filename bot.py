import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# BOT TOKEN (CLOUD SAFE)
# =========================
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# =========================
# IN-MEMORY STORAGE
# =========================
notes = {}
# structure:
# {
#   "math": {
#       "text": ["note1", "note2"],
#       "images": [{"file_id": "...", "caption": "..."}]
#   }
# }

# =========================
# COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Notes Bot\n\n"
        "Commands:\n"
        "/addnote <section> <text>\n"
        "/addimage <section> <description> (send with image)\n"
        "/getnotes <section>"
    )

async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Usage:\n/addnote <section> <text>"
        )
        return

    section = context.args[0].lower()
    text = " ".join(context.args[1:])

    if section not in notes:
        notes[section] = {"text": [], "images": []}

    notes[section]["text"].append(text)

    await update.message.reply_text(
        f"✅ Text note added to section: {section}"
    )

async def get_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ Usage:\n/getnotes <section>"
        )
        return

    section = context.args[0].lower()

    if section not in notes:
        await update.message.reply_text(
            "❌ No notes found for this section."
        )
        return

    data = notes[section]

    # Send text notes
    if data["text"]:
        text_output = "\n\n".join(
            f"📝 {i+1}. {note}"
            for i, note in enumerate(data["text"])
        )
        await update.message.reply_text(
            f"📄 Notes for *{section}*:\n\n{text_output}",
            parse_mode="Markdown"
        )

    # Send image notes
    for img in data["images"]:
        await update.message.reply_photo(
            photo=img["file_id"],
            caption=f"🖼 {img['caption']}"
        )

async def add_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message.photo or not message.caption:
        return

    caption = message.caption.strip()

    if not caption.startswith("/addimage"):
        return

    parts = caption.split(maxsplit=2)

    if len(parts) < 3:
        await message.reply_text(
            "❌ Send an image with caption:\n/addimage <section> <description>"
        )
        return

    section = parts[1].lower()
    description = parts[2]
    photo = message.photo[-1]

    if section not in notes:
        notes[section] = {"text": [], "images": []}

    notes[section]["images"].append({
        "file_id": photo.file_id,
        "caption": description
    })

    await message.reply_text(
        f"🖼 Image note added to section: {section}"
    )

# =========================
# MAIN
# =========================
def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN not set")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addnote", add_note))
    app.add_handler(CommandHandler("getnotes", get_notes))
    app.add_handler(MessageHandler(filters.PHOTO, add_image))

    print("🤖 Notes bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()