# Multi-stage build
# Builder
FROM python:3.12-slim AS builder

WORKDIR /

# todo: reduce amount of libraries?
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*


COPY req.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r req.txt

# Tests
FROM builder AS tester

COPY . .
RUN pip install pytest
RUN pytest --disable-warnings --tb=auto tests/


# Application runtime
FROM python:3.12-slim AS runtime

WORKDIR /

# postgresql
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin


COPY . .

# Default
EXPOSE 8000

# DB Setup + ASGI
CMD ["bash", "-c", "python setup_db.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
