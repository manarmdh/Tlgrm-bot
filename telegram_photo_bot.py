import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler,)

import os
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8723529865:AAGaZkVpX2mSKL6cNWUfhy-rsdPhWfREcaQ")
ADMIN_IDS = [5842678175, 1005258580]  
CHOOSE_TYPE, CHOOSE_WILAYA, SEND_PHOTOS = range(3)

PHOTO_TYPES = [
    " صور المقرأة",
    " صور الأكاديمية",
    " صور المخيمات الحضورية",
    " صور المخيمات الإلكترونية",
    " صور المدارس القرآنية النموذجية", ]
WILAYAS = [
    "01-أدرار",            "02-الشلف",            "03-الأغواط",          "04-أم البواقي",
    "05-باتنة",            "06-بجاية",            "07-بسكرة",            "08-بشار",
    "09-البليدة",          "10-البويرة",          "11-تمنراست",          "12-تبسة",
    "13-تلمسان",           "14-تيارت",            "15-تيزي وزو",         "16-الجزائر",
    "17-الجلفة",           "18-جيجل",             "19-سطيف",             "20-سعيدة",
    "21-سكيكدة",           "22-سيدي بلعباس",     "23-عنابة",            "24-قالمة",
    "25-قسنطينة",          "26-المدية",           "27-مستغانم",          "28-المسيلة",
    "29-معسكر",            "30-ورقلة",            "31-وهران",            "32-البيض",
    "33-إليزي",            "34-برج بوعريريج",    "35-بومرداس",          "36-الطارف",
    "37-تندوف",            "38-تيسمسيلت",        "39-الوادي",           "40-خنشلة",
    "41-سوق أهراس",        "42-تيبازة",          "43-ميلة",             "44-عين الدفلى",
    "45-النعامة",          "46-عين تموشنت",      "47-غرداية",           "48-غليزان",
    "49-تيميمون",          "50-برج باجي مختار",  "51-أولاد جلال",       "52-بني عباس",
    "53-عين صالح",         "54-عين قزام",        "55-تقرت",             "56-جانت",
    "57-المغير",           "58-المنيعة",          "59-بريكة",
]
WILAYAS_PER_PAGE = 12
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def build_type_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(t, callback_data=f"type|{i}")
        for i, t in enumerate(PHOTO_TYPES)
    ]
    keyboard = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(keyboard)

def build_wilaya_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    start = page * WILAYAS_PER_PAGE
    end   = min(start + WILAYAS_PER_PAGE, len(WILAYAS))

    buttons = [
        InlineKeyboardButton(WILAYAS[start + i], callback_data=f"wilaya|{start + i}")
        for i in range(end - start)
    ]
    keyboard = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ السابق", callback_data=f"page|{page - 1}"))
    if end < len(WILAYAS):
        nav.append(InlineKeyboardButton("التالي ▶️", callback_data=f"page|{page + 1}"))
    if nav:
        keyboard.append(nav)

    total_pages = -(-len(WILAYAS) // WILAYAS_PER_PAGE)
    keyboard.append([
        InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="noop")
    ])

    return InlineKeyboardMarkup(keyboard)


async def notify_admins_photo(context, file_id: str, caption: str):
    """يبعث الصورة لكل أدمن في ADMIN_IDS"""
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=caption,
            )
        except Exception as e:
            logger.warning(f"لم يستطيع الإرسال للادمين {admin_id}: {e}")

async def notify_admins_text(context, text: str):
    """يبعث رسالة نصية لكل أدمن في ADMIN_IDS"""
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=text)
        except Exception as e:
            logger.warning(f"لم يستطيع الإرسال للادمين {admin_id}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "📸 *أهلاً بك!*\n\n اختر *نوع* الصور اللي تُريد ارسالها:",
        parse_mode="Markdown",
        reply_markup=build_type_keyboard(),
    )
    return CHOOSE_TYPE

async def handle_type_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    _, idx = query.data.split("|")
    chosen = PHOTO_TYPES[int(idx)]
    context.user_data["photo_type"] = chosen

    await query.edit_message_text(
        f"✅ اخترت: *{chosen}*\n\nدوراً اختر *الولاية*:",
        parse_mode="Markdown",
        reply_markup=build_wilaya_keyboard(page=0),
    )
    return CHOOSE_WILAYA

