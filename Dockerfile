FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml poetry.lock README.md /app/

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false
COPY run_web.py /app/
COPY src /app/src

RUN poetry install --no-interaction --no-ansi

EXPOSE 8000

CMD ["python", "-m", "run_web"]