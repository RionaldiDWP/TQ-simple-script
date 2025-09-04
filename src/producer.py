import asyncio
import websockets
import redis.asyncio as redis
import json
import uuid
from datetime import datetime, timezone
from functools import partial

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
QUEUE_NAME = 'audio_processing_queue'

async def redis_listener(websocket, pubsub, client_id):
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                data = json.loads(message['data'])
                await websocket.send(f"Result for task {data['task_id']}: {data['result']}")
    
    except asyncio.CancelledError:
        print(f"[{client_id}] Listener task cancelled.")
    finally:
        await pubsub.close()

async def handler(websocket, redis_client, client_id):
    try:
        async for message in websocket:
            task_id = str(uuid.uuid4())
            print(f"Received message: {message}, assigned task ID: {task_id}")
            task = {
                'task_id': task_id,
                'client_id': client_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': message
            }
            await redis_client.lpush(QUEUE_NAME, json.dumps(task))
            print(f"Task {task_id} enqueued successfully.")

            await websocket.send(f"Task {task_id} received and enqueued.")


    
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    except Exception as e:
        print(f"An error occurred: {e}")

async def connection_manager(websocket, redis_client):
    client_id = str(uuid.uuid4())  # Unique for each client connection
    pubsub = redis_client.pubsub()

    result_channel = f"result_{client_id}"
    await pubsub.subscribe(result_channel)

    listener_task = asyncio.create_task(redis_listener(websocket, pubsub, client_id))
    handler_task = asyncio.create_task(handler(websocket, redis_client, client_id))

    done, pending = await asyncio.wait(
        [listener_task, handler_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
    
    print(f"Connection with client {client_id} closed.")

async def main():
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client = redis.Redis(connection_pool=pool)

    try:
        await redis_client.ping()
        print("Connected to Redis successfully.")
    except Exception as e:
        print(f"Could not connect to Redis: {e}")
        return

    handler_with_redis = partial(connection_manager, redis_client=redis_client)

    async with websockets.serve(handler_with_redis, "localhost", 8765) as server:
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future() 


if __name__ == "__main__":
    asyncio.run(main())
