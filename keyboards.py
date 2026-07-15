from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def quality_keyboard(qualities: list[int]):

    keyboard = []

    keyboard.append([
        InlineKeyboardButton(
            "🎵 MP3",
            callback_data="audio"
        )
    ])

    row = []

    for q in qualities:

        row.append(
            InlineKeyboardButton(
                f"{q}p",
                callback_data=f"video:{q}"
            )
        )

        if len(row) == 3:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)