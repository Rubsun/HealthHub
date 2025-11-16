FROM python:3.11-slim as builder

WORKDIR /app

COPY services/integrations-service/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY services/integrations-service/ .

ENV PATH=/root/.local/bin:$PATH

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]



