from flask import Flask, render_template, jsonify
from influxdb_client import InfluxDBClient
from dotenv import load_dotenv
import os

app = Flask(__name__)

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
# Initialize InfluxDB Client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()

@app.route('/')
def index():
    """Renders the main dashboard page."""
    return render_template('index.html')

@app.route('/data')
def get_latest_data():
    """Provides the latest sensor reading as JSON."""
    flux_query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -10m)
      |> filter(fn: (r) => r._measurement == "environment")
      |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
      |> last()
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    result = query_api.query(query=flux_query)

    if not result or not result[0].records:
        return jsonify(temperature="N/A", humidity="N/A")

    latest_record = result[0].records[0]
    
    # *** FIXED LINE BELOW ***
    # Access data using dictionary-style access on the .values attribute
    data = {
        "temperature": f"{latest_record.values['temperature']:.1f}" if 'temperature' in latest_record.values else "N/A",
        "humidity": f"{latest_record.values['humidity']:.1f}" if 'humidity' in latest_record.values else "N/A"
    }
    return jsonify(data)


@app.route('/history_data')
def get_history_data():
    """Provides aggregated sensor data for the last 8 hours as JSON."""
    flux_query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -8h)
      |> filter(fn: (r) => r._measurement == "environment")
      |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
      |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> yield(name: "mean")
    '''
    results = query_api.query(query=flux_query)

    timestamps = []
    temperatures = []
    humidities = []

    for table in results:
        for record in table.records:
            # Format timestamp for Chart.js
            timestamps.append(record.get_time().strftime('%Y-%m-%dT%H:%M:%SZ'))
            
            # *** FIXED LINES BELOW ***
            # Use .get() for safer access in a loop, it returns None if a key is missing
            temperatures.append(record.values.get('temperature'))
            humidities.append(record.values.get('humidity'))

    return jsonify({
        "timestamps": timestamps,
        "temperatures": temperatures,
        "humidities": humidities
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5031, debug=True)
