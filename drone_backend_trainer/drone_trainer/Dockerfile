FROM crpi-9994gc03c1aikjap.cn-hangzhou.personal.cr.aliyuncs.com/radio_fingerprinting/ml_dronerf:latest

WORKDIR /app

# 安装必要的 Python 依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制 API 服务器代码
COPY server.py /app/

# 运行 FastAPI 服务器
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
