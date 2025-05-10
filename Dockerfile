FROM python:3.12.8
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock ./

# Install dependencies
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --locked --no-dev

EXPOSE 8080

COPY . .

RUN chmod +x execute.sh