from fastapi import FastAPI
import httpx
import logging
import time

app = FastAPI()

SERVICE_1_URL = "https://prod-tools.kodif.io/tools/internal/execute"
SERVICE_2_URL = "https://tools.kodif.io/tools/internal/execute"

logging.basicConfig(level=logging.INFO)

@app.get("/")
async def aggregate():
    payload = {
    "name": "zendesk_list_all_articles",
    "company_id": "2438",
    "context": {
    }
}

    headers = {
        "Content-Type": "application/json",
        "Connection": "close"  
    }

    client = httpx.AsyncClient(http2=False, headers=headers)

    durations_1 = []
    durations_2 = []

    for i in range(10):
        start = time.perf_counter()
        res = await client.post(SERVICE_1_URL, json=payload)
        duration = time.perf_counter() - start
        durations_1.append(duration)
        logging.info(f"[Service 1 - #{i+1}] Status: {res.status_code}, Time: {duration:.3f}s")

    for i in range(10):
        start = time.perf_counter()
        res = await client.post(SERVICE_2_URL, json=payload)
        duration = time.perf_counter() - start
        durations_2.append(duration)
        logging.info(f"[Service 2 - #{i+1}] Status: {res.status_code}, Time: {duration:.3f}s")

    await client.aclose()

    def stats(durations):
        return {
            "min": f"{min(durations):.3f} sec",
            "max": f"{max(durations):.3f} sec",
            "avg": f"{sum(durations)/len(durations):.3f} sec"
        }

    stats_1 = stats(durations_1)
    stats_2 = stats(durations_2)

    logging.info(f"Service 1 - Min: {stats_1['min']}, Max: {stats_1['max']}, Avg: {stats_1['avg']}")
    logging.info(f"Service 2 - Min: {stats_2['min']}, Max: {stats_2['max']}, Avg: {stats_2['avg']}")

    return {
        "K8S": stats_1,
        "EBS": stats_2
    }
