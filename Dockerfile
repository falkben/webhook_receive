FROM python:3.12

WORKDIR /app

COPY . /app
RUN pip --no-cache-dir install .

EXPOSE 5000
CMD ["uvicorn", "webhook_receive.main:app", "--host", "0.0.0.0", "--port", "5000"]
