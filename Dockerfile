FROM python:3.12.8

# TODO: Do we need to add environment variables here?

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install "psycopg[binary,pool]"

EXPOSE 8080

COPY . .

RUN chmod +x execute.sh