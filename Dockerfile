FROM python:3.10

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY poetry.lock pyproject.toml ./

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY . .

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "localhost", "--port", "8022"]