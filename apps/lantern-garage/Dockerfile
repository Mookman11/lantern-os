# Lantern Garage + Discord Bot (Single Container)
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (Node + Python build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install Node dependencies
COPY package*.json ./
RUN npm ci --production

# Copy application code
COPY . .

# Expose web port
EXPOSE 8080

# Start both services
# Web server + Discord bot
CMD ["sh", "-c", "node server.js & python src/discord_lounge_bot/bot.py"]