async def handle_page_nav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    _, page_str = query.data.split("|")
    await query.edit_message_reply_markup(
        reply_markup=build_wilaya_keyboard(page=int(page_str))
    )
    return CHOOSE_WILAYA


async def handle_noop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    return CHOOSE_WILAYA


async def handle_wilaya_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, idx = query.data.split("|")
    chosen_wilaya = WILAYAS[int(idx)]
    context.user_data["wilaya"]  = chosen_wilaya
    context.user_data["photos"]  = []

    photo_type = context.user_data["photo_type"]

    folder = os.path.join("photos", photo_type.replace(" ", "_"), chosen_wilaya)
    os.makedirs(folder, exist_ok=True)
    context.user_data["save_folder"] = folder

    await query.edit_message_text(
        f"✅ *{photo_type}* | 📍 *{chosen_wilaya}*\n\n"
        "الآن ابعث الصور 📤\n"
        "_(يمكنك إرسال أكثر من صورة)_\n\n"
        "اكتب /done إذ انتهيت !، أو /cancel لإلغاء",
        parse_mode="Markdown",
    )
    return SEND_PHOTOS

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo  = update.message.photo[-1]  # أعلى جودة
    file   = await photo.get_file()

    folder    = context.user_data["save_folder"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename  = os.path.join(folder, f"{timestamp}.jpg")
    await file.download_to_drive(filename)

    context.user_data["photos"].append(filename)
    count = len(context.user_data["photos"])

    await update.message.reply_text(
        f"✅ تم استقبال الصورة ({count})\n"
        "أرسل المزيد أو اكتب /done للإنهاء"
    )
    user     = update.effective_user
    username = f"@{user.username}" if user.username else "بدون يوزرنيم"
    caption  = (
        f"📸 صورة جديدة رقم {count}\n"
        f"👤 {user.full_name} ({username})\n"
        f"🆔 ID: {user.id}\n"
        f"🏷️ النوع: {context.user_data['photo_type']}\n"
        f"📍 الولاية: {context.user_data['wilaya']}"
    )
    await notify_admins_photo(context, photo.file_id, caption)
    return SEND_PHOTOS
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    count = len(context.user_data.get("photos", []))
    ptype = context.user_data.get("photo_type", "")
    wil   = context.user_data.get("wilaya", "")
    user  = update.effective_user

    if count == 0:
        await update.message.reply_text(
            "⚠️ لم تُرسل أي صورة!\nارسل على الأقل صورة واحدة أو اكتب /cancel"
        )
        return SEND_PHOTOS

    await update.message.reply_text(
        f"🎉 *شكراً!* تم استقبال *{count}* صورة\n"
        f"🏷️ النوع: {ptype}\n"
        f"📍 الولاية: {wil}\n\n"
        "اكتب /start لإرسال مجموعة جديدة",
        parse_mode="Markdown",
    )

    username = f"@{user.username}" if user.username else "بدون يوزرنيم"
    await notify_admins_text(
        context,
        f"✅ انتهى الإرسال\n"
        f"👤 {user.full_name} ({username})\n"
        f"🆔 ID: {user.id}\n"
        f"🏷️ {ptype} | 📍 {wil}\n"
        f"📊 المجموع: {count} صورة"
    )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "❌ تم الإلغاء.\nاكتب /start للبدء من جديد"
    )
    return ConversationHandler.END


def main():
    os.makedirs("photos", exist_ok=True)

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_TYPE: [
                CallbackQueryHandler(handle_type_choice, pattern=r"^type\|"),
            ],
            CHOOSE_WILAYA: [
                CallbackQueryHandler(handle_wilaya_choice, pattern=r"^wilaya\|"),
                CallbackQueryHandler(handle_page_nav,      pattern=r"^page\|"),
                CallbackQueryHandler(handle_noop,          pattern=r"^noop$"),
            ],
            SEND_PHOTOS: [
                MessageHandler(filters.PHOTO, handle_photo),
                CommandHandler("done", done),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    logger.info("البوت يشتغل ✅")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
