from datetime import datetime

from odmantic import Model, Reference, ObjectId


class Author(Model):
    name: str
    bio: str

    model_config = {
        "collection": "authors"
    }


class Book(Model):
    isbn: str
    title: str
    description: str
    publication_date: datetime
    author_id: ObjectId

    model_config = {
        "collection": "books"
    }


class User(Model):
    name: str
    birthday: datetime
    email: str
    phone: str

    model_config = {
        "collection": "users"
    }


class Review(Model):
    rating: int
    comment: str
    user_id: User = Reference()
    book_id: Book = Reference()

    model_config = {
        "collection": "reviews"
    }
