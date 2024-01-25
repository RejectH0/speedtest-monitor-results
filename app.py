###################################################################
#
# Version 1.3 - 20240124-2335
# This app.py Flask Python application is the monitoring and reporting portion of the speedtest logging utilities
# Created and maintain by RejectH0. Hotel Coral Essex.
#
# 1.3 adds the ability to disable a host through the new 'status' table for each database.

from flask import Flask, render_template, request
import threading
import time
import pymysql
import logging
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
logging.basicConfig(filename='app.log', level=logging.ERROR)
# Shared resources and their lock
plot_params = {'start': None, 'end': None}
plot_params_lock = threading.Lock()
plot_lock = threading.Lock()  # To avoid concurrency issues
latest_plots = []
latest_plots_lock = threading.Lock()
# Directory where plot images will be saved
PLOT_DIR = 'static/images'
os.makedirs(PLOT_DIR, exist_ok=True)  # Ensure the directory exists
global_start, global_end = None, None

def get_databases():
    try:
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASS)
        cursor = conn.cursor()
        query = "SHOW DATABASES LIKE '%\_speedtest';"  # Updated query
        cursor.execute(query)
        all_dbs = cursor.fetchall()
        cursor.close()
        conn.close()
        return [db[0] for db in all_dbs]
    except Exception as e:
        logging.error(f"Error fetching database list: {e}")
        return []

def is_host_enabled():
    try:
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASS)
        cursor = conn.cursor()
        cursor.execute("SELECT enabled FROM status ORDER BY id DESC LIMIT 1;")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else False
    except Exception as e:
        logging.error(f"Error checking host status: {e}")
        return False

def fetch_data(db_name, start=None, end=None):
    # Corrected SQL query
    query = "SELECT timestamp, (download / 1000000) AS download_mbps, (upload / 1000000) AS upload_mbps FROM speedtest_results"

    if start and end:
        query += " WHERE timestamp BETWEEN %s AND %s"

    try:
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASS, db=db_name)
        cursor = conn.cursor()
        if start and end:
            cursor.execute(query, (start, end))
        else:
            cursor.execute(query)
        data = pd.DataFrame(cursor.fetchall(), columns=['timestamp', 'download_mbps', 'upload_mbps'])
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        logging.error(f"Error fetching data from database {db_name}: {e}")
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
        logging.error(f"Error plotting data for database {db_name}: {e}")
        return None


def update_plots():
    while True:
        with plot_params_lock:
            start = plot_params['start']
            end = plot_params['end']

        new_plots = []
        dbs = get_databases()
        for db in dbs:
            if not is_host_enabled():
			    logging.error(f"Host {db} is currently disabled. Skipping.")
                continue
            data = fetch_data(db, start, end)
            if data is not None and not data.empty:
                filename = plot_data(data, db)
                if filename:
                    new_plots.append({'filename': filename, 'caption': f"{db} plot"})

        with latest_plots_lock:
            global latest_plots
            latest_plots = new_plots

        time.sleep(300)

plot_thread = threading.Thread(target=update_plots)
plot_thread.daemon = True
plot_thread.start()

@app.route('/', methods=['GET'])
def index():
    global plot_params
    with plot_params_lock:
        plot_params['start'] = request.args.get('start')
        plot_params['end'] = request.args.get('end')

    with latest_plots_lock:
        return render_template('index.html', plots=latest_plots)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
