FROM python:3.12.8
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt
RUN uv pip --system install -r requirements.txt
RUN uv pip --system install "psycopg[binary,pool]"

EXPOSE 8080

COPY . .

RUN chmod +x execute.sh