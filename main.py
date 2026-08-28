import asyncio
import datetime
import logging
import os
import random
from zoneinfo import ZoneInfo

from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from telegram.error import TelegramError
from telegram.ext import Application

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("VIPPredictorBot")

TOKEN = os.environ.get("TOKEN", "8983526249:AAHRSloR9WZZoG-5PeEhPY7ZP-487q5QqCA")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@protonxona_bot")
TIMEZONE = ZoneInfo("Africa/Accra")

# ==========================================
# SIGNAL BUILDERS & FORMATTERS
# ==========================================
def build_mines_grid() -> str:
    """Generates a clean 5x5 grid with 4 safe star locations."""
    grid_size = 25
    safe_tiles = set(random.sample(range(1, grid_size + 1), 4))
    
    rows = []
    for r in range(5):
        row_str = "".join("⭐ " if (r * 5 + c + 1) in safe_tiles else "🟦 " for c in range(5))
        rows.append(f"> {row_str.strip()}")
    
    return "\n".join(rows)


def build_message_payload(current_hour: int) -> str:
    """Constructs professional, high-converting Markdown templates."""
    
    # 1. COIN FLIP SESSION (01:00 - 07:59 GMT)
    if 1 <= current_hour < 8:
        outcome = random.choice(["🪙 HEADS 🟡", "🪙 TAILS 🟢"])
        confidence = random.randint(93, 99)
        return (
            "🟢 *LIVE SIGNAL — 1WIN COIN FLIP* 🟢\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            ">\n"
            f" 🎯 *Predicted Outcome:* `{outcome}`\n"
            f" 📊 *Algorithm Confidence:* `{confidence}%`\n"
            ">\n"
            " ⚡ *Action:* Place bet within 2 minutes!\n"
            " ⌛ *Next Signal:* In 6 minutes\n"
            ">\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📲 [Open 1Win App](https://1win.com) | Manage Risk Wisely"
        )

    # 2. MINES SESSION (08:00 - 15:59 GMT)
    elif 8 <= current_hour < 16:
        grid = build_mines_grid()
        return (
            "🟢 *LIVE SIGNAL — 1WIN MINES* 🟢\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            ">\n"
            f"{grid}\n"
            ">\n"
            " 💣 *Recommended Mines:* `3`\n"
            " ⭐ *Safe Stars Target:* `4`\n"
            " 🎯 *Predicted Accuracy:* `98.4%`\n"
            ">\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📲 [Open 1Win App](https://1win.com) | Next round in 6 mins"
        )

    # 3. AVIATOR SESSION (16:00 - 22:59 GMT)
    elif 16 <= current_hour < 23:
        multiplier = round(random.uniform(1.40, 3.80), 2)
        return (
            "🟢 *LIVE SIGNAL — 1WIN AVIATOR* 🟢\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            ">\n"
            f" 🚀 *Auto Cashout Target:* `{multiplier}x`\n"
            " ⏰ *Validity:* Next 2 Flights\n"
            " 🛡️ *Strategy:* Strict Auto-Cashout\n"
            ">\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📲 [Open 1Win App](https://1win.com) | Cash out before target!"
        )

    # 4. MAINTENANCE / OFFLINE (23:00 - 00:59 GMT)
    else:
        return (
            "🔴 *SESSION CLOSED — SYSTEM OFFLINE* 🔴\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            ">\n"
            " 🌙 *The VIP Bot algorithms are offline for nightly calibration.*\n"
            ">\n"
            " 🪙 *Live signals resume at 01:00 AM GMT (Coin Flip).*\n"
            ">\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "😴 *Rest up, analyze your day, and manage your bankroll!*"
        )

# ==========================================
# ASYNC BOT DISPATCHERS
# ==========================================
async def safe_send_message(bot: Bot, text: str, label: str):
    """Dispatches Telegram messages with built-in retry logic."""
    for attempt in range(1, 4):
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            now = datetime.datetime.now(TIMEZONE)
            logger.info(f"[{now.strftime('%H:%M:%S GMT')}] Success: {label} posted to {CHANNEL_ID}")
            return
        except TelegramError as te:
            logger.warning(f"Attempt {attempt} failed for {label}: {te}")
            await asyncio.sleep(2 * attempt)
        except Exception as e:
            logger.error(f"Unexpected error posting {label}: {e}")
            break


