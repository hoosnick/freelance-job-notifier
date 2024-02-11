import asyncio
import random
import re

import aiohttp
import feedparser
from aiogram import Bot, html
from selectolax.lexbor import LexborHTMLParser as htmlp

from app.bot.keyboards import apply_button
from app.config_reader import Settings
from app.db.tables import FreelancePlatform, Project
from kwork import Kwork

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


async def get_upwork_jobs(bot: Bot, config: Settings):
    url = "https://www.upwork.com/ab/feed/jobs/rss"
    params = {
        "q": config.up_question,
        "subcategory2_uid": config.up_subcategories,
        "sort": "recency",
        "paging": "0;50",
        "api_params": "1",
        "securityToken": config.up_securitytoken,
        "userUid": config.up_useruid,
        "orgUid": config.up_orguid
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
            project = await Project.objects().get_or_create(
                Project.url == feed.link, {Project.title: feed.title}
            )

            if not project._was_created:
                continue

            data = parse_metadata(
                htmlp(feed.description).text(separator='', strip=False)
            )

            project.description = data['desc']
            project.freelance_platform = FreelancePlatform.UPWORK
            await project.save()

            text = TEMPLATES.get('UPWORK').format(
                title=html.quote(feed.title),
                description=html.quote(data['desc'][:3000]),
                budget=data['budget'],
                hourly_range=data['hourly_range'],
                category=data['category'],
                country=data['country'],
            )

            btn_data = {
                'url': config.app_base_url,
                'id': project.id,
                'lang': 'en',
                'username': config.bot_username
            }

            await bot.send_message(
                chat_id=config.tg_group, text=text,
                message_thread_id=config.tg_topic_id,
                reply_markup=apply_button(
                    text="Click to apply",
                    url=feed.link,
                    data=btn_data,
                    in_group=True
                )
            )

            await asyncio.sleep(random.choice([1, 2, 3]))


async def get_kwork_projects(bot: Bot, config: Settings):
    kwork = Kwork(
        login=config.kw_login,
        password=config.kw_password,
        phone_last=config.kw_phone_last
    )
    token = await kwork.token

    categories_ids = config.kw_categories

    raw_projects = await kwork.api_request(
        method="post",
        api_method="projects",
        categories=categories_ids,
        page=1, token=token
    )

    success = raw_projects["success"]
    if not success:
        return await kwork.close()

    def get_project_data(response: list) -> list:
        result = []
        for item in response:
            result.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "description": item.get("description"),
                "price": item.get("price"),
                "possible_price_limit": item.get("possible_price_limit")
            })
        return result

    projects = get_project_data(raw_projects["response"])

    paging = raw_projects["paging"]
    pages = int((paging["pages"] + 1) / 2)

    for page in range(2, pages):
        other_projects = await kwork.api_request(
            method="post", api_method="projects",
            categories=categories_ids,
            page=page, token=token
        )

        projects.extend(get_project_data(other_projects["response"]))

    for project in projects:
        url = "https://kwork.ru/projects/" + str(project.get("id"))

        kw_project = await Project.objects().get_or_create(
            Project.url == url, {Project.title: project.get("title")}
        )

        if not kw_project._was_created:
            continue

        desc = htmlp(project.get("description")).text(separator='\n', strip=True)

        kw_project.description = desc
        kw_project.freelance_platform = FreelancePlatform.KWORK
        await kw_project.save()

        text = TEMPLATES.get('KWORK').format(
            html.quote(project.get("title")), html.quote(desc[:3000]),
            project.get("price"), project.get("possible_price_limit")
        )

        btn_data = {
            'url': config.app_base_url,
            'id': kw_project.id,
            'lang': 'ru',
            'username': config.bot_username
        }

        await bot.send_message(
            chat_id=config.tg_group, text=text,
            message_thread_id=config.tg_topic_id,
            reply_markup=apply_button(
                text="Предложить услугу", url=url,
                data=btn_data, in_group=True
            )
        )

        await asyncio.sleep(random.choice([1, 2, 3]))

    await kwork.close()
