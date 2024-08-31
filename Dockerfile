# FROM python:3.8-slim
FROM python:3.5.10-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN apt-get update && apt-get install -y wget gnupg2 lsb-release && \
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

# Install PostgreSQL 12 and other required packages
RUN apt-get update && \
    apt-get install -y \
    postgresql-12 postgresql-12-postgis-3 \
    libpq-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY plugins.txt /app/
RUN pip install --no-cache-dir -r plugins.txt
COPY . /app/
EXPOSE 8001

# Command to run the application
# CMD ["gunicorn", "undpnuprp.wsgi:application", "--bind", "0.0.0.0:8001"]
