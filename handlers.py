import os

from telegram import Update

from telegram.ext import ContextTypes

from downloader import Downloader

from keyboards import quality_keyboard


USER_URL = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 لینک یوتیوب را ارسال کن."
    )


async def receive_url(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:

        await update.message.reply_text(
            "❌ لینک معتبر نیست."
        )

        return

    msg = await update.message.reply_text(
        "⏳ دریافت اطلاعات..."
    )

    try:

        info = Downloader.video_info(url)

        USER_URL[update.effective_user.id] = url

        qualities = Downloader.qualities(info)

        await msg.delete()

        await update.message.reply_photo(
            photo=info["thumbnail"],
            caption=f"""
🎬 {info['title']}

👤 {info['uploader']}

⏱ {info['duration']} ثانیه

کیفیت را انتخاب کنید:
""",
            reply_markup=quality_keyboard(qualities)
        )

    except Exception as e:

        await msg.edit_text(str(e))


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user = update.effective_user.id

    if user not in USER_URL:

        await query.edit_message_text(
            "لینک پیدا نشد."
        )

        return

    url = USER_URL[user]

    await query.edit_message_caption(
        caption="⏳ دانلود در حال انجام..."
    )

    try:

        if query.data == "audio":

            file, info = Downloader.download_audio(url)

            with open(file, "rb") as f:

                await context.bot.send_audio(
                    chat_id=query.message.chat.id,
                    audio=f,
                    caption=info["title"]
                )

            Downloader.cleanup(file)

            return

        quality = int(query.data.split(":")[1])

        file, info = Downloader.download_video(
            url,
            quality
        )

        with open(file, "rb") as f:

            await context.bot.send_video(
                chat_id=query.message.chat.id,
                video=f,
                caption=info["title"],
                supports_streaming=True
            )

        Downloader.cleanup(file)

    except Exception as e:

        await context.bot.send_message(
            query.message.chat.id,
            f"❌ {e}"
        )