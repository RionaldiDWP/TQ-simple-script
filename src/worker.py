import redis
import json
import time
import random

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
QUEUE_TASK = 'audio_processing_queue'

def process_task(task):

    print(f"Processing task ID: {task['task_id']} with data: {task['data']}")
    # generate random string
    random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
    
    time.sleep(2)
    print(f"Task ID: {task['task_id']} processed successfully.")
    return random_str


def main():
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    print("successfully connected to redis. Waiting for tasks...")

    while True:
        # blocking command until a task is available so it doesn't constantly poll the server
        # 0 = block indefinitely
        try:
            _, task_json = redis_client.brpop(QUEUE_TASK, 0)

            task = json.loads(task_json.decode('utf-8'))
            result = process_task(task)
            client_id = task.get('client_id')
            if client_id:
                result_channel = f"result_{client_id}"
                result_data = {
                    'task_id': task.get('task_id'),
                    'result': result
                }
                redis_client.publish(result_channel, json.dumps(result_data))
                print(f"Published result for task ID: {task['task_id']} to channel: {result_channel}")

        except redis.exceptions.ConnectionError as e:
            print(f"Could not connect to Redis, retrying in 5 seconds... Error: {e}")
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nShutting down worker.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()