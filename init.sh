#!/bin/bash

echo ">>> Starting services with Docker Compose..."
docker-compose up --build -d

echo ">>> Running migrations..."
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

echo ">>> Fixing sequences..."
docker-compose exec web python manage.py fix_sequences

echo ">>> Running initial data ingestion via Celery..."
docker-compose exec web python manage.py shell -c "from customers.tasks import ingest_data; ingest_data.delay()"

echo ">>> Testing register API..."
curl -X POST http://localhost:8000/api/customers/register/ \
-H "Content-Type: application/json" \
-d '{
  "first_name": "Init",
  "last_name": "Test",
  "age": 25,
  "monthly_income": 50000,
  "phone_number": "9112836477"
}'

echo ">>> Setup completed successfully!"
