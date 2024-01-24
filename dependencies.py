from odmantic import AIOEngine

from repositories.users import UsersRepository
from repositories.authors import AuthorsRepository
from services.users import UsersService
from services.authors import AuthorsService

mongo_engine = AIOEngine()

users_service = UsersService(UsersRepository(mongo_engine))
authors_service = AuthorsService(AuthorsRepository(mongo_engine))


def get_users_service() -> UsersService:
    return users_service


def get_authors_service() -> AuthorsService:
    return authors_service
