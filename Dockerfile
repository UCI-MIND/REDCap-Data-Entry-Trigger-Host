FROM python:3.12.10-alpine3.21

ENV TZ="America/Los_Angeles"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "20000", "--log-level", "warning"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
