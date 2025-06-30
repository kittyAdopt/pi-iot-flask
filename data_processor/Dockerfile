# Use Python 3.12 as a base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/requirements.txt

# Install libgpiod C library and command-line tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgpiod2 \
    gpiod \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the data processor script into the container at /app
COPY save_data_to_db.py /app/save_data_to_db.py

# Define environment variables for InfluxDB connection
# These will be set at runtime by docker-compose
ENV INFLUXDB_URL=http://influxdb:8086
ENV INFLUXDB_TOKEN=
ENV INFLUXDB_ORG=
ENV INFLUXDB_BUCKET=

# Define the command to run the script
CMD ["python", "save_data_to_db.py"]
