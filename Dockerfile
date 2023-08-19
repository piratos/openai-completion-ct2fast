FROM python:3.10-slim-bullseye

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY main.py /app/

EXPOSE 7091

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]
