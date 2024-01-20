
# Speedtest Monitor Results

## Overview
**Speedtest Monitor Results** is a Python Flask web application designed to display and refresh speedtest results logged into a MariaDB database. It visualizes the results in a web interface, updating the data every 300 seconds.

---

### Getting Started

#### Prerequisites
- Python 3
- Flask
- `pip3`
- MariaDB/MySQL database

#### Dependencies
- `pymysql`
- `Flask`
- `pandas`
- `seaborn`
- `matplotlib`

Install them using:
```bash
pip3 install pymysql Flask pandas seaborn matplotlib
```

#### Configuration
Create a `config.ini` in the same directory as `app.py` with the following content:

```ini
[database]
host=YOUR_DATABASE_HOST
port=YOUR_DATABASE_PORT
user=YOUR_DATABASE_USER
password=YOUR_DATABASE_PASSWORD
```
Replace the placeholders with your actual database credentials.

#### Initialization
Initialize and activate the Python environment:

```bash
python3 -m venv venv
source venv/bin/activate
cd path_to_your_project
```

Run the application:

```bash
flask run --host=0.0.0.0 --port=8080
```

---

### Features
- Auto-refreshing visualization of speedtest results.
- Interactive plots displayed in a web interface.
- Each plot represents data from a distinct host in the database.

---

### Feedback
We are open to feedback and suggestions. Please feel free to contribute or report issues on our GitHub repository.

---

### Disclaimer
This project is intended for educational and monitoring purposes. Please use it responsibly.

---

### Acknowledgements
Thanks to the Python and Flask communities for the resources and inspiration for this project.

---

Enjoy monitoring your internet speeds with **Speedtest Monitor Results**!
