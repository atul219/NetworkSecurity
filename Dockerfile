FROM python:3.12-slim-bookworm
WORKDIR /app
COPY . /app

RUN apt update -y && apt install awscli -y

RUN apt-get update && pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "app.py"]