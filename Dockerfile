# Use a lightweight Python image
FROM python:3.10-alpine

# Set the working directory
WORKDIR /app

# Install Poetry and dependencies
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install

# Copy application code
COPY . .

# Expose the port for FastAPI.
EXPOSE 8000

# Start the application
CMD ["poetry", "run", "start"]