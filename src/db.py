import argparse
import os

from dotenv import load_dotenv
from passlib.context import CryptContext
from tortoise.models import Model
from tortoise import Tortoise, fields, run_async

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
load_dotenv()


class UserExists(Exception):
    pass


def get_password_hash(password):
    return pwd_context.hash(password)


class User(Model):
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    added = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.username


async def init(db_url=None):
    """Initializes database"""
    if db_url is None:
        db_url = os.getenv("DATABASE_URL")
        if db_url is None:
            raise RuntimeError("Please specify a DB")

    await Tortoise.init(
        db_url=db_url,
        modules={'models': ['__main__']}
    )
    await Tortoise.generate_schemas()


async def create_user(username, password):
    """Creates user encrypting password, raises exception
       if user already exists"""
    user = await User.get_or_none(
        username=username)
    if user is None:
        encrypted_pw = get_password_hash(password)
        user = await User.create(
            username=username,
            password=encrypted_pw)
        return user
    else:
        raise UserExists(f"Username {username} already exists")


async def main(args):
    await init()
    await create_user(args.username, args.password)
    print(f"{args.username} created")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Create a user")
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    args = parser.parse_args()
    run_async(main(args))
