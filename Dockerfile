# Stage 1: Build dependencies
FROM python:3.11-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

# Copy requirements
COPY requirements.txt .

# Build wheels for the dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# Stage 2: Final lightweight image
FROM python:3.11-alpine

WORKDIR /app

# Copy wheels from the builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install packages using the built wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Copy the application code
COPY . .

# Expose port
EXPOSE 5000

# Run flask app with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
