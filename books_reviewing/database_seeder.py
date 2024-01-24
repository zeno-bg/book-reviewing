import datetime
import os

from motor.motor_asyncio import AsyncIOMotorClient

from books_reviewing.services.users import UsersService
from books_reviewing.services.authors import AuthorsService
from books_reviewing.services.books import BooksService
from books_reviewing.services.reviews import ReviewsService
from schemas.authors import BaseAuthorSchema
from schemas.books import BaseBookSchema
from schemas.reviews import BaseReviewSchema
from schemas.users import BaseUserSchema


class DatabaseSeeder:
    users_service: UsersService
    authors_service: AuthorsService
    books_service: BooksService
    reviews_service: ReviewsService
    motor_client: AsyncIOMotorClient

    def __init__(
        self,
        users_service: UsersService,
        authors_service: AuthorsService,
        books_service: BooksService,
        reviews_service: ReviewsService,
        mongo_client: AsyncIOMotorClient,
    ):
        self.users_service = users_service
        self.authors_service = authors_service
        self.books_service = books_service
        self.reviews_service = reviews_service
        self.motor_client = mongo_client

    async def seed_database(self):
        users = {
            "john": BaseUserSchema(
                name="John Doe",
                email="john@doe.com",
                birthday=datetime.datetime.now(),
                phone="+389234323243",
            ),
            "jack": BaseUserSchema(
                name="Jack Doe",
                email="jack@doe.com",
                birthday=datetime.datetime.now(),
                phone="+389234223243",
            ),
            "jane": BaseUserSchema(
                name="Jane Doe",
                email="jane@doe.com",
                birthday=datetime.datetime.now(),
                phone="+389235323243",
            ),
            "jill": BaseUserSchema(
                name="Jill Doe",
                email="jill@doe.com",
                birthday=datetime.datetime.now(),
                phone="+389232323243",
            ),
            "jess": BaseUserSchema(
                name="Jess Doe",
                email="jess@doe.com",
                birthday=datetime.datetime.now(),
                phone="+389231323243",
            ),
        }
        for key, value in users.items():
            users[key] = await self.users_service.create(value)

        authors = {
            "pepa": BaseAuthorSchema(name="PEPAA", bio="She is the best"),
            "ceca": BaseAuthorSchema(name="CECAAA", bio="She is the second best"),
            "meca": BaseAuthorSchema(name="MECA", bio="She ........"),
        }

        for key, value in authors.items():
            authors[key] = await self.authors_service.create(value)

        books = {
            "pepa_pig_1": BaseBookSchema(
                isbn="1111111111",
                title="Pepa Pig 1",
                description="The Realest BlockBluster Ever!!!",
                publication_date=datetime.datetime.now(),
                author_id=authors["pepa"].id,
            ),
            "pepa_pig_2": BaseBookSchema(
                isbn="1111111121",
                title="Pepa Pig 2",
                description="The Realest BlockBluster Ever!!!",
                publication_date=datetime.datetime.now(),
                author_id=authors["pepa"].id,
            ),
            "pepa_pig_3": BaseBookSchema(
                isbn="111111113331",
                title="Pepa Pig 3",
                description="The Realest BlockBluster Ever!!!",
                publication_date=datetime.datetime.now(),
                author_id=authors["pepa"].id,
            ),
            "ceca_1": BaseBookSchema(
                isbn="111111113334",
                title="Ceca is trying",
                description="Ceca is trying to come back .........",
                publication_date=datetime.datetime.now(),
                author_id=authors["ceca"].id,
            ),
        }

        for key, value in books.items():
            books[key] = await self.books_service.create(value)

        reviews = [
            BaseReviewSchema(
                rating=1,
                comment="JQWEKLRJ QWEKLRJ QKLWEJLKQW",
                book_id=books["pepa_pig_1"].id,
                user_id=users["john"].id,
            ),
            BaseReviewSchema(
                rating=4,
                comment="JQWEKLRJ QWoajwerio ajwero iEKLRJ QKLWEJLKQW",
                book_id=books["pepa_pig_1"].id,
                user_id=users["jane"].id,
            ),
            BaseReviewSchema(
                rating=5,
                comment="JQWEKLRJ QWEKLRJ asdjvolasid fQKLWEJLKQW",
                book_id=books["pepa_pig_1"].id,
                user_id=users["jill"].id,
            ),
            BaseReviewSchema(
                rating=2,
                comment="JQWEKLRJ QWEKLRJ QKLWEJLKQW",
                book_id=books["pepa_pig_2"].id,
                user_id=users["john"].id,
            ),
            BaseReviewSchema(
                rating=1,
                comment="JQWEKLRJ QWEKLRJ QKLWEJLKQW",
                book_id=books["pepa_pig_3"].id,
                user_id=users["jill"].id,
            ),
            BaseReviewSchema(
                rating=3,
                comment="JQWEKLRJ QWEKLRJ QKLWEJLKQW",
                book_id=books["pepa_pig_2"].id,
                user_id=users["jane"].id,
            ),
            BaseReviewSchema(
                rating=4,
                comment="JQWEKLRJ QWEKLRJ QKLWEJLKQW",
                book_id=books["pepa_pig_3"].id,
                user_id=users["john"].id,
            ),
            BaseReviewSchema(
                rating=2,
                comment="JQWEKLRJ QWEKLRJ QKLWEJLKQW",
                book_id=books["ceca_1"].id,
                user_id=users["john"].id,
            ),
            BaseReviewSchema(
                rating=4,
                comment="JQWEKLRJ QWEKLRJ QKLWEJLKQW",
                book_id=books["pepa_pig_3"].id,
                user_id=users["john"].id,
            ),
        ]

    async def clear_database(self):
        db = self.motor_client[os.getenv("MONGO_DB", "book_reviews")]
        db.drop_collection("users")
        db.drop_collection("authors")
        db.drop_collection("books")
        db.drop_collection("reviews")
