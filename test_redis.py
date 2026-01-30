import redis

try:
    r = redis.from_url('redis://127.0.0.1:6379/0')
    r.ping()
    print("Successfully connected to Redis.")
except Exception as e:
    print(f"Failed to connect to Redis: {e}")
