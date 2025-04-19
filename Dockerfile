# Stage 1: Build frontend
FROM node:18 AS frontend-builder
WORKDIR /app
COPY ui/package.json ui/package-lock.json ./
RUN npm install
COPY ui .
RUN npm run build

# Stage 2: Build backend
FROM python:3.10-slim AS backend-builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .

# Stage 3: Final image
FROM python:3.10-slim
WORKDIR /app

# Copy built frontend
COPY --from=frontend-builder /app/dist ./ui/dist

# Copy backend
COPY --from=backend-builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=backend-builder /app .

# Environment variables
ENV OLLAMA_URL=http://localhost:11434
ENV PORT=8000
EXPOSE $PORT

# Run both frontend and backend
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
