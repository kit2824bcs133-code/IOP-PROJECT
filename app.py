"""Streamlit dashboard for an educational EV battery health project."""

from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from battery import (
    calculate_soh,
    classify_health,
    estimate_rul,
    generate_simulated_reading,
)


APP_DIR = Path(__file__).parent
HISTORY_FILE = APP_DIR / "data" / "battery_history.csv"
HISTORY_COLUMNS = [
    "timestamp",
    "voltage_v",
    "current_a",
    "temperature_c",
    "rated_capacity_ah",
    "current_capacity_ah",
    "soh_percent",
    "health",
    "rul_years",
    "degradation_rate_percent_per_year",
    "reading_type",
]

SAMPLE_READING = {
    "voltage_v": 52.4,
    "current_a": 18.2,
    "temperature_c": 31.5,
    "rated_capacity_ah": 100.0,
    "current_capacity_ah": 86.0,
}


def ensure_history_file() -> None:
    """Create the history folder and CSV header if this is a fresh install."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        pd.DataFrame(columns=HISTORY_COLUMNS).to_csv(HISTORY_FILE, index=False)


def make_prediction(
    reading: dict[str, float], degradation_rate: float, reading_type: str
) -> dict[str, object]:
    """Combine the input reading with the project's simple calculations."""
    soh = calculate_soh(
        reading["current_capacity_ah"], reading["rated_capacity_ah"]
    )
    return {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        **reading,
        "soh_percent": round(soh, 2),
        "health": classify_health(soh),
        "rul_years": round(estimate_rul(soh, degradation_rate), 2),
        "degradation_rate_percent_per_year": degradation_rate,
        "reading_type": reading_type,
    }


def save_reading(record: dict[str, object]) -> None:
    """Append one reading and its prediction to the CSV history."""
    ensure_history_file()
    pd.DataFrame([record], columns=HISTORY_COLUMNS).to_csv(
        HISTORY_FILE, mode="a", header=False, index=False
    )


def load_history() -> pd.DataFrame:
    ensure_history_file()
    history = pd.read_csv(HISTORY_FILE)
    if history.empty:
        return pd.DataFrame(columns=HISTORY_COLUMNS)
    history["timestamp"] = pd.to_datetime(history["timestamp"], errors="coerce")
    return history.dropna(subset=["timestamp"]).sort_values("timestamp")


def advisor_messages(health: str, temperature: float) -> tuple[str, str]:
    """Return short general-purpose suggestions in English and Tamil."""
    if temperature >= 40:
        english = "The battery is warm. Reduce heavy use and let it cool in a safe, ventilated place."
        tamil = "மின்கலம் சூடாக உள்ளது. அதிக பயன்பாட்டைத் தவிர்த்து, காற்றோட்டமான பாதுகாப்பான இடத்தில் குளிரவிடவும்."
    elif health == "Good":
        english = "Health looks good in this estimate. Continue routine inspection and follow the vehicle maker's guidance."
        tamil = "இந்த மதிப்பீட்டில் மின்கலத்தின் நிலை நன்றாக உள்ளது. வழக்கமான பரிசோதனையைத் தொடரவும்; வாகன தயாரிப்பாளரின் வழிகாட்டுதலைப் பின்பற்றவும்."
    elif health == "Fair":
        english = "Health is fair in this estimate. Monitor capacity and arrange a professional check if performance changes."
        tamil = "இந்த மதிப்பீட்டில் மின்கலத்தின் நிலை மிதமாக உள்ளது. திறனை கண்காணித்து, செயல்திறன் மாறினால் நிபுணரிடம் பரிசோதிக்கவும்."
    else:
        english = "Health is degraded in this estimate. Ask a qualified technician to inspect the battery."
        tamil = "இந்த மதிப்பீட்டில் மின்கலத்தின் நிலை குறைந்துள்ளது. தகுதியான தொழில்நுட்ப நிபுணரிடம் பரிசோதிக்கவும்."
    return english, tamil


st.set_page_config(
    page_title="EV Battery Health and Life Predictor",
    page_icon="🔋",
    layout="wide",
)

st.title("🔋 EV Battery Health and Life Predictor")
st.caption(
    "A beginner-friendly learning demo. All sample and generated readings are simulated; "
    "predictions are not validated on real batteries."
)

ensure_history_file()

if "voltage_v" not in st.session_state:
    st.session_state.update(SAMPLE_READING)
if "current_record" not in st.session_state:
    st.session_state.current_record = make_prediction(
        SAMPLE_READING, 2.5, "Simulated sample"
    )

