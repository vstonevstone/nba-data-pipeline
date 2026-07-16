FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY schema.sql .
COPY src/ ./src/
COPY main.py .

ENTRYPOINT ["python", "main.py"]