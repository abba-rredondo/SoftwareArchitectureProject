FROM python:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python populate_keyspace.py && touch /app/.db_initialized || echo "La base de datos ya ha sido inicializada."

EXPOSE 8000


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
