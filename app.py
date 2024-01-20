
from flask import Flask, render_template
import threading
import time
import pymysql
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import configparser
import os

# Configuration Variables
config = configparser.ConfigParser()
config.read('config.ini')
DB_HOST = config['database']['host']
DB_PORT = int(config['database']['port'])
DB_USER = config['database']['user']
DB_PASS = config['database']['password']

app = Flask(__name__)

# Directory where plot images will be saved
PLOT_DIR = 'static/images'
os.makedirs(PLOT_DIR, exist_ok=True)  # Ensure the directory exists

def get_databases():
    try:
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASS)
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES;")
        all_dbs = cursor.fetchall()
        cursor.close()
        conn.close()
        return [db[0] for db in all_dbs if db[0].endswith('_speedtest')]
    except Exception as e:
        print(f"Error fetching database list: {e}")
        return []

def fetch_data(db_name):
    try:
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASS, db=db_name)
        cursor = conn.cursor()
        query = "SELECT timestamp, (download / 1024 / 1024) AS download_mbps, (upload / 1024 / 1024) AS upload_mbps FROM speedtest_results"
        cursor.execute(query)
        data = pd.DataFrame(cursor.fetchall(), columns=['timestamp', 'download_mbps', 'upload_mbps'])
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        print(f"Error fetching data from database {db_name}: {e}")
        return None

def plot_data(data, db_name):
    try:
        # Convert 'timestamp' column to datetime objects
        data['timestamp'] = pd.to_datetime(data['timestamp'])

        sns.set(style="whitegrid")
        fig, ax1 = plt.subplots(figsize=(10, 6))

        color = 'tab:blue'
        ax1.set_xlabel('Timestamp')
        ax1.set_ylabel('Download Speed (Mbps)', color=color)
        ax1.plot(data['timestamp'], data['download_mbps'], label='Download Mbps', color=color)
        ax1.tick_params(axis='y', labelcolor=color)

        # Set the y-axis for download to show full range of data
        ax1.set_ylim(min(data['download_mbps']) - (max(data['download_mbps']) * 0.1),
                     max(data['download_mbps']) + (max(data['download_mbps']) * 0.1))

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

        color = 'tab:red'
        ax2.set_ylabel('Upload Speed (Mbps)', color=color)
        ax2.plot(data['timestamp'], data['upload_mbps'], label='Upload Mbps', color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        # Set the y-axis for upload to show full range of data
        ax2.set_ylim(min(data['upload_mbps']) - (max(data['upload_mbps']) * 0.1),
                     max(data['upload_mbps']) + (max(data['upload_mbps']) * 0.1))

        # Improve the readability of the x-axis.
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        fig.autofmt_xdate()  # Rotation

        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.title(f'Speedtest Results for {db_name}')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        # Generate the filename with the current date and time
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{db_name}-{current_time}.png"
        filepath = os.path.join(PLOT_DIR, filename)

        # Save the plot as a PNG file
        plt.savefig(filepath)
        plt.close()

        return filename
    except Exception as e:
        print(f"Error plotting data for database {db_name}: {e}")
        return None

latest_plots = []

def update_plots():
    while True:
        new_plots = []
        dbs = get_databases()
        for db in dbs:
            data = fetch_data(db)
            if data is not None and not data.empty:
                filename = plot_data(data, db)
                if filename:
                    new_plots.append({'filename': filename, 'caption': f"{db} plot"})
        global latest_plots
        latest_plots = new_plots
        time.sleep(300)

plot_thread = threading.Thread(target=update_plots)
plot_thread.daemon = True
plot_thread.start()

@app.route('/')
def index():
    return render_template('index.html', plots=latest_plots)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
