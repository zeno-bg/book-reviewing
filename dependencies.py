from odmantic import AIOEngine

from repositories.users import UsersRepository
from services.users import UsersService

mongo_engine = AIOEngine()

users_service = UsersService(UsersRepository(mongo_engine))


def get_mongo_engine() -> AIOEngine:
    return mongo_engine


def get_users_service() -> UsersService:
    return users_service
