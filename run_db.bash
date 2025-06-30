docker run -d -p 8086:8086 \
  -v "$PWD/data:/var/lib/influxdb2" \
  -v "$PWD/config:/etc/influxdb2" \
  --env-file /home/ping-pi5/.env/influxdb.env \
  influxdb:latest
