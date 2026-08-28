import asyncio
import datetime
import os
import random
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from telegram.ext import Application

# CONFIGURATION
TOKEN = os.environ.get(
    "TOKEN", "8983526249:AAHRSloR9WZZoG-5PeEhPY7ZP-487q5QqCA"
)
CHANNEL_ID = (
    "@protonxona_bot"  # Ensure the bot is added as an Admin in this channel!
)


def build_mines_grid() -> str:
    grid_size = 25
    safe_tiles = random.sample(range(1, grid_size + 1), 4)
    grid_display = ""
    for i in range(1, grid_size + 1):
        grid_display += "⭐ " if i in safe_tiles else "🟦 "
        if i % 5 == 0:
            grid_display += "\n"
    return grid_display


async def send_hourly_predictions(bot: Bot):
    # Fetch local current time (Explicit UTC / GMT timezone to avoid Android crashes)
    now = datetime.datetime.now(ZoneInfo("UTC"))
    current_hour = now.hour

    # 1. MINES SESSION (1:00 AM to 7:00 AM)
    if 1 <= current_hour <= 7:
        grid = build_mines_grid()
        message = (
            "🚀 *1WIN MINES SIGNAL* 🚀\n\n"
            f"{grid}\n"
            "🎯 *Recommended Mines:* 3\n"
            "⭐ *Safe Stars:* 4\n"
            "⚠️ _Accuracy: 98% (Next round in 6 mins)_"
        )

    # 2. FLIP THE COIN SESSION (8:00 AM to 3:00 PM / 15:00)
    elif 8 <= current_hour <= 15:
        outcome = random.choice(["🪙 HEADS", "🪙 TAILS"])
        confidence = random.randint(91, 98)
        message = (
            "🪙 *1WIN COIN FLIP SIGNAL* 🪙\n\n"
            f"🎯 *Predicted Result:* {outcome}\n"
            f"📊 *Bot Confidence:* {confidence}%\n\n"
            "⚠️ _Bet within 2 minutes! Next signal in 6 mins._"
        )

    # 3. AVIATOR PREDICTION SESSION (4:00 PM / 16:00 to 11:00 PM / 23:00)
    elif 16 <= current_hour <= 23:
        multiplier = round(random.uniform(1.35, 3.50), 2)
        message = (
            "✈️ *1WIN AVIATOR PREDICTION* ✈️\n\n"
            f"🚀 *Auto Cashout Target:* {multiplier}x\n"
            "⏰ *Valid For:* Next Flight\n\n"
            "⚠️ _Cash out strictly before target multiplier! Next signal in 6 mins._"
        )

    # 4. GOOD NIGHT SESSION (11:01 PM to 12:59 AM)
    else:
        message = (
            "🌙 *GOOD NIGHT TRADERS!* 🌙\n\n"
            "The VIP Bot algorithms are now offline for maintenance.\n"
            "Signals will resume tomorrow at *1:00 AM* with the Mines predictor.\n\n"
            "😴 _Rest up and practice sound risk management!_"
        )

    try:
        await bot.send_message(
            chat_id=CHANNEL_ID, text=message, parse_mode="Markdown"
        )
        print(f"[{now.strftime('%H:%M:%S UTC')}] Signal sent to {CHANNEL_ID}")
    except Exception as e:
        print(f"Failed to send message to {CHANNEL_ID}: {e}")


async def main():
    # Build Application
    app = Application.builder().token(TOKEN).build()

    # Configure APScheduler with explicit timezone for Android/Pydroid 3 support
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("UTC"))

    # Add job to scheduler (Runs every 6 minutes)
    scheduler.add_job(
        send_hourly_predictions,
        "interval",
        minutes=6,
        args=[app.bot],
    )

    scheduler.start()
    print("Channel Predictor Bot is running continuously...")

    # Initialize Application context
    async with app:
        await app.start()

        # Send an immediate test post upon launching
        print("Sending initial signal on launch...")
        await send_hourly_predictions(app.bot)

        # Keep event loop alive indefinitely
        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
