import asyncio
import datetime
import os
import random
from zoneinfo import ZoneInfo
from aiohttp import web
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
TIMEZONE = ZoneInfo("Africa/Accra")

# SESSION BANNER IMAGES
AVIATOR_IMAGE_URL = "https://carder.top/imagens/1787956019513-490226521.jpg"
MINES_IMAGE_URL = "https://carder.top/imagens/1787956064400-230189890.jpg"
COIN_FLIP_IMAGE_URL = "https://carder.top/imagens/1787956065622-306701028.jpg"


def build_mines_grid() -> str:
    grid_size = 25
    safe_tiles = random.sample(range(1, grid_size + 1), 4)
    grid_display = ""
    for i in range(1, grid_size + 1):
        grid_display += "⭐ " if i in safe_tiles else "🟦 "
        if i % 5 == 0:
            grid_display += "\n\n"
    return grid_display


async def send_1min_warning(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    current_hour = now.hour

    if current_hour == 0 or (current_hour == 23 and now.minute > 54):
        return

    warning_text = (
        "🟡 *ALERT PREPARE YOUR BETS!* 🟡\n\n"
        "> 🔔 *Get ready for the next game!*\n"
        ">\n"
        "> ⏳ *Signal drops in 1 MINUTE.*\n"
        ">\n"
        "> 📱 *Open your 1Win app and stay ready!* ⚡\n\n"
        "⠀"
    )

    try:
        await bot.send_message(
            chat_id=CHANNEL_ID, text=warning_text, parse_mode="Markdown"
        )
        print(f"[{now.strftime('%H:%M:%S GMT')}] 1-minute alert sent.")
    except Exception as e:
        print(f"Failed to send 1-min alert to {CHANNEL_ID}: {e}")


async def send_hourly_predictions(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    current_hour = now.hour

    message = ""

    # 1. COIN FLIP SESSION (1:00 AM to 7:59 AM GMT)
    if 1 <= current_hour < 8:
        outcome = random.choice(["🪙 HEADS 🟡", "🪙 TAILS 🟢"])
        confidence = random.randint(91, 98)
        message = (
            "🟢 *LIVE SIGNAL 1WIN COIN FLIP* 🟢\n\n"
            ">\n"
            f"> 🎯 *Predicted Result:* `{outcome}`\n"
            ">\n"
            f"> 📊 *Bot Confidence:* `{confidence}%`\n"
            ">\n"
            "> ⚠️ *Bet within 2 minutes! Next game in 6 mins.* 💸\n\n"
            "⠀"
        )

    # 2. MINES SESSION (8:00 AM to 3:59 PM / 15:59 GMT)
    elif 8 <= current_hour < 16:
        grid = build_mines_grid()
        message = (
            "🟢 *LIVE SIGNAL 1WIN MINES* 🟢\n\n"
            ">\n"
            f"{grid}\n"
            "> 💣 *Recommended Mines:* `3`\n"
            ">\n"
            "> ⭐ *Safe Stars:* `4`\n"
            ">\n"
            "> ⚠️ *Accuracy: 98% (Next game in 6 mins)* 🤑\n\n"
            "⠀"
        )

    # 3. AVIATOR PREDICTION SESSION (4:00 PM / 16:00 to 10:59 PM / 22:59 GMT)
    elif 16 <= current_hour < 23:
        multiplier = round(random.uniform(1.35, 3.50), 2)
        message = (
            "🟢 *LIVE SIGNAL 1WIN AVIATOR* 🟢\n\n"
            ">\n"
            f"> 🚀 *Auto Cashout Target:* `{multiplier}x`\n"
            ">\n"
            "> ⏰ *Valid For:* `Next Flight`\n"
            ">\n"
            "> ⚠️ *Cash out strictly before target multiplier!* 💵\n\n"
            "⠀"
        )

    # 4. GOOD NIGHT SESSION (11:00 PM to 12:59 AM GMT)
    else:
        message = (
            "🔴 *OFFLINE SESSION ENDED* 🔴\n\n"
            ">\n"
            "> 🌙 *The VIP Bot algorithms are offline for maintenance.*\n"
            ">\n"
            "> 🪙 *Games resume tomorrow at 1:00 AM GMT.*\n"
            ">\n"
            "> 😴 *Rest up and manage your risk!* 💰\n\n"
            "⠀"
        )

    try:
        await bot.send_message(
            chat_id=CHANNEL_ID, text=message, parse_mode="Markdown"
        )
        print(f"[{now.strftime('%H:%M:%S GMT')}] Game signal sent to {CHANNEL_ID}")
    except Exception as e:
        print(f"Failed to send message to {CHANNEL_ID}: {e}")


async def send_30min_reminder(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    hour = now.hour
    next_game = None

    if hour == 0:
        next_game = "🪙 COIN FLIP"
    elif hour == 7:
        next_game = "🚀 MINES"
    elif hour == 15:
        next_game = "✈️ AVIATOR PREDICTION"

    if next_game:
        reminder_text = (
            "🔵 *INFO 30-MINUTE GAME CHANGE* 🔵\n\n"
            ">\n"
            f"> 📢 *Next session ({next_game}) starts in ⌛ 30 minutes!*\n"
            ">\n"
            "> 💰 *Deposit funds into your account now and prepare!* 🚀\n\n"
            "⠀"
        )
        try:
            if hour == 0:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=COIN_FLIP_IMAGE_URL,
                    caption=reminder_text,
                    parse_mode="Markdown",
                )
            elif hour == 7:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=MINES_IMAGE_URL,
                    caption=reminder_text,
                    parse_mode="Markdown",
                )
            elif hour == 15:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=AVIATOR_IMAGE_URL,
                    caption=reminder_text,
                    parse_mode="Markdown",
                )
            else:
                await bot.send_message(
                    chat_id=CHANNEL_ID, text=reminder_text, parse_mode="Markdown"
                )
            print(f"[{now.strftime('%H:%M:%S GMT')}] 30-min reminder sent.")
        except Exception as e:
            print(f"Failed to send reminder to {CHANNEL_ID}: {e}")


