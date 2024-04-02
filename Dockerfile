FROM python:3.10.2-bullseye
WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
