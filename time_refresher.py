import redis

r = redis.from_url(os.environ["REDIS_URL"])

def reset_counter():
  r.set("counter", 0)

if __name__ == "__main__":
  reset_counter()
