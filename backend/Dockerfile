FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy just the dependency files first
COPY pyproject.toml poetry.lock ./

# Copy the application code before installing dependencies
# This is needed because poetry needs to find the app directory
COPY . .

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --without dev

# Create non-root user and set up SQLite directory
RUN useradd -m -u 1000 appuser && \
    mkdir -p /data && \
    chown -R appuser:appuser /app /data && \
    chmod 777 /data

# Set environment variable for SQLite database location
ENV SQLITE_DB_FILE=/data/scheduler.db

USER appuser

EXPOSE 8000

# Run migrations and start the app
CMD ["sh", "-c", "poetry run alembic upgrade head && poetry run uvicorn app.main:app --host 0.0.0.0 --port 9000"]
