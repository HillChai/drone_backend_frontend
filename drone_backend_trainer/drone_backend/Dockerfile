# 使用 Python 3.10 作为基础镜像
FROM python:3.10

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY ./app /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# 暴露 FastAPI 端口
EXPOSE 8000

# 运行 FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
