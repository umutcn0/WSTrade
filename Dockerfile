FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure poetry to not create a virtual environment since we're in a container
RUN poetry config virtualenvs.create false

# Install dependencies (added --no-root flag)
RUN poetry install --without dev --no-interaction --no-ansi --no-root

# Copy application code
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 