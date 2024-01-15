import os

from piccolo.conf.apps import AppRegistry
from piccolo.engine.sqlite import SQLiteEngine

from pydantic_settings import BaseSettings

os.environ['PICCOLO_CONF'] = 'app.config_reader'


class Settings(BaseSettings):
    piccolo_conf: str = 'app.config_reader'

    kw_login: str
    kw_password: str
    kw_phone_last: str
    kw_categories: str

    up_securitytoken: str
    up_useruid: str
    up_orguid: str
    up_question: str
    up_subcategories: str

    tg_token: str
    tg_group: int
    tg_group_link: str
    tg_topic_id: int
    tg_admin: int
    bot_username: str | None = None

    app_base_url: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


DB = SQLiteEngine('projects.db')

APP_REGISTRY = AppRegistry(apps=['app.db.piccolo_app'])
