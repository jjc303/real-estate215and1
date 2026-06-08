FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

COPY backend/requirements.txt /tmp/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends fonts-wqy-microhei && rm -rf /var/lib/apt/lists/* && pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r /tmp/requirements.txt

COPY backend /app/backend
COPY scripts /app/scripts

EXPOSE 8000

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8000", "app.main:app"]
