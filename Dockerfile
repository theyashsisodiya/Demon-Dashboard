# Use ultra-lightweight Alpine-based Python image (~50MB)
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Ensure stdout and stderr streams are unbuffered (logs show in real time)
ENV PYTHONUNBUFFERED=1 \
    PORT=8080

# Copy application files
COPY server.py ./
COPY static/ ./static/
COPY ZENIN.zip ./
COPY dark.zip ./
COPY keys.db ./

# Expose server port
EXPOSE 8080

# Run the server
CMD ["python", "server.py"]
