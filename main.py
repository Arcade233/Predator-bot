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

# REGISTRATION LINK
REGISTRATION_LINK = "https://1win.com"  # Replace with your affiliate link

# GLOBAL COUNTERS
trade_count = 1
current_balance = 500.00


def build_mines_grid() -> str:
    grid_size = 25
    safe_tiles = random.sample(range(1, grid_size + 1), 4)
    grid_display = ""
    for i in range(1, grid_size + 1):
        grid_display += "⭐ " if i in safe_tiles else "🟦 "
        if i % 5 == 0:
            grid_display += "\n"
    return grid_display


async def send_1min_warning(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    current_hour = now.hour

    if current_hour == 0 or (current_hour == 23 and now.minute > 54):
        return

    warning_text = "LAST SIGNAL 🗣️"

    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=warning_text)
        print(f"[{now.strftime('%H:%M:%S GMT')}] 'LAST SIGNAL' warning sent.")
    except Exception as e:
        print(f"Failed to send 1-min alert to {CHANNEL_ID}: {e}")


async def send_hourly_predictions(bot: Bot):
    global trade_count, current_balance
    now = datetime.datetime.now(TIMEZONE)
    current_hour = now.hour

    # 4. GOOD NIGHT / MAINTENANCE SESSION
    if current_hour == 0 or current_hour >= 23:
        night_text = (
            "🌙 *GOOD NIGHT TRADERS!* 🌙\n\n"
            "The VIP Bot algorithms are offline for maintenance.\n"
            "Games resume tomorrow at *1:00 AM GMT*.\n\n"
            "😴 _Rest up and manage your risk!_"
        )
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID, text=night_text, parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Failed to send goodnight message: {e}")
        return

    # STEP 1: PREVIOUS TRADE RESULT (Matches screenshot style)
    if trade_count > 1:
        profit = round(random.uniform(50.0, 150.0), 2)
        current_balance += profit
        result_text = (
            f"*{trade_count - 1}th TRADE* ✅\n\n"
            f"💲 *Current balance ${current_balance:,.2f}*\n\n"
            f"➡️ [REGISTRATION LINK]({REGISTRATION_LINK}) ⬅️"
        )
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=result_text,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
            await asyncio.sleep(2)  # Delay between messages
        except Exception as e:
            print(f"Failed to send trade result: {e}")

    # STEP 2: SETUP & BET INFO
    setup_text = ""
    direction_text = ""

    if 1 <= current_hour < 8:  # COIN FLIP
        outcome = random.choice(["HEADS 🟢", "TAILS 🟢"])
        bet_amount = random.choice([50, 100, 200, 350])
        setup_text = (
            "👉 *COIN FLIP (1WIN)*\n"
            "⏱ *2 MINUTE*\n"
            f"💲 *Use {bet_amount} $ from balance*\n\n"
            f"➡️ [REGISTRATION LINK]({REGISTRATION_LINK}) ⬅️"
        )
        direction_text = f"*{outcome}*"

    elif 8 <= current_hour < 16:  # MINES
        grid = build_mines_grid()
        setup_text = (
            "👉 *MINES (1WIN)*\n"
            "⏱ *3 MINUTE*\n"
            "💲 *Use 200 $ from balance*\n\n"
            f"➡️ [REGISTRATION LINK]({REGISTRATION_LINK}) ⬅️"
        )
        direction_text = f"🚀 *SAFE TILES:*\n\n{grid}"

    elif 16 <= current_hour < 23:  # AVIATOR
        multiplier = round(random.uniform(1.35, 3.50), 2)
        setup_text = (
            "👉 *AVIATOR (1WIN)*\n"
            "⏱ *NEXT FLIGHT*\n"
            "💲 *Use 150 $ from balance*\n\n"
            f"➡️ [REGISTRATION LINK]({REGISTRATION_LINK}) ⬅️"
        )
        direction_text = f"UP 🟢 *Target:* `{multiplier}x`"

    # SEND STEP 2 (Setup info)
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=setup_text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
        print(f"[{now.strftime('%H:%M:%S GMT')}] Setup signal sent.")
        
        await asyncio.sleep(3)  # Wait 3 seconds before sending direction

        # SEND STEP 3 (Direction / Action message like "UP 🟢")
        await bot.send_message(
            chat_id=CHANNEL_ID, text=direction_text, parse_mode="Markdown"
        )
        print(f"[{now.strftime('%H:%M:%S GMT')}] Direction signal sent.")

        trade_count += 1

    except Exception as e:
        print(f"Failed to send setup/direction signal: {e}")


async def send_30min_reminder(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    hour = now.hour
    next_game = None

    if hour == 0:
        next_game = "COIN FLIP"
    elif hour == 7:
        next_game = "MINES"
    elif hour == 15:
        next_game = "AVIATOR"

    if next_game:
        reminder_text = (
            "🚨 *30-MINUTE SESSION WARNING* 🚨\n\n"
            f"The next game session (*{next_game}*) starts in 30 minutes!\n\n"
            f"➡️ [REGISTRATION LINK]({REGISTRATION_LINK}) ⬅️"
        )
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=reminder_text,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
        except Exception as e:
            print(f"Failed to send 30-min reminder: {e}")


async def send_10min_transition(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    hour = now.hour

    ended_game = None
    next_game = None

    if hour == 0:
        ended_game = "AVIATOR"
        next_game = "COIN FLIP"
    elif hour == 7:
        ended_game = "COIN FLIP"
        next_game = "MINES"
    elif hour == 15:
        ended_game = "MINES"
        next_game = "AVIATOR"

    if next_game and ended_game:
        transition_text = (
            "🏁 *SESSION ENDED* 🏁\n\n"
            f"The *{ended_game}* session has closed.\n"
            f"Next session (*{next_game}*) starts in **10 minutes**!\n\n"
            f"➡️ [REGISTRATION LINK]({REGISTRATION_LINK}) ⬅️"
        )
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=transition_text,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
        except Exception as e:
            print(f"Failed to send 10-min transition: {e}")


# HTTP handler for Render's port detection
async def handle_ping(request):
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

        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            await app.stop()
            await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
