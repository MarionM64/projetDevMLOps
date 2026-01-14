# fast and light python image
FROM python:3.11-slim

WORKDIR /app

# Copy the requirements
COPY requirements.txt .

# Install the requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code
COPY . .

# The next command will be surcharged in docker-compose, but will be used in prod
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
