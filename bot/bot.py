# flake8: noqa
import asyncio
import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from config import (
    BOT_TOKEN, LOG_LEVEL, LOG_DIR, BOT_MODE, 
    WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_SECRET
)
from middlewares.auth import AuthMiddleware
from middlewares.i18n import i18n_middleware
from routers import user, admin, super_admin
from services.api import api_client
from webhook import setup_webhook, remove_webhook, create_webhook_app

# Logging sozlash (production-ready)
def setup_logging():
    """Setup proper logging with file rotation"""
    # Create logs directory
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(exist_ok=True)
    
    # Log file path
    log_file = log_dir / 'bot.log'
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # File handler with rotation (10MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Suppress noisy loggers
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Bot va Dispatcher yaratish
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def setup_bot():
    """Bot sozlash"""
    # Middleware-larni ro'yxatdan o'tkazish
    # 1. AuthMiddleware birinchi (user ma'lumotlarini olish uchun)
    # 2. i18n middleware ikkinchi (user language'ga qarab)
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.message.middleware(i18n_middleware)
    dp.callback_query.middleware(i18n_middleware)
    
    # Router-larni ro'yxatdan o'tkazish
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(super_admin.router)
    
    logger.info("Bot sozlandi va tayyor!")


async def on_startup():
    """Startup tasks"""
    logger.info("Bot startup tasks...")
    await setup_bot()
    
    # API client session initialization
    await api_client._get_session()
    logger.info("API client session initialized")
    
    if BOT_MODE == 'webhook' and WEBHOOK_URL:
        # Setup webhook
        success = await setup_webhook(bot, WEBHOOK_URL, WEBHOOK_SECRET)
        if not success:
            logger.error("Failed to setup webhook, exiting...")
            raise RuntimeError("Webhook setup failed")
        logger.info("Webhook mode enabled")
    else:
        logger.info("Polling mode enabled (for development)")


async def on_shutdown():
    """Shutdown tasks"""
    logger.info("Bot shutdown tasks...")
    
    # Close API client session
    await api_client.close()
    
    # Remove webhook if in webhook mode
    if BOT_MODE == 'webhook':
        await remove_webhook(bot)
    
    # Close bot session
    await bot.session.close()
    logger.info("Bot shutdown complete")


async def run_polling():
    """Run bot in polling mode (development)"""
    try:
        await on_startup()
        logger.info("Bot polling started...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Bot polling error: {e}", exc_info=True)
    finally:
        await on_shutdown()


async def run_webhook():
    """Run bot in webhook mode (production)"""
    if not WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL must be set for webhook mode")
    
    try:
        await on_startup()
        
        # Create webhook app
        app = create_webhook_app(bot, dp)
        
        # Get webhook port from environment or default
        webhook_port = int(os.getenv('WEBHOOK_PORT', '8443'))
        webhook_host = os.getenv('WEBHOOK_HOST_BIND', '0.0.0.0')
        
        logger.info(f"Starting webhook server on {webhook_host}:{webhook_port}")
        
        # Run webhook server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, webhook_host, webhook_port)
        await site.start()
        
        logger.info(f"Webhook server started on port {webhook_port}")
        logger.info(f"Webhook URL: {WEBHOOK_URL}")
        
        # Keep running
        try:
            await asyncio.Event().wait()  # Wait forever
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await runner.cleanup()
            await on_shutdown()
            
    except Exception as e:
        logger.error(f"Webhook server error: {e}", exc_info=True)
        await on_shutdown()
        raise


async def main():
    """Asosiy funksiya"""
    try:
        if BOT_MODE == 'webhook':
            await run_webhook()
        else:
            await run_polling()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
