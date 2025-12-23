"""
Webhook setup and handling for production deployment
"""
import logging
from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from config import WEBHOOK_PATH, WEBHOOK_SECRET

logger = logging.getLogger(__name__)


async def setup_webhook(bot: Bot, webhook_url: str, secret_token: str = None):
    """Set webhook URL on Telegram servers"""
    try:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=secret_token,
            drop_pending_updates=True  # Clear pending updates
        )
        logger.info(f"Webhook set successfully: {webhook_url}")
        return True
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}", exc_info=True)
        return False


async def remove_webhook(bot: Bot):
    """Remove webhook (switch back to polling)"""
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook removed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to remove webhook: {e}", exc_info=True)
        return False


def create_webhook_app(bot: Bot, dispatcher):
    """Create aiohttp application for webhook"""
    app = web.Application()
    
    # Create webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
        secret_token=WEBHOOK_SECRET if WEBHOOK_SECRET else None
    )
    
    # Register webhook path
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    # Health check endpoint
    async def health_check(request):
        return web.json_response({"status": "ok", "service": "telegram_bot"})
    
    app.router.add_get("/health", health_check)
    
    return app

