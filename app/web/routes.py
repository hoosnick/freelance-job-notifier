from pathlib import Path

from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from app.db.tables import Offer, PremiumUser, Project
from app.gpt import generate_offer


async def home(request: Request):
    return FileResponse(Path(__file__).parent.resolve() / "offers.html")


async def create_offer(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(
            token=bot.token,
            init_data=data["_auth"]
        )
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized :("})

    parsed_user = await parse_user(web_app_init_data.user.id)

    if parsed_user is None:
        return json_response({"ok": False, "err": "You're not a Premium user :("})

    project_id = request.rel_url.query.get('for')
    lang = request.rel_url.query.get('lang')

    project = await Project.objects().get(Project.id == int(project_id))
    if project is None:
        return json_response({"ok": False, "err": "Project not found!"})

    if lang not in ['en', 'ru']:
        return json_response({"ok": False, "err": "This language is not supported!"})

    result = await generate_offer(project.title + "\n" + project.description, lang)
    if not result['ok']:
        return json_response(result)

    new_offer = Offer(
        project=project,
        offer=result.get('response'),
        offer_by=parsed_user
    )
    await new_offer.save()

    result['offer_by'] = parsed_user.name

    return json_response(result)


async def get_offers(request: Request):
    project_id = request.rel_url.query.get('for')

    project = await Project.objects().get(Project.id == int(project_id))
    if project is None:
        return json_response({"ok": False, "err": "Project not found!"})

    offers = (
        await Offer.select(
            Offer.offer_by.name.as_alias('offer_by'),
            *Offer.all_columns([Offer.id, Offer.project, Offer.offer_by])
        ).where(
            Offer.project == project
        ))

    return json_response(
        {
            "ok": True,
            "project": {
                "url": project.url,
                "title": project.title,
                "description": project.description,
                "freelance_platform": project.freelance_platform,
            },
            'offers': offers
        }
    )


async def parse_user(telegram_id: int):
    return (
        await PremiumUser
        .objects()
        .get(PremiumUser.tg_id == telegram_id)
    )
