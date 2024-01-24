from odmantic import AIOEngine, ObjectId
from odmantic.query import QueryExpression

from books_reviewing.exceptions import database_exception_wrapper
from books_reviewing.models import Review


class ReviewsRepository:
    mongo_engine: AIOEngine

    def __init__(self, mongo_engine: AIOEngine):
        self.mongo_engine = mongo_engine

    @database_exception_wrapper
    async def save(self, review: Review) -> Review:
        return await self.mongo_engine.save(review)

    @database_exception_wrapper
    async def get_one(self, review_id: ObjectId) -> Review | None:
        review: Review = await self.mongo_engine.find_one(
            Review, Review.id == review_id
        )
        return review

    @database_exception_wrapper
    async def get_all(self) -> list[Review]:
        return await self.mongo_engine.find(Review)

    @database_exception_wrapper
    async def delete(self, review: Review):
        await self.mongo_engine.delete(review)

    @database_exception_wrapper
    async def query(
        self,
        sort: str,
        sort_direction: str,
        page: int,
        size: int,
        filters_dict: dict[str, str | ObjectId] = None,
    ) -> (list[Review], int):
        queries = []
        if len(filters_dict) > 0:
            for filter_attribute_name in filters_dict.keys():
                queries.append(
                    QueryExpression(
                        eval("Review." + filter_attribute_name)
                        == filters_dict[filter_attribute_name]
                    )
                )

        items = await self.mongo_engine.find(
            Review,
            *queries,
            sort=eval("Review." + sort + "." + sort_direction + "()"),
            skip=(page - 1) * size,
            limit=size
        )
        total_count = await self.mongo_engine.count(Review, *queries)

        return items, total_count

    @database_exception_wrapper
    async def get_average_rating_for_book(self, book_id: ObjectId) -> float:
        result = (
            await self.mongo_engine.get_collection(Review)
            .aggregate(
                [
                    {"$match": {"book_id": book_id}},
                    {"$group": {"_id": None, "average_rating": {"$avg": "$rating"}}},
                ]
            )
            .to_list(length=None)
        )
        if len(result) == 0:
            return 0
        return result[0]["average_rating"]

    @database_exception_wrapper
    async def delete_reviews_for_book(self, book_id: ObjectId):
        return await self.mongo_engine.remove(Review, Review.book_id == book_id)

    @database_exception_wrapper
    async def delete_reviews_for_books(self, book_ids: list[ObjectId]):
        return await self.mongo_engine.remove(Review, Review.book_id.in_(book_ids))

    @database_exception_wrapper
    async def delete_reviews_by_user(self, user_id: ObjectId):
        return await self.mongo_engine.remove(Review, Review.user_id == user_id)
