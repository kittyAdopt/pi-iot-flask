docker run -d --name influxdb \
  -p 8086:8086 \
  -v "$PWD/data:/var/lib/influxdb2" \
  -v "$PWD/config:/etc/influxdb2" \
  --env-file ~/.env/influxdb.env \
  influxdb:latest
