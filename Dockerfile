FROM python:3.11-slim

WORKDIR /app

# Copy just the requirements first to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY server.py .

# Environment variables will be provided at runtime
ENV METABASE_URL=""
ENV METABASE_USERNAME=""
ENV METABASE_PASSWORD=""

# Run the server using stdio transport (required for Claude)
CMD ["python", "server.py"]
