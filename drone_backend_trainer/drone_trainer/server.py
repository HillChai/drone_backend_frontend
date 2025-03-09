from fastapi import FastAPI
from starlette.responses import StreamingResponse
import docker
import json
import time

app = FastAPI()
# 使用 Windows 远程 API 连接 Docker
DOCKER_API_URL = "unix://var/run/docker.sock"
CONTAINER_NAME = "ecg_after_requirement"

try:
    client = docker.DockerClient(base_url=DOCKER_API_URL)
    print("✅ 成功连接到 Docker API")
except Exception as e:
    print(f"❌ 连接 Docker 失败: {e}")

def stream_training_logs():
    try:
        container = client.containers.get(CONTAINER_NAME)
        # ✅ 直接监听 `exec_run` 运行的进程日志，而不是 `docker logs`
        command = "python3 /drone_system_material/algorithms/dronerf_vits/multi_resolution_vits/MyTrain.py"
        exec_result = container.exec_run(
            ["sh", "-c", command],
            stream=True
        )
        for line in exec_result.output:
            yield f"data: {line.decode('utf-8')}\n\n"
    except Exception as e:
        yield f"data: {str(e)}\n\n"

@app.get("/train_progress")
async def train_progress():
    """ SSE 端点，实时推送训练日志 """
    return StreamingResponse(stream_training_logs(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
