import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.minio import init_minio_bucket
from app import routers
from app import metrics
from elasticsearch import AsyncElasticsearch


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await wait_for_elasticsearch(es):
        raise Exception("Elasticsearch is not available after waiting")

    init_minio_bucket()

    yield


app = FastAPI(title="Blog", lifespan=lifespan)

app.include_router(routers.router)
app.include_router(metrics.router)

es = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])


async def wait_for_elasticsearch(es_client, timeout: int = 60):
    for i in range(timeout):
        try:
            if await es_client.ping():
                return True
        except Exception:
            pass
        await asyncio.sleep(1)
    return False
