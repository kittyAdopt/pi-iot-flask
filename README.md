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

*   The Docker images for the `flask-app` and `data-processor` services use `python:3.12` as their base image. The `data-processor` image also explicitly installs `libgpiod2` (the C library for GPIO access) and `gpiod` (CLI tools) to support sensor readings with `adafruit-blinka`.
*   The Flask app (`flask_app/app.py`) runs with `debug=False` by default when using the Docker setup, which is recommended for production or staging environments.
*   The Flask app and the data collection script (`data_processor/save_data_to_db.py`) both load InfluxDB connection details from environment variables, which are supplied via the `.env` file in the Docker Compose setup (or via `--env-file` if using `docker run`).
*   The `adafruit-blinka`, `adafruit-circuitpython-dht`, and `lgpio` (Python bindings for `libgpiod`) libraries in `data_processor/requirements.txt` are for interacting with hardware sensors.
*   **Hardware Access for `data-processor`**: To allow the `data-processor` container to access host GPIO hardware (e.g., on a Raspberry Pi), you **must** configure it with appropriate permissions. In `docker-compose.yml` (for local development) or in the `docker run` command (used by the GitHub Actions deploy step), ensure options like `--privileged` and/or `--device /dev/gpiomem --device /dev/gpiochip0` are used. This is crucial because even with the necessary libraries (`libgpiod2`, `lgpio`) installed in the container, it still needs permission to interact with the host's hardware. Without these Docker permissions, `adafruit-blinka` will likely fail to detect the hardware or time out, leading to errors in `save_data_to_db.py`. If you run the container on a machine without physical sensor hardware or appropriate emulation/permissions, the script might log errors but is designed to handle `RuntimeError` exceptions and continue attempting to read.

## CI/CD with GitHub Actions

This project includes a GitHub Actions workflow defined in `.github/workflows/main.yml` that automates building Docker images and deploying the application.

### Workflow Overview

The workflow consists of two main jobs:

1.  **`build_and_push`**:
    *   Triggered on every push to any branch.
    *   Checks out the source code.
    *   Logs into Docker Hub.
    *   Builds two Docker images:
        *   `pingshian0131/pi-iot-flask:data-processor` (from `data_processor/Dockerfile`)
        *   `pingshian0131/pi-iot-flask:latest` (from `flask_app/Dockerfile`)
    *   Tags the images with both a static tag (e.g., `latest`, `data-processor`) and a dynamic tag based on the Git commit SHA (e.g., `data-processor-a1b2c3d`).
    *   Pushes these images to Docker Hub.

2.  **`deploy`**:
    *   Depends on the successful completion of the `build_and_push` job.
    *   **Warning**: This job currently triggers on pushes to *any branch*. It is highly recommended to modify the workflow to restrict deployment to a specific branch (e.g., `main`) by adding a conditional like `if: github.ref == 'refs/heads/main'` to the `deploy` job definition.
    *   **Tailscale Integration**:
        *   The job first establishes a Tailscale connection from the GitHub Actions runner to your private network. This allows secure access to your deployment server without exposing it directly to the internet.
        *   It uses a `TAILSCALE_AUTH_KEY` secret (an ephemeral auth key with appropriate tags like `tag:ci-runner` is recommended).
        *   The SSH connection (`appleboy/ssh-action`) then connects to your server using its Tailscale MagicDNS name or Tailscale IP address (e.g., `your-deploy-server-tailscale-name` or `100.x.y.z`). You will need to replace the placeholder in the workflow with your server's actual Tailscale address.
    *   Creates a `.env` file on the server using the content of the `ENV_FILE_CONTENT` GitHub secret.
    *   Stops and removes any existing `db-process` and `pi-iot-flask` containers.
    *   Removes the `pingshian0131/pi-iot-flask:data-processor` and `pingshian0131/pi-iot-flask:latest` Docker images from the server to ensure fresh images are pulled.
    *   Pulls the latest images from Docker Hub.
    *   Starts the `db-process` container using `pingshian0131/pi-iot-flask:data-processor`.
    *   Starts the `pi-iot-flask` container using `pingshian0131/pi-iot-flask:latest`.

### Required GitHub Secrets

To use this workflow, you need to configure the following secrets in your GitHub repository settings (`Settings > Secrets and variables > Actions`):

*   `DOCKERHUB_USERNAME`: Your Docker Hub username.
*   `DOCKERHUB_TOKEN`: Your Docker Hub Personal Access Token (PAT) with read/write permissions.
*   `TAILSCALE_AUTH_KEY`: A Tailscale auth key (ephemeral and tagged recommended, e.g., with `tag:ci-runner`) to allow the GitHub Actions runner to join your tailnet.
*   `DEPLOY_USERNAME`: The username for SSH login to your deployment server.
*   `DEPLOY_SSH_KEY`: The private SSH key (ensure the public key is in the server's `authorized_keys`) for connecting to your deployment server.
*   `ENV_FILE_CONTENT`: The complete content of your application's `.env` file. This file contains sensitive information like InfluxDB credentials.
*   Note: The `DEPLOY_HOST` secret is no longer directly used by the SSH action if using Tailscale; instead, you modify the workflow file to include the server's Tailscale name/IP.

### Workflow Assumptions

*   **Tailscale Setup**:
    *   Your deployment server must be running Tailscale and be part of your tailnet.
    *   You should have appropriate Tailscale ACLs configured to allow nodes tagged as `tag:ci-runner` (or your chosen tag) to connect to your deployment server on the SSH port (e.g., port 22).
    *   The workflow file's `deploy` job needs to have the `host` field for the SSH action updated from the placeholder `your-deploy-server-tailscale-name` to your server's actual Tailscale MagicDNS name or IP address.
*   **InfluxDB**: The workflow assumes that an InfluxDB instance is already running and accessible to the application containers on the deployment server, as configured in your `.env` file.
*   **Server Setup**: The deployment server needs to have Docker installed and the SSH user must have permissions to run Docker commands.
*   **Project Directory**: The deploy script creates a project directory (default `~/pi-iot-project`) on the server to store the `.env` file. The `docker run` commands use this `.env` file.

### Important Security Note for `ENV_FILE_CONTENT`

Storing the entire `.env` file content as a GitHub secret is convenient but means this sensitive data is accessible within the GitHub Actions environment. For production systems with highly sensitive data, consider using a dedicated secrets management solution (e.g., HashiCorp Vault, AWS Secrets Manager) and fetching secrets at deploy time, or ensuring the `.env` file is securely managed directly on the server outside of the CI/CD push.
