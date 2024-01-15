import re

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from app.bot.keyboards import apply_button
from app.config_reader import Settings
from app.db.tables import FreelancePlatform, PremiumUser, Project

router = Router()


@router.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'project_(\d+)'))
))
async def about_project(m: Message, command: CommandObject, config: Settings):
    try:
        project_id = int(command.args.split('_')[-1])
    except ValueError as v:
        return await m.answer(str(v))

    project = await Project.objects().get(Project.id == project_id)
    if project is None:
        return await m.answer("Project not found!")

    lang = 'ru' if project.freelance_platform == FreelancePlatform.KWORK else 'en'
    apply_btn = 'Предложить услугу' if lang == 'ru' else 'Click to apply'
    project_desc = f"<b>{project.title}</b>\n\n<i>{project.description}</i>"

    await m.answer(
        text=project_desc,
        reply_markup=apply_button(
            apply_btn, project.url,
            {
                'url': config.app_base_url,
                'id': project.id,
                'lang': lang,
                'group_link': config.tg_group_link
            }
        )
    )


@router.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'INVITE_([A-Z0-9]{6})'))
))
async def new_premium_user(m: Message, command: CommandObject):
    if await PremiumUser.exists().where(PremiumUser.tg_id == m.from_user.id):
        return m.answer('You are already a Premium user :)')

    invite_link = command.args.split('_')[-1]
    pro_user = await PremiumUser.objects() \
        .get(PremiumUser.invite_link == invite_link)

    if pro_user is None:
        return m.answer('No such invite link available :(')
    if pro_user.tg_id != 0:
        return m.answer('This invite link is already used :(')

    pro_user.tg_id = m.from_user.id
    pro_user.name = m.from_user.full_name

    await pro_user.save()

    await m.answer('You are now a Premium user! Enjoy :)')


@router.message(CommandStart())
async def command_start(m: Message):
    await m.answer("Hi!")


@router.message(Command("promo"))
async def generate_promo(m: Message, config: Settings):
    if m.from_user.id != config.tg_admin:
        return

    new_promo = PremiumUser()
    await new_promo.save()

    invite_code = f'INVITE_{new_promo.invite_link}'

    return m.answer(f'<code>https://t.me/{config.bot_username}?start={invite_code}</code>')
