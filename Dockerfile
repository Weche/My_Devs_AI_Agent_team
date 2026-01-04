# Multi-stage Dockerfile for Albedo AI Team
# Combines Python (Telegram Bot) + Node.js (Dev Agents)

# Stage 1: Build Node.js agents
FROM node:24-slim AS node-builder

WORKDIR /app/dev-agents

# Copy package files
COPY dev-agents/package.json dev-agents/orchestrator.js dev-agents/shared-env.js dev-agents/shared-env.d.ts ./

# Copy all 3 agents
COPY dev-agents/frontend-agent ./frontend-agent
COPY dev-agents/backend-agent ./backend-agent
COPY dev-agents/database-agent ./database-agent

# Install dependencies for orchestrator
RUN npm install

# Install dependencies for each agent
RUN cd frontend-agent && npm install && npm run build
RUN cd backend-agent && npm install && npm run build
RUN cd database-agent && npm install && npm run build

# Stage 2: Python + Node.js runtime
FROM python:3.13-slim

# Install Node.js in the Python image
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application
COPY src/ ./src/
COPY config/ ./config/

# Copy Node.js agents from builder
COPY --from=node-builder /app/dev-agents ./dev-agents

# Create directories for volumes
RUN mkdir -p /data/database /app/workspaces

# Create startup script that runs both Python and Node.js
RUN echo '#!/bin/bash\n\
echo "Starting Albedo AI Team..."\n\
echo ""\n\
echo "Starting Dev Agents (Node.js)..."\n\
cd /app/dev-agents && npm start &\n\
AGENTS_PID=$!\n\
echo "Dev Agents started with PID: $AGENTS_PID"\n\
echo ""\n\
sleep 5\n\
echo "Starting Telegram Bot (Python)..."\n\
cd /app && python src/telegram/bot.py &\n\
BOT_PID=$!\n\
echo "Telegram Bot started with PID: $BOT_PID"\n\
echo ""\n\
echo "All services running!"\n\
echo "  - Dev Agents: http://localhost:3001, 3002, 3003"\n\
echo "  - Telegram Bot: Connected"\n\
echo ""\n\
wait -n\n\
exit $?\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports (internal only)
EXPOSE 3001 3002 3003 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3001/health || exit 1

# Run startup script
CMD ["/app/start.sh"]
