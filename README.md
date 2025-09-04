# Example Script TQ

## Setup

### 1. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install websockets redis
```

### 3. Run Redis with Docker

```bash
docker run --name my-redis -p 6379:6379 -d redis
```

## Running the Scripts

Open separate terminals for each process and run:

```bash
# Terminal 1: Start the worker
python src/worker.py

# Terminal 2: Start the producer (WebSocket server)
python src/producer.py
```

## Testing

You can test the server using either:

- The provided client script:
  ```bash
  python client.py
  ```
- Or a WebSocket client (e.g., Postman) by connecting to:
  ```
  ws://localhost:8765
  ```