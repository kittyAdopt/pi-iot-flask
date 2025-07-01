docker stop db-process

docker rm db-process

docker run -d --name db-process \
  --env-file ~/Documents/projects/dht22-pi-flask/.env \
  --privileged \
  --device /dev/gpiomem \
  --device /dev/gpiochip0 \
  --restart=always \
  pingshian0131/pi-iot-flask:data-process

