FROM python:3.10-slim

WORKDIR /app

COPY testcases/requirements.txt .

RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY testcases/ .

CMD ["gunicorn","testcases.wsgi:application","--bind","0:8000"]
