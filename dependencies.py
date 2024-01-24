import os

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from repositories.users import UsersRepository
from repositories.authors import AuthorsRepository
from repositories.books import BooksRepository
from repositories.reviews import ReviewsRepository
from services.users import UsersService
from services.authors import AuthorsService
from services.books import BooksService
from services.reviews import ReviewsService

mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
mongo_engine = AIOEngine(
    client=mongo_client, database=os.getenv("MONGO_DB", "books_reviewing")
)

users_service = UsersService(UsersRepository(mongo_engine))
authors_service = AuthorsService(AuthorsRepository(mongo_engine))
books_service = BooksService(BooksRepository(mongo_engine), authors_service)
reviews_service = ReviewsService(
    ReviewsRepository(mongo_engine), books_service, users_service
)

books_service.reviews_service = reviews_service
authors_service.books_service = books_service
users_service.reviews_service = reviews_service


def get_users_service() -> UsersService:
    return users_service


def get_authors_service() -> AuthorsService:
    return authors_service


def get_books_service() -> BooksService:
    return books_service


def get_reviews_service() -> ReviewsService:
    return reviews_service
