FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY db/ /app/db/
COPY collector/ /app/collector/

CMD ["python", "collector/main.py"]
