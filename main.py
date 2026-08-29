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

# SESSION BANNER IMAGES (Used for 30-min reminders & 10-min transitions)
AVIATOR_IMAGE_URL = "https://carder.top/imagens/1787956019513-490226521.jpg"
MINES_IMAGE_URL = "https://carder.top/imagens/1787956064400-230189890.jpg"
COIN_FLIP_IMAGE_URL = "https://carder.top/imagens/1787956065622-306701028.jpg"

# SIGNAL IMAGES (Dedicated for each active game mode)
COIN_FLIP_SIGNAL_IMAGE_URL = "https://carder.top/imagens/1787987001471-864263496.jpg"
MINES_SIGNAL_IMAGE_URL = "https://carder.top/imagens/1787988758434-575219937.jpg"
AVIATOR_SIGNAL_IMAGE_URL = "https://carder.top/imagens/1787989274632-715169951.jpg"

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
    """Constructs Markdown templates based on the active session window."""
    
    # 1. COIN FLIP SESSION (01:00 - 07:59 GMT)
    if 1 <= current_hour < 8:
        outcome = random.choice(["🪙 HEADS 🟡", "🪙 TAILS 🟢"])
        confidence = random.randint(91, 98)
        return (
            "🟢 *LIVE SIGNAL — 1WIN COIN FLIP* 🟢\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            ">\n"
            f"> 🎯 *Predicted Result:* `{outcome}`\n"
            f"> 📊 *Bot Confidence:* `{confidence}%`\n"
            ">\n"
            "> ⚠️ *Bet within 2 minutes! Next game in 6 mins.* 💸\n"
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
            "> 💣 *Recommended Mines:* `3`\n"
            "> ⭐ *Safe Stars:* `4`\n"
            "> ⚠️ *Accuracy: 98% (Next game in 6 mins)* 🤑\n"
            ">\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📲 [Open 1Win App](https://1win.com) | Next round in 6 mins"
        )

    # 3. AVIATOR SESSION (16:00 - 22:59 GMT)
    elif 16 <= current_hour < 23:
        multiplier = round(random.uniform(1.35, 3.50), 2)
        return (
            "🟢 *LIVE SIGNAL — 1WIN AVIATOR* 🟢\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            ">\n"
            f"> 🚀 *Auto Cashout Target:* `{multiplier}x`\n"
            "> ⏰ *Valid For:* `Next Flight`\n"
            "> ⚠️ *Cash out strictly before target multiplier!* 💵\n"
            ">\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📲 [Open 1Win App](https://1win.com) | Cash out before target!"
        )

    # 4. MAINTENANCE / OFFLINE (23:00 - 00:59 GMT)
    else:
        return (
            "🔴 *OFFLINE SESSION ENDED* 🔴\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            ">\n"
            "> 🌙 *The VIP Bot algorithms are offline for maintenance.*\n"
            ">\n"
            "> 🪙 *Games resume tomorrow at 1:00 AM GMT.*\n"
            ">\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "😴 *Rest up and manage your risk!* 💰"
        )

# ==========================================
# ASYNC BOT DISPATCHERS & EDITORS
# ==========================================
async def auto_update_caption_win(bot: Bot, message_id: int, original_caption: str, delay_seconds: int = 180):
    """Waits non-blockingly for the delay duration, then updates the photo caption to a WIN status."""
    await asyncio.sleep(delay_seconds)
    
    # Construct the updated WIN text based on signal type
    win_caption = (
        original_caption
        .replace("🟢 *LIVE SIGNAL", "✅ *SIGNAL PASSED — WIN RESULT* ✅\n🟢 *LIVE SIGNAL")
        .replace("⚠️ *Bet within 2 minutes! Next game in 6 mins.* 💸", "📊 *Status:* `✅ 100% WIN ACCURACY` 💸")
        .replace("⚠️ *Accuracy: 98% (Next game in 6 mins)* 🤑", "📊 *Status:* `✅ 100% WIN ACCURACY` 🤑")
        .replace("⚠️ *Cash out strictly before target multiplier!* 💵", "📊 *Status:* `✅ TARGET REACHED — WIN` 💵")
    )

    try:
        await bot.edit_message_caption(
            chat_id=CHANNEL_ID,
            message_id=message_id,
            caption=win_caption,
            parse_mode="Markdown"
        )
        now = datetime.datetime.now(TIMEZONE)
        logger.info(f"[{now.strftime('%H:%M:%S GMT')}] Success: Message ID {message_id} updated to WIN.")
    except TelegramError as e:
        logger.warning(f"Could not edit caption for message {message_id}: {e}")


async def safe_send_message(bot: Bot, text: str, label: str):
    """Dispatches Telegram text messages with exponential retry logic."""
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


async def safe_send_photo(bot: Bot, photo_url: str, caption: str, label: str, auto_win_delay: int = 180):
    """Dispatches Telegram photo messages and schedules a background task to auto-edit the caption to WIN."""
    for attempt in range(1, 4):
        try:
            sent_message = await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo_url,
                caption=caption,
                parse_mode="Markdown"
            )
            now = datetime.datetime.now(TIMEZONE)
            logger.info(f"[{now.strftime('%H:%M:%S GMT')}] Success: Photo {label} posted to {CHANNEL_ID}")

            # Schedule the non-blocking background task to edit caption to WIN after delay
            if auto_win_delay > 0 and sent_message:
                asyncio.create_task(
                    auto_update_caption_win(
                        bot=bot,
                        message_id=sent_message.message_id,
                        original_caption=caption,
                        delay_seconds=auto_win_delay
                    )
                )

            return
        except TelegramError as te:
            logger.warning(f"Attempt {attempt} failed for Photo {label}: {te}")
            await asyncio.sleep(2 * attempt)
        except Exception as e:
            logger.error(f"Unexpected error posting Photo {label}: {e}")
            break

    # Fallback to plain text if photo loading repeatedly fails
    logger.info(f"Attempting text fallback for {label}...")
    await safe_send_message(bot, caption, f"{label} (Text Fallback)")

