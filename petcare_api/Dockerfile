FROM python:3.12-slim

WORKDIR /app

# Install API dependencies
COPY petcare_api/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy runtime domain modules
COPY petcare_runtime/src/petcare ./petcare_runtime/src/petcare

# Copy API entrypoint
COPY petcare_api/main.py ./main.py

ENV PYTHONPATH="/app/petcare_runtime/src"
ENV PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
