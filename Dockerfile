# Use Python 3.11 slim (alpine may have issues with faiss-cpu compilation)
FROM python:3.11-slim

# Create and change to the app directory
WORKDIR /app

# Copy local code to the container image
COPY . .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Railway uses PORT env variable)
EXPOSE 8000

# Run the web service on container startup
# Use hypercorn for better async support (Railway recommended)
CMD ["hypercorn", "app.main:app", "--bind", "[::]:8000"]
