#!/bin/bash
app="redcap-data-entry-trigger-host"
port=20000

echo "Stopping ${app}"
docker stop ${app}

echo "Removing ${app}"
docker rm ${app}

echo "Building ${app}"
docker build -t ${app} .

echo "Running ${app}"
docker run -d \
  --restart unless-stopped \
  -p ${port}:${port} \
  --name=${app} \
  -v $PWD:/app ${app}
