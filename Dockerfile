FROM python:3-alpine AS builder

WORKDIR /app

COPY . .

RUN ["sh", "app.setup.sh"]

EXPOSE 5000

CMD ["sh", "app.run.sh"]