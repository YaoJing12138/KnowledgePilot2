# 1. 基础镜像：从官方精简版 Python 3.11 开始打底
FROM python:3.11-slim

# 2. 设定容器内的工作目录（容器内部路径，和你的 D:\ 无关）
WORKDIR /app

# 3. 先只拷贝依赖清单，再装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 上面装完依赖后，再拷贝其余全部源码
COPY . .

# 5. 说明容器对外暴露 8000 端口（这是文档性的，实际映射在 run 时做）
EXPOSE 8000

# 6. 容器启动时执行的命令：必须是 0.0.0.0
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
