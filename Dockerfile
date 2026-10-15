FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt pyproject.toml ./
COPY src ./src
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install -e .

COPY . .

CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000", "-f", "orchestration/definitions.py"]

