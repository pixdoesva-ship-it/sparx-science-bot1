# Use official Python image with Playwright pre-installed
FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port (Render requires it, even for bots)
EXPOSE 10000

# Run the bot
CMD ["python", "main.py"]