async def send_10min_transition(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    hour = now.hour

    ended_game = None
    next_game = None

    if hour == 0:
        ended_game = "✈️ AVIATOR PREDICTION"
        next_game = "🪙 COIN FLIP"
    elif hour == 7:
        ended_game = "🪙 COIN FLIP"
        next_game = "🚀 MINES"
    elif hour == 15:
        ended_game = "🚀 MINES"
        next_game = "✈️ AVIATOR PREDICTION"

    if next_game and ended_game:
        transition_text = (
            "🔵 *INFO SESSION TRANSITION* 🔵\n\n"
            ">\n"
            f"> 🛑 *Previous {ended_game} session has ended.*\n"
            ">\n"
            f"> ⏳ *Next session ({next_game}) begins in 10 MINUTES!*\n"
            ">\n"
            "> 🚨 *Get ready and open your apps!* 💸\n\n"
            "⠀"
        )
        try:
            if hour == 0:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=COIN_FLIP_IMAGE_URL,
                    caption=transition_text,
                    parse_mode="Markdown",
                )
            elif hour == 7:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=MINES_IMAGE_URL,
                    caption=transition_text,
                    parse_mode="Markdown",
                )
            elif hour == 15:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=AVIATOR_IMAGE_URL,
                    caption=transition_text,
                    parse_mode="Markdown",
                )
            else:
                await bot.send_message(
                    chat_id=CHANNEL_ID, text=transition_text, parse_mode="Markdown"
                )
            print(f"[{now.strftime('%H:%M:%S GMT')}] 10-min transition sent.")
        except Exception as e:
            print(f"Failed to send transition to {CHANNEL_ID}: {e}")


# HTTP handler to keep Render awake when pinged by UptimeRobot
async def handle_ping(request):
    print("Keep-alive ping received.")
    return web.Response(text="Bot is running!")


async def main():
    app = Application.builder().token(TOKEN).build()
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    # 1. Main Game Signals (Every 6 minutes)
    scheduler.add_job(
        send_hourly_predictions,
        "cron",
        minute="0,6,12,18,24,30,36,42,48,54",
        args=[app.bot],
    )

    # 2. Pre-Signal Warning (1 minute prior)
    scheduler.add_job(
        send_1min_warning,
        "cron",
        minute="5,11,17,23,29,35,41,47,53,59",
        args=[app.bot],
    )

    # 3. 30-Minute Game Reminders
    scheduler.add_job(
        send_30min_reminder,
        "cron",
        minute="30",
        hour="0,7,15",
        args=[app.bot],
    )

    # 4. 10-Minute Transition Warnings
    scheduler.add_job(
        send_10min_transition,
        "cron",
        minute="50",
        hour="0,7,15",
        args=[app.bot],
    )

    scheduler.start()
    print("Channel Predictor Bot is running continuously...")

    # Start HTTP server for Render port binding
    web_app = web.Application()
    web_app.router.add_get("/", handle_ping)
    runner = web.AppRunner(web_app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"HTTP dummy server running on port {port}")

    async with app:
        await app.start()
        print("Sending initial post on launch...")
        await send_hourly_predictions(app.bot)

        # Resilient infinite loop preventing disconnect crashes
        while True:
            try:
                await asyncio.Event().wait()
            except (KeyboardInterrupt, SystemExit):
                scheduler.shutdown()
                await app.stop()
                await runner.cleanup()
                break
            except Exception as e:
                print(f"Temporary connection error caught: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
