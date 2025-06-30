# pi-iot-flask

A Flask application and data processor for collecting sensor data (e.g., temperature and humidity from a DHT22 sensor) and storing it in InfluxDB, with a web interface to view the data. This project is set up to run using Docker and Docker Compose.

## Project Structure

```
.
├── data_processor/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── save_data_to_db.py  # Script to collect sensor data
├── flask_app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py              # Flask application
│   └── templates/
│       └── index.html      # Web interface
├── .env.example            # Example environment variables for the apps
├── influxdb.env.example    # Example environment variables for InfluxDB setup
├── docker-compose.yml      # Docker Compose configuration
├── .gitignore
└── README.md
```

## Prerequisites

*   Docker: [Install Docker](https://docs.docker.com/get-docker/)
*   Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## Running with Docker

This project uses Docker Compose to manage the application, data processor, and InfluxDB services.

### 1. Configure Environment Variables

You'll need to create two environment files: one for the application services (`.env`) and one for the InfluxDB service (`influxdb.env`).

**a. Application Environment (`.env`)**

Copy the example file:

```bash
cp .env.example .env
```

Edit `.env` and fill in the values. These values **must** correspond to the organization, bucket, and admin token you will configure for InfluxDB.

*   `INFLUXDB_URL`: Should generally remain `http://influxdb:8086` when using Docker Compose, as `influxdb` will be the service name.
*   `INFLUXDB_TOKEN`: Set this to the **same value** you will use for `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` in `influxdb.env`.
*   `INFLUXDB_ORG`: Set this to the **same value** you will use for `DOCKER_INFLUXDB_INIT_ORG` in `influxdb.env`.
*   `INFLUXDB_BUCKET`: Set this to the **same value** you will use for `DOCKER_INFLUXDB_INIT_BUCKET` in `influxdb.env`.

**b. InfluxDB Environment (`influxdb.env`)**

Copy the example file:

```bash
cp influxdb.env.example influxdb.env
```

Edit `influxdb.env` and set your desired initial configuration for InfluxDB:

*   `DOCKER_INFLUXDB_INIT_MODE=setup`: Keep this as `setup` for the first run to initialize InfluxDB.
*   `DOCKER_INFLUXDB_INIT_USERNAME`: Your desired username for the InfluxDB initial user.
*   `DOCKER_INFLUXDB_INIT_PASSWORD`: Your desired password for this user.
*   `DOCKER_INFLUXDB_INIT_ORG`: The name of your InfluxDB organization. This will be used as `INFLUXDB_ORG` in the `.env` file for the applications.
*   `DOCKER_INFLUXDB_INIT_BUCKET`: The name of your InfluxDB bucket. This will be used as `INFLUXDB_BUCKET` in the `.env` file for the applications.
*   `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN`: A secure admin token. This token will be used as `INFLUXDB_TOKEN` in the `.env` file for the applications to authenticate.

**Important:** Ensure that `INFLUXDB_TOKEN`, `INFLUXDB_ORG`, and `INFLUXDB_BUCKET` in your `.env` file match `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN`, `DOCKER_INFLUXDB_INIT_ORG`, and `DOCKER_INFLUXDB_INIT_BUCKET` in your `influxdb.env` file, respectively.

### 2. Build and Run Services

Once the environment files are configured, you can build and start all services using Docker Compose:

```bash
docker-compose up --build -d
```

*   `--build`: Forces Docker Compose to build the images before starting the containers.
*   `-d`: Runs the containers in detached mode (in the background).

### 3. Accessing the Application

*   **Web Interface**: Open your browser and go to `http://localhost:5031`
*   **InfluxDB UI**: Open your browser and go to `http://localhost:8086`. You can log in with the username and password specified in `influxdb.env` (`DOCKER_INFLUXDB_INIT_USERNAME` and `DOCKER_INFLUXDB_INIT_PASSWORD`).

### Docker Compose Services

The `docker-compose.yml` file defines three main services:

*   **`flask-app`**:
    *   Builds from `./flask_app/Dockerfile`.
    *   Runs the Flask web application.
    *   Accessible on `http://localhost:5031`.
*   **`data-processor`**:
    *   Builds from `./data_processor/Dockerfile`.
    *   Runs the `save_data_to_db.py` script to collect and store sensor data.
    *   This service requires hardware access if you are using a physical sensor like DHT22. The `docker-compose.yml` includes commented-out lines for `privileged` mode and `devices` mapping that might be necessary on systems like a Raspberry Pi. You may need to uncomment and adjust these based on your hardware setup.
*   **`influxdb`**:
    *   Uses the official `influxdb:latest` image.
    *   Handles the InfluxDB database.
    *   Data is persisted in a Docker volume named `influxdb_data` mapped to `./influxdb_data` on your host machine. This means your database data will remain even if you stop and remove the containers.
    *   Accessible on `http://localhost:8086`.

### Stopping the Services

To stop the running services:

```bash
docker-compose down
```

To stop and remove volumes (including InfluxDB data):

```bash
docker-compose down -v
```

## Development Notes

*   The Docker images for the `flask-app` and `data-processor` services use `python:3.12` as their base image (changed from `python:3.12-slim`) to ensure all necessary system libraries are available for the installed Python packages.
*   The Flask app (`flask_app/app.py`) runs with `debug=False` by default when using the Docker setup, which is recommended for production or staging environments.
*   The Flask app and the data collection script (`data_processor/save_data_to_db.py`) both load InfluxDB connection details from environment variables, which are supplied via the `.env` file in the Docker Compose setup (or via `--env-file` if using `docker run`).
*   The `adafruit-blinka`, `adafruit-circuitpython-dht`, and `lgpio` (for `libgpiod` interaction on newer Raspberry Pi systems) libraries in `data_processor/requirements.txt` are for interacting with hardware sensors.
*   **Hardware Access for `data-processor`**: To allow the `data-processor` container to access host GPIO hardware (e.g., on a Raspberry Pi), you **must** configure it with appropriate permissions. In `docker-compose.yml`, uncomment and use `privileged: true` or specific `devices` mappings (like `/dev/gpiomem`). Without this, `adafruit-blinka` will likely fail to detect the hardware, leading to errors in `save_data_to_db.py`. If you run the container on a machine without this hardware or appropriate emulation/permissions, the script might log errors but is designed to handle `RuntimeError` exceptions and continue attempting to read.
