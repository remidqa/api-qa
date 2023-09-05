FROM python:3.11-slim

ENV FLASK_APP=api_qa
ENV FLASK_RUN_PORT=5020
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 11

WORKDIR /app

COPY . .

RUN python -m pip install -r requirements.txt

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]

EXPOSE 5020
