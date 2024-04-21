import os

from dotenv import load_dotenv
from piccolo.conf.apps import AppRegistry
from piccolo.engine.sqlite import SQLiteEngine
from pydantic_settings import BaseSettings

os.environ["PICCOLO_CONF"] = "app.config_reader"

load_dotenv(override=True)


class Settings(BaseSettings):
    piccolo_conf: str = "app.config_reader"

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
    bot_username: str = "your_bot"

    app_base_url: str
    app_host: str = "localhost"
    app_port: int = 8081

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


db_path = os.path.join("app", "db", "database")
if not os.path.exists(db_path):
    os.makedirs(db_path)

DB = SQLiteEngine("%s\\projects.db" % db_path)

APP_REGISTRY = AppRegistry(apps=["app.db.piccolo_app"])
