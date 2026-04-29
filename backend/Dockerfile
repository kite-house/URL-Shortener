FROM python:3.12.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn src.main:app --host $BACKEND_HOST --port $BACKEND_PORT --reload --workers 4"]