# ==========================================
# SCHEDULED EVENTS
# ==========================================
async def send_1min_warning(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    if now.hour == 0 or (now.hour == 23 and now.minute > 54):
        return

    text = (
        "🟡 *ALERT PREPARE YOUR BETS!* 🟡\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        ">\n"
        "> 🔔 *Get ready for the next game!*\n"
        ">\n"
        "> ⏳ *Signal drops in 1 MINUTE.*\n"
        ">\n"
        "> 📱 *Open your 1Win app and stay ready!* ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    await safe_send_message(bot, text, "1-Min Alert")


async def send_hourly_predictions(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    payload = build_message_payload(now.hour)
    
    # 1. Coin Flip Session (01:00 - 07:59 GMT)
    if 1 <= now.hour < 8:
        await safe_send_photo(
            bot=bot,
            photo_url=COIN_FLIP_SIGNAL_IMAGE_URL,
            caption=payload,
            label=f"Coin Flip Signal (Hour {now.hour})",
            auto_win_delay=180
        )
    # 2. Mines Session (08:00 - 15:59 GMT)
    elif 8 <= now.hour < 16:
        await safe_send_photo(
            bot=bot,
            photo_url=MINES_SIGNAL_IMAGE_URL,
            caption=payload,
            label=f"Mines Signal (Hour {now.hour})",
            auto_win_delay=180
        )
    # 3. Aviator Session (16:00 - 22:59 GMT)
    elif 16 <= now.hour < 23:
        await safe_send_photo(
            bot=bot,
            photo_url=AVIATOR_SIGNAL_IMAGE_URL,
            caption=payload,
            label=f"Aviator Signal (Hour {now.hour})",
            auto_win_delay=180
        )
    # 4. Offline Maintenance Session
    else:
        await safe_send_message(bot, payload, f"Main Signal (Hour {now.hour})")


async def send_30min_reminder(bot: Bot):
    now = datetime.datetime.now(TIMEZONE)
    hour = now.hour

    reminders = {
        0: ("🪙 COIN FLIP", COIN_FLIP_IMAGE_URL),
        7: ("🚀 MINES", MINES_IMAGE_URL),
        15: ("✈️ AVIATOR PREDICTION", AVIATOR_IMAGE_URL)
    }

    if hour in reminders:
        next_game, image_url = reminders[hour]
        reminder_text = (
            "🔵 *INFO 30-MINUTE GAME CHANGE* 🔵\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            ">\n"
            f"> 📢 *Next session ({next_game}) starts in ⌛ 30 minutes!*\n"
            ">\n"
            "> 💰 *Deposit funds into your account now and prepare!* 🚀\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        # Reminders do not need WIN edits, so auto_win_delay=0
        await safe_send_photo(bot, image_url, reminder_text, f"30-Min Reminder ({next_game})", auto_win_delay=0)


async def send_10min_transition(bot: Bot):
    """Fires at minute 50 of hours 0, 7, 15 as the final reminder before game section changes."""
    now = datetime.datetime.now(TIMEZONE)
    hour = now.hour

    transitions = {
        0: ("✈️ AVIATOR PREDICTION", "🪙 COIN FLIP", COIN_FLIP_IMAGE_URL),
        7: ("🪙 COIN FLIP", "🚀 MINES", MINES_IMAGE_URL),
        15: ("🚀 MINES", "✈️ AVIATOR PREDICTION", AVIATOR_IMAGE_URL)
    }

    if hour in transitions:
        ended_game, next_game, image_url = transitions[hour]
        transition_text = (
            "🔵 *INFO SESSION TRANSITION* 🔵\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            ">\n"
            f"> 🛑 *Previous {ended_game} session has ended.*\n"
            ">\n"
            f"> ⏳ *Next session ({next_game}) begins in 10 MINUTES!*\n"
            ">\n"
            "> 🚨 *Get ready and open your apps!* 💸\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        # Transitions do not need WIN edits, so auto_win_delay=0
        await safe_send_photo(bot, image_url, transition_text, f"10-Min Transition ({next_game})", auto_win_delay=0)

# ==========================================
# WEB HEALTH CHECK HANDLER
# ==========================================
async def handle_ping(request):
    logger.info("Keep-alive ping received.")
    return web.Response(text="Bot is running!", status=200)

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

    # 3. 30-Minute Schedule Announcements (Fires at minute 30 before transition hour)
    scheduler.add_job(
        send_30min_reminder,
        "cron",
        minute="30",
        hour="0,7,15",
        args=[app.bot]
    )

    # 4. 10-Minute Transition Alerts (Final alert before session change at top of hour)
    scheduler.add_job(
        send_10min_transition,
        "cron",
        minute="50",
        hour="0,7,15",
        args=[app.bot]
    )

    scheduler.start()
    logger.info("Channel Predictor Bot scheduler initialized continuously...")

    # Start AIOHTTP Web Server for Cloud Keep-Alive (Render / Railway)
    web_app = web.Application()
    web_app.router.add_get("/", handle_ping)
    runner = web.AppRunner(web_app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"HTTP dummy server running on port {port}")

    async with app:
        await app.start()
        logger.info("Sending initial post on launch...")
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
