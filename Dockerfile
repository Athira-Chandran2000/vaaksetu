# ─── Stage 1: Build the React Frontend ───
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ─── Stage 2: Setup the Python Backend ───
FROM python:3.10-slim

# Create a non-root user for Hugging Face (required)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install backend dependencies
COPY --chown=user backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --user -r backend/requirements.txt

# Copy backend source
COPY --chown=user backend/ ./backend/

# Copy the built frontend from Stage 1
COPY --chown=user --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port (Hugging Face uses 7860)
ENV PORT=7860
EXPOSE 7860

# Set working directory to backend to run the app
WORKDIR /app/backend

# Command to run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
