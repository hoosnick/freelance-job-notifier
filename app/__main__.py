import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import (SimpleRequestHandler,
                                            setup_application)
from aiohttp.web import run_app
from aiohttp.web_app import Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from piccolo.engine import engine_finder

from app.bot.handlers import router
from app.bot.middlewares import RetryRequestMiddleware
from app.config_reader import Settings
from app.db.tables import PROJECT_TABLES
from app.parser import get_kwork_projects, get_upwork_jobs
from app.web.routes import create_offer, get_offers, home


async def database_connection(config: Settings,  close=False, persist=True) -> None:
    db = engine_finder(config.piccolo_conf)

    if db.engine_type == 'sqlite':
        if close:
            return

        if not persist:
            for table in reversed(PROJECT_TABLES):
                await table.alter().drop_table(if_exists=True)

        for table in PROJECT_TABLES:
            await table.create_table(if_not_exists=True)
    else:
        if close:
            return await db.close_connection_pool()

        await db.start_connection_pool()


async def on_startup(bot: Bot, base_url: str, scheduler: AsyncIOScheduler, config: Settings):
    await bot.me()

    config.bot_username = bot._me.username
    print(config.bot_username)

    await database_connection(config, persist=True)

    await bot.set_webhook(f"{base_url}/webhook")

    scheduler.add_job(
        get_upwork_jobs, 'interval', minutes=15,
        kwargs={'bot': bot, 'config': config}
    )
    # scheduler.add_job(
    #     get_kwork_projects, 'interval', minutes=10,
    #     kwargs={'bot': bot, 'config': config}
    # )
    scheduler.start()


async def on_shutdown(bot: Bot, config: Settings, scheduler: AsyncIOScheduler):
    await database_connection(config, close=True)

    await bot.delete_webhook(drop_pending_updates=True)

    scheduler.shutdown(wait=False)


def create_bot(config: Settings) -> Bot:
    session: AiohttpSession = AiohttpSession()
    session.middleware(RetryRequestMiddleware())

    return Bot(
        token=config.tg_token,
        parse_mode=ParseMode.HTML,
        session=session,
        disable_web_page_preview=True
    )


def main():
    config = Settings()

    bot = create_bot(config)

    dp = Dispatcher()
    dp["base_url"] = config.app_base_url
    dp["config"] = config

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(router)

    scheduler = AsyncIOScheduler()
    dp['scheduler'] = scheduler

    app = Application()
    app["bot"] = bot

    app.router.add_get("/", home)
    app.router.add_post("/generate", create_offer)
    app.router.add_get("/offers", get_offers)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    run_app(app, host="127.0.0.1", port=8081)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
