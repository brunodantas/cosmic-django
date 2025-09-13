FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set environment variables for uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Create and set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy the Django project
COPY cosmic/ ./cosmic/
COPY allocation/ ./allocation/

# Install the project
RUN uv sync --frozen

# Expose Django's default port
EXPOSE 8000

# Set the default command to run the Django development server
CMD ["uv", "run", "python", "cosmic/manage.py", "runserver", "0.0.0.0:8000"]