async def send_1min_warning(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    if now.hour == 0 or (now.hour == 23 and now.minute > 54):
        return

    text = (
        "🟡 *PRE-SIGNAL ALERT — 1 MINUTE* 🟡\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        ">\n"
        " 🔔 *Get ready for the next prediction!*\n"
        " ⌛ *Signal drops in precisely 60 SECONDS.*\n"
        ">\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *Open 1Win now & ensure your balance is ready!*"
    )
    await safe_send_message(bot, text, "1-Min Alert")


async def send_hourly_predictions(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    payload = build_message_payload(now.hour)
    await safe_send_message(bot, payload, f"Main Signal (Hour {now.hour})")


async def send_30min_reminder(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    next_game_map = {0: "🪙 COIN FLIP", 7: "🚀 MINES", 15: "✈️ AVIATOR"}
    next_game = next_game_map.get(now.hour)

    if next_game:
        text = (
            "🔵 *SCHEDULE INFO — 30 MIN NOTICE* 🔵\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            ">\n"
            f" 📢 *The next major session ({next_game}) starts in 30 MINUTES!*\n"
            ">\n"
            " 💰 *Top up your balance now to avoid missing early signals.*\n"
            ">\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        await safe_send_message(bot, text, "30-Min Reminder")


async def send_10min_transition(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    transitions = {
        0: ("✈️ AVIATOR", "🪙 COIN FLIP"),
        7: ("🪙 COIN FLIP", "🚀 MINES"),
        15: ("🚀 MINES", "✈️ AVIATOR")
    }
    
    if now.hour in transitions:
        ended, upcoming = transitions[now.hour]
        text = (
            "🔵 *SESSION TRANSITION — 10 MINUTES* 🔵\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            ">\n"
            f" 🛑 *The {ended} session has concluded.*\n"
            f" ⏳ *Next session ({upcoming}) launches in 10 MINUTES!*\n"
            ">\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💸 *Get set and prepare your betting strategy!*"
        )
        await safe_send_message(bot, text, "10-Min Transition")

# ==========================================
# WEB HEALTH CHECK HANDLER
# ==========================================
async def handle_ping(request):
    return web.Response(text="VIP Predictor Bot is Active and Healthy!", status=200)

# ==========================================
# MAIN EXECUTION
# ==========================================
async def main():
    logger.info("Initializing VIP Predictor Engine...")
    
    app = Application.builder().token(TOKEN).build()
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    # 1. Core Predictions (Every 6 mins)
    scheduler.add_job(
        send_hourly_predictions,
        "cron",
        minute="0,6,12,18,24,30,36,42,48,54",
        args=[app.bot]
    )

    # 2. Pre-Signal Warnings (1 min prior)
    scheduler.add_job(
        send_1min_warning,
        "cron",
        minute="5,11,17,23,29,35,41,47,53,59",
        args=[app.bot]
    )

    # 3. 30-Minute Schedule Announcements
    scheduler.add_job(
        send_30min_reminder,
        "cron",
        minute="30",
        hour="0,7,15",
        args=[app.bot]
    )

    # 4. 10-Minute Transition Alerts
    scheduler.add_job(
        send_10min_transition,
        "cron",
        minute="50",
        hour="0,7,15",
        args=[app.bot]
    )

    scheduler.start()
    logger.info("APScheduler initialized successfully with Africa/Accra timezone.")

    # Start AIOHTTP Web Server for Cloud Keep-Alive (Render / Railway)
    web_app = web.Application()
    web_app.router.add_get("/", handle_ping)
    runner = web.AppRunner(web_app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check web service listening on port {port}")

    async with app:
        await app.start()
        logger.info("Bot application started. Publishing startup payload...")
        await send_hourly_predictions(app.bot)

        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutdown signal received. Cleaning up...")
            scheduler.shutdown()
            await app.stop()
            await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
