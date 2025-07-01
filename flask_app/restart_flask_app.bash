docker stop pi-iot-flask
docker rm pi-iot-flask

docker run -d --name pi-iot-flask \
  -p "5031:5031" \
  --env-file ~/Documents/projects/dht22-pi-flask/.env \
  --restart=always \
  pingshian0131/pi-iot-flask:latest
