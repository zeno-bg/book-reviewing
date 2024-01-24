FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./books_reviewing /code/books_reviewing

ENV PYTHONPATH=/code/books_reviewing

CMD ["uvicorn", "books_reviewing.main:app", "--host", "0.0.0.0", "--port", "80"]
