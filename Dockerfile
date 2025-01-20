FROM python:3.12.8-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache gcc libffi-dev musl-dev sqlite-dev \
    && pip install --no-cache-dir --upgrade pip

COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . /app/

# Expose FastAPI default port
EXPOSE 9090

CMD ["python", "-m", "app.main"]
