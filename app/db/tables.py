import random
import string
from enum import Enum
from typing import List

from piccolo.columns import BigInt, ForeignKey, Text, Varchar
from piccolo.columns.readable import Readable
from piccolo.table import Table

from app.config_reader import DB


def generate_promo_code(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))


class FreelancePlatform(str, Enum):
    KWORK = 'kwork'
    UPWORK = 'upwork'


class Project(Table, db=DB):
    url = Varchar(length=1024, required=True)
    title = Varchar(required=True)
    description = Text(required=True)
    freelance_platform = Varchar(choices=FreelancePlatform, required=True)


class PremiumUser(Table, db=DB):
    tg_id = BigInt(default=0)
    name = Varchar()
    invite_link = Varchar(default=generate_promo_code)

    @classmethod
    def get_readable(cls):
        return Readable("%s [%s]", [cls.name, cls.tg_id])


class Offer(Table, db=DB):
    project = ForeignKey(Project)
    offer = Text()
    offer_by = ForeignKey(PremiumUser)


PROJECT_TABLES: List[Table] = [Project, Offer, PremiumUser]