with st.sidebar:
    st.header("Battery inputs")
    degradation_rate = st.slider(
        "Assumed degradation rate (% per year)",
        min_value=0.5,
        max_value=10.0,
        value=2.5,
        step=0.5,
        help="A simple assumption used only to estimate remaining life.",
    )
    if st.button("🎲 Generate simulated reading", use_container_width=True):
        simulated = generate_simulated_reading()
        st.session_state.update(simulated)
        generated_record = make_prediction(
            simulated, degradation_rate, "Simulated"
        )
        save_reading(generated_record)
        st.session_state.current_record = generated_record
        st.success("Simulated reading generated and saved.")

    st.info("The values below are user-entered unless generated with the simulation button.")
    with st.form("battery_input_form"):
        voltage_v = st.number_input(
            "Voltage (V)", min_value=0.0, max_value=1000.0, step=0.1, key="voltage_v"
        )
        current_a = st.number_input(
            "Current (A)", min_value=0.0, max_value=10000.0, step=0.1, key="current_a"
        )
        temperature_c = st.number_input(
            "Temperature (°C)",
            min_value=-50.0,
            max_value=150.0,
            step=0.5,
            key="temperature_c",
        )
        rated_capacity_ah = st.number_input(
            "Rated capacity (Ah)",
            min_value=0.1,
            max_value=100000.0,
            step=1.0,
            key="rated_capacity_ah",
        )
        current_capacity_ah = st.number_input(
            "Current capacity (Ah)",
            min_value=0.0,
            max_value=100000.0,
            step=1.0,
            key="current_capacity_ah",
        )
        submitted = st.form_submit_button(
            "Calculate and save reading", use_container_width=True
        )

    if submitted:
        entered_reading = {
            "voltage_v": voltage_v,
            "current_a": current_a,
            "temperature_c": temperature_c,
            "rated_capacity_ah": rated_capacity_ah,
            "current_capacity_ah": current_capacity_ah,
        }
        try:
            record = make_prediction(
                entered_reading, degradation_rate, "User-entered (not validated)"
            )
        except ValueError as error:
            st.error(str(error))
        else:
            save_reading(record)
            st.session_state.current_record = record
            st.success("Reading and prediction saved to CSV.")

record = st.session_state.current_record
health_color = {"Good": "🟢", "Fair": "🟠", "Degraded": "🔴"}.get(
    str(record["health"]), "⚪"
)

st.subheader("Battery information")
card1, card2, card3, card4 = st.columns(4)
card1.metric("State of Health (SOH)", f"{record['soh_percent']:.1f}%")
card2.metric("Health status", f"{health_color} {record['health']}")
card3.metric("Estimated remaining life", f"{record['rul_years']:.1f} years")
card4.metric("Reading type", str(record["reading_type"]))

st.caption(
    "SOH = (Current Capacity ÷ Rated Capacity) × 100. "
    "RUL is a rough estimate to 70% SOH using the selected assumed degradation rate; "
    "it is not a service-life guarantee."
)

english_advice, tamil_advice = advisor_messages(
    str(record["health"]), float(record["temperature_c"])
)
with st.expander("Battery advisor | மின்கல ஆலோசனை", expanded=True):
    st.write(f"**English:** {english_advice}")
    st.write(f"**தமிழ்:** {tamil_advice}")
    st.caption("General educational suggestions only; not a safety diagnosis.")

history = load_history()
chart_rows = history.copy()
current_time = pd.to_datetime(record["timestamp"], errors="coerce")
if pd.notna(current_time):
    active_row = pd.DataFrame([record])
    active_row["timestamp"] = pd.to_datetime(active_row["timestamp"])
    if history.empty or not (
        pd.to_datetime(history["timestamp"]) == current_time
    ).any():
        chart_rows = pd.concat([chart_rows, active_row], ignore_index=True)
chart_rows = chart_rows.sort_values("timestamp").tail(30)

st.subheader("Battery readings over time")
if chart_rows.empty:
    st.info("No readings yet. Generate a simulated reading or save battery inputs.")
else:
    plot_data = chart_rows.melt(
        id_vars=["timestamp", "reading_type"],
        value_vars=["voltage_v", "temperature_c", "soh_percent"],
        var_name="measurement",
        value_name="value",
    )
    plot_data["measurement"] = plot_data["measurement"].map(
        {
            "voltage_v": "Voltage (V)",
            "temperature_c": "Temperature (°C)",
            "soh_percent": "SOH (%)",
        }
    )
    chart = px.line(
        plot_data,
        x="timestamp",
        y="value",
        color="measurement",
        markers=True,
        hover_data=["reading_type"],
        title="Voltage, temperature, and SOH (different units; read each series by its label)",
    )
    st.plotly_chart(chart, use_container_width=True)

st.subheader("Saved prediction history")
if history.empty:
    st.info("No saved history is available.")
else:
    st.dataframe(
        history[HISTORY_COLUMNS].sort_values("timestamp", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

report = pd.DataFrame([record], columns=HISTORY_COLUMNS).to_csv(index=False).encode(
    "utf-8"
)
st.download_button(
    "⬇️ Download current battery report (CSV)",
    data=report,
    file_name="battery_report.csv",
    mime="text/csv",
)

st.caption(
    f"Saved history file: data/battery_history.csv · Assumed degradation rate: "
    f"{degradation_rate:.1f}% per year."
)
