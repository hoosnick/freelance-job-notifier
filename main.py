import asyncio
import json
import logging
import os
import random
import re

import aiohttp

import aiosqlite

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dotenv import load_dotenv

import feedparser

from selectolax.lexbor import LexborHTMLParser as htmlp

from kwork import Kwork
from kwork.types import Project

load_dotenv()  # take environment variables from .env

logging.basicConfig(level=logging.INFO)

scheduler = AsyncIOScheduler()


TEMPLATES = {
    'KWORK': '💸 <b>{}</b>\n\n'
             '<i>{}</i>\n\n'
             'Желаемый бюджет: <code>{:,} ₽</code>\n'
             'Допустимый: до <code>{:,} ₽</code>',

    'UPWORK': "☘️ <b>{title}</b>\n\n"
              "<i>{description}</i>\n\n"
              "Budget: <code>{budget}</code>\n"
              "Hourly Range: {hourly_range}\n"
              "Category: {category}\n"
              "Country: {country}"
}


async def create_tables() -> None:
    db = await aiosqlite.connect(database='projects.db')
    await db.execute('CREATE TABLE IF NOT EXISTS "up_jobs" ("job_id" TEXT)')
    await db.execute('CREATE TABLE IF NOT EXISTS "kw_projects" ("project_id" INTEGER NOT NULL)')
    await db.commit()
    await db.close()

    print('[INFO] Tables are ready...')


async def check_existence(data: dict) -> bool:
    q_select = "SELECT EXISTS(SELECT 1 FROM {table} WHERE {field} = ?)"
    q_insert = "INSERT INTO {table} ({field}) VALUES (?)"

    async with aiosqlite.connect(database='projects.db') as db:
        async with db.execute(
            q_select.format(table=data['table'], field=data['field']),
            (data['id'],)
        ) as cursor:
            exists = await cursor.fetchone()

        if not exists[0]:  # add to database
            await db.execute(
                q_insert.format(table=data['table'], field=data['field']),
                (data['id'],)
            )
            await db.commit()

    return exists[0]


async def send_project(session: aiohttp.ClientSession, data: dict) -> None:
    data['chat_id'] = int(os.getenv("TG_GROUP"))
    data['message_thread_id'] = int(os.getenv("TG_TOPIC_ID"))
    data['disable_web_page_preview'] = True
    data['parse_mode'] = 'HTML'

    TG_ENDPOINT = 'https://api.telegram.org/bot' + os.getenv("TG_TOKEN")

    await session.post(TG_ENDPOINT + '/sendMessage', data=data)


@scheduler.scheduled_job('interval', minutes=15)
async def get_upwork_jobs():
    url = "https://www.upwork.com/ab/feed/jobs/rss"
    params = {
        "q": os.getenv("UP_QUESTION"),
        "subcategory2_uid": os.getenv("UP_SUBCATEGORIES"),
        "sort": "recency",
        "paging": "0;50",
        "api_params": "1",
        "securityToken": os.getenv("UP_SECURITYTOKEN"),
        "userUid": os.getenv("UP_USERUID"),
        "orgUid": os.getenv("UP_ORGUID")
    }

    def parse_metadata(html: str) -> dict:
        parsed_data = {}

        patterns = {
            'hourly_range': r'Hourly Range:(.*?)(?:Posted On:|$)',
            'budget': r'Budget:(.*?)(?:Posted On:|$)',
            'posted': r'Posted On:(.*?)(?:Category:|$)',
            'category': r'Category:(.*?)(?:Skills:|$)',
            'skills': r'Skills:(.*?)(?:Country:|$)',
            'country': r'Country:(.*?)(?:click|$)'
        }

        # Find the earliest occurring metadata pattern
        earliest_position = len(html)
        for pattern in patterns.values():
            match = re.search(pattern, html, re.DOTALL)
            if match and match.start() < earliest_position:
                earliest_position = match.start()

        # Extract description based on the earliest pattern
        parsed_data['desc'] = html[:earliest_position].strip()

        # Extract other metadata
        for key, pattern in patterns.items():
            match = re.search(pattern, html, re.DOTALL)
            parsed_data[key] = match.group(1).strip() if match else None

        return parsed_data

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                return

            content = await response.text()

        feeds = feedparser.parse(content)
        for feed in feeds.entries:
            already_exist = await check_existence(
                data={'table': 'up_jobs', 'field': 'job_id', 'id': feed.link}
            )
            if already_exist:
                continue

            data = parse_metadata(
                htmlp(feed.description).text(separator='', strip=False)
            )

            tg_data = {
                'text': TEMPLATES.get('UPWORK').format(
                    title=feed.title,
                    description=data['desc'][:3000],
                    budget=data['budget'],
                    hourly_range=data['hourly_range'],
                    category=data['category'],
                    country=data['country'],
                ),
                'reply_markup': json.dumps({
                    "inline_keyboard": [[{
                        "text": "Click to apply",
                        "url": feed.link
                    }]]}
                )
            }

            await send_project(session, tg_data)
            await asyncio.sleep(random.choice([1, 2, 3]))


@scheduler.scheduled_job('interval', minutes=10)
async def get_kwork_projects():
    kwork = Kwork(
        login=os.getenv('KW_LOGIN'),
        password=os.getenv('KW_PASSWORD'),
        phone_last=os.getenv('KW_PHONE_LAST')
    )
    token = await kwork.token

    categories_ids = os.getenv('KW_CATEGORIES')

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
        already_exist = await check_existence(
            {'table': 'kw_projects', 'field': 'project_id', 'id': project.id}
        )
        if already_exist:
            continue

        desc = htmlp(project.description).text(separator='\n', strip=True)

        tg_data = {
            'text': TEMPLATES.get('KWORK').format(
                project.title, desc[:3000],
                project.price, project.possible_price_limit
            ),
            'reply_markup': json.dumps({
                "inline_keyboard": [[{
                    "text": "Предложить услугу",
                    "url": "https://kwork.ru/projects/" + str(project.id)
                }]]}
            )
        }

        await send_project(kwork.session, tg_data)
        await asyncio.sleep(random.choice([1, 2, 3]))

    await kwork.close()


if __name__ == '__main__':
    scheduler.start()
    loop = asyncio.get_event_loop()
    loop.create_task(create_tables())
    loop.run_forever()
