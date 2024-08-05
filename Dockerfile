FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Install PostGIS and other required packages
RUN apt-get update && \
    apt-get install -y \
    postgis build-essential \
    postgresql \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirement.txt /app/
RUN pip install --no-cache-dir -r requirement.txt
COPY . /app/
EXPOSE 8000

# Command to run the application
# CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
