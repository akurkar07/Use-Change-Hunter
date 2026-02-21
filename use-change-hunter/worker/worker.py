from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
app = Celery("use_change_hunter", broker=redis_url, backend=redis_url)

from jobs import prefetch_demo, batch_score

if __name__ == "__main__":
    app.start()
