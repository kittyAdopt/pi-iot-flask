import os
import time
import board
import adafruit_dht
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

load_dotenv()

# --- InfluxDB Configuration ---
INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN", "")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG", "")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET", "")

if (
    not INFLUXDB_URL or
    not INFLUXDB_TOKEN or
    not INFLUXDB_ORG or
    not INFLUXDB_BUCKET
):
    raise ValueError("DB DATA NOT SETUP!!!!!!!!!!!")

# --- DHT22 Sensor Configuration ---
dhtDevice = adafruit_dht.DHT22(board.D2)

def main():
    """
    Reads temperature and humidity from the DHT22 sensor and writes it to InfluxDB.
    """
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    while True:
        try:
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity

            if temperature_c is not None and humidity is not None:
                print(f"Temp: {temperature_c:.1f} C / Humidity: {humidity:.1f} %")

                point = Point("environment") \
                    .tag("location", "living_room") \
                    .field("temperature", float(temperature_c)) \
                    .field("humidity", float(humidity)) \
                    .time(int(time.time()), WritePrecision.S)

                write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

            else:
                print("Failed to retrieve reading. Trying again...")

        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as e:
            dhtDevice.exit()
            raise e

        time.sleep(15)  # Wait 15 seconds before the next reading

if __name__ == '__main__':
    main()
