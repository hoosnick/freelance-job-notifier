import asyncio
import json
import logging
import os
import random

import aiosqlite

from aiohttp import ClientSession as CS

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dotenv import load_dotenv

from selectolax.lexbor import LexborHTMLParser as htmlp

from kwork import Kwork
from kwork.types import Project

load_dotenv()  # take environment variables from .env

logging.basicConfig(level=logging.INFO)

scheduler = AsyncIOScheduler()

TG_ENDPOINT = 'https://api.telegram.org/bot' + os.getenv("TG_TOKEN")

TEMPLATE = '💸 <b>{}</b>\n\n' \
           '<i>{}</i>\n\n' \
           'Желаемый бюджет: <code>{:,} ₽</code>\n' \
           'Допустимый: до <code>{:,} ₽</code>'


async def add_project_if_not_exists(project_id: int) -> bool:
    q_select = "SELECT EXISTS(SELECT 1 FROM projects WHERE project_id = ?)"
    q_insert = "INSERT INTO projects (project_id) VALUES (?)"

    async with aiosqlite.connect(database='projects.db') as db:
        async with db.execute(q_select, (project_id,)) as cursor:
            exists = await cursor.fetchone()

        if not exists[0]:
            await db.execute(q_insert, (project_id,))
            await db.commit()

    return exists[0]


async def send_project(session: CS, project: Project) -> None:
    was_created = await add_project_if_not_exists(project.id)
    if was_created: return

    description = htmlp(project.description).text(separator='\n', strip=True)
    short_description = description[:3000]

    data = {
        'chat_id': int(os.getenv("TG_GROUP")),
        'message_thread_id': int(os.getenv("TG_TOPIC_ID")),
        'text': TEMPLATE.format(
            project.title, short_description,
            project.price, project.possible_price_limit
        ),
        'disable_web_page_preview': True,
        'parse_mode': 'HTML'
    }
    data["reply_markup"] = json.dumps({
        "inline_keyboard": [[{
            "text": "Предложить услугу",
            "url": "https://kwork.ru/projects/" + str(project.id)
        }]]}
    )
    await session.post(TG_ENDPOINT + '/sendMessage', data=data)


@scheduler.scheduled_job('interval', minutes=10)
async def get_projects():
    kwork = Kwork(
        login=os.getenv('LOGIN'),
        password=os.getenv('PASSWORD'),
        phone_last=os.getenv('PHONE_LAST')
    )
    token = await kwork.token

    categories = [38, 255, 41, 37, 81, 113]
    categories_ids = ",".join(str(category) for category in categories)

    raw_projects = await kwork.api_request(
        method="post",
        api_method="projects",
        categories=categories_ids,
        page=1, token=token
    )

    success = raw_projects["success"]
    if not success:
        return await kwork.close()

    # first page projects
    projects = [Project(**pr) for pr in raw_projects["response"]]

    paging = raw_projects["paging"]
    pages = int((paging["pages"] + 1) / 2)

    for page in range(2, pages):
        other_projects = await kwork.api_request(
            method="post", api_method="projects",
            categories=categories_ids,
            page=page, token=token
        )

        for dict_project in other_projects["response"]:
            projects.append(Project(**dict_project))

    for project in projects:
        await send_project(kwork.session, project)
        await asyncio.sleep(random.choice([1, 2, 3]))

    await kwork.close()


if __name__ == '__main__':
    scheduler.start()
    asyncio.get_event_loop().run_forever()
