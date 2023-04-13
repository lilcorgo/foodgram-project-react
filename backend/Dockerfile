FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .

COPY data .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

RUN pip install gunicorn

CMD ["gunicorn", "foodgram_api.wsgi:application", "--bind", "0:8000"]