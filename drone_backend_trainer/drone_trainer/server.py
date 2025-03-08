from fastapi import FastAPI
import time
import json
from starlette.responses import StreamingResponse
from concurrent.futures import ThreadPoolExecutor
import sys

app = FastAPI()

# 模拟训练数据
def train_and_stream():
    for epoch in range(1, 101):
        accuracy = round(epoch * 0.01, 4)
        loss = round(1 / (epoch + 1), 4)
        
        # SSE 格式：每次发送训练进度
        sys.stdout.write(f"data: {json.dumps({'epoch': epoch, 'accuracy': accuracy, 'loss': loss})}\n\n")
        sys.stdout.flush()
        time.sleep(0.5)  # 模拟训练耗时

@app.get("/train_progress")
async def train_progress():
    return StreamingResponse(train_and_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
