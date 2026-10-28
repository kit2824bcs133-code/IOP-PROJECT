# EV Battery Health and Life Predictor

A small, simulation-only college mini-project built with Python, Streamlit, Pandas, and Plotly. It demonstrates a basic battery State of Health (SOH) calculation, a clearly labelled remaining useful life (RUL) estimate, simple charts, an English/Tamil advisor, CSV history, and a downloadable report.

> **Important:** Sample readings and generated readings are simulated. The calculations and suggestions are educational examples and have not been validated on real batteries. This project does not connect to physical hardware and must not be used to make battery safety or replacement decisions.

## What the project does

- Accepts voltage, current, temperature, rated capacity, and current capacity.
- Calculates `SOH = (Current Capacity / Rated Capacity) × 100`.
- Classifies health as **Good** (SOH at least 80%), **Fair** (60% to less than 80%), or **Degraded** (below 60%). These are simple project thresholds.
- Estimates years until 70% SOH using the selected assumed annual degradation rate. This is a rough estimate, not a validated lifetime prediction.
- Charts voltage, temperature, and SOH, and labels simulated/user-entered history.
- Generates simulated readings, saves readings and predictions to `data/battery_history.csv`, and downloads the current result as a CSV report.

## Requirements

- Windows 10 or later
- Python 3.9 or later
- Visual Studio Code with the Python extension

No ESP32, database, MQTT broker, paid API, or machine-learning model is required.

## Install and run in the VS Code PowerShell terminal

Open the project folder in VS Code, choose **Terminal → New Terminal**, and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, allow it only for the current terminal session, then activate:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

Streamlit prints its local URL in the terminal and normally opens a browser. Open **http://localhost:8501** if it does not open automatically. Stop the app with **Ctrl+C** in the terminal.

## Project files

- `app.py` — Streamlit dashboard, inputs, charts, advisor, CSV saving, and report download.
- `battery.py` — standalone SOH, health classification, RUL, and simulated-reading functions.
- `requirements.txt` — Python package dependencies.
- `data/battery_history.csv` — sample row and saved readings/predictions.

## Simple project workflow

1. The dashboard starts with one clearly labelled simulated sample reading.
2. Enter battery readings in the sidebar, or generate a new simulated reading.
3. Press **Calculate and save reading** for entered values. Simulated readings are saved when generated.
4. The app calculates SOH and health status, then estimates RUL from the selected assumed degradation rate.
5. The charts and history table update from saved readings. Download the current prediction as a CSV report.
