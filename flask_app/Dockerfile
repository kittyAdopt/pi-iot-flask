# Use Python 3.12 slim as a base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application script into the container at /app
COPY app.py /app/app.py

# Copy the templates directory into the container at /app/templates
COPY templates/ /app/templates/

# Define environment variables for InfluxDB connection
# These will be set at runtime by docker-compose
ENV INFLUXDB_URL=http://influxdb:8086
ENV INFLUXDB_TOKEN=
ENV INFLUXDB_ORG=
ENV INFLUXDB_BUCKET=

# Make port 5031 available to the world outside this container
EXPOSE 5031

# Define the command to run the application
CMD ["python", "app.py"]
