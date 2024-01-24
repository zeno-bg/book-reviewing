from odmantic import AIOEngine

from repositories.users import UsersRepository
from repositories.authors import AuthorsRepository
from repositories.books import BooksRepository
from services.users import UsersService
from services.authors import AuthorsService
from services.books import BooksService

mongo_engine = AIOEngine()

users_service = UsersService(UsersRepository(mongo_engine))
authors_service = AuthorsService(AuthorsRepository(mongo_engine))
books_service = BooksService(BooksRepository(mongo_engine), authors_service)
authors_service.books_service = books_service


def get_users_service() -> UsersService:
    return users_service


def get_authors_service() -> AuthorsService:
    return authors_service


def get_books_service() -> BooksService:
    return books_service
