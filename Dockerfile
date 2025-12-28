FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN pip install --no-cache-dir .

EXPOSE 5000
CMD ["uvicorn", "webhook_receive.main:app", "--host", "0.0.0.0", "--port", "5000"]
