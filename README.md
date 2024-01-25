# Book reviewing backend
This is a FastAPI implementation of a simple book reviewing backend.
It uses MongoDB as a database with Odmantic as an ODM.

It allows for CRUD operations with the relevant data (users, authors, books, reviews) and supports the relationships between the models.

All input data is validated by Pydantic.

Pagination, sorting, filtering are available on the query endpoints.

93% test coverage. Mostly covered business logic in service classes. Integration tests would be nice. Repositories are not tested.

## Architecture

The business logic lives in `service` classes, one for each model type. Routers use those services to perform operations.
This allows for easier maintenance and an easier transition to a `v2`, `v3`, etc. API as you would be reusing most of the code but would change a scheme or add a few more endpoints.

Database communication is done in repositories. Thus, services contain only business logic, unrelated to any external entity. We can easily mock our repositories and thus we have easy testing and maintainability, as well as the option to change the database without too much hassle.


## Installation

`docker build -t books_reviewing .`

This will build the `books_reviewing` docker image.

Use `docker-compose up` to start the application. Access the OpenAPI specs on `127.0.0.1/docs` where you can create requests.

The application pre-seeds the database with dummy data and deletes it when it is shutdown. You can set the `SEED_DUMMY_DATABASE` env variable to `0` in `docker-compose.yml` if you would like to have a clean database.

## OpenAPI spec

You can access the OpenAPI spec here for a quick review: https://petstore.swagger.io/?url=https://raw.githubusercontent.com/zeno-bg/book-reviewing/main/openapi.json
