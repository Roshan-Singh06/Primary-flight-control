
import math
import time
import streamlit as st

# EXPERIMENTAL PROTOTYPE — NOT FOR FLIGHT USE

P0 = 101325.0
RHO0 = 1.225
T0_CUSTOM = 287.15
T0_ISA = 288.15
R = 287.0
GAMMA = 1.4
G0 = 9.80665
LAPSE = 0.0065
KNOTS = 1.943844492
FEET = 3.280839895

st.set_page_config(
    page_title="AeroPanel | Flight Instruments",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp {background:#0b111a;color:#e7edf5;}
header[data-testid="stHeader"] {background:transparent;}
.block-container {padding-top:1.5rem;max-width:1500px;}
[data-testid="stSidebar"] {background:#111b28;border-right:1px solid #263549;}
[data-testid="stMetric"] {
    background:#131e2c;border:1px solid #27374a;
    padding:17px;border-radius:12px;
}
[data-testid="stMetricLabel"] {color:#91a5bd;font-size:13px;}
[data-testid="stMetricValue"] {color:#f0f6ff;font-size:27px;}
div[data-testid="stVerticalBlock"] > div {gap:0.65rem;}
h1,h2,h3 {color:#f0f6ff;}
hr {border-color:#27374a;}
.eyebrow {color:#6ec8ff;font-size:11px;font-weight:700;letter-spacing:2px;}
.hero {background:linear-gradient(120deg,#16283b,#101a28);
border:1px solid #293c52;border-radius:16px;padding:22px 25px;margin-bottom:18px;}
.hero-title {font-size:28px;font-weight:750;color:#f2f7ff;}
.hero-sub {color:#9aafc5;font-size:13px;margin-top:5px;}
.section {font-size:12px;letter-spacing:1.6px;font-weight:700;
color:#70c8ff;margin:16px 0 10px;}
.panel {background:#131e2c;border:1px solid #27374a;border-radius:14px;
padding:17px;margin-bottom:10px;}
.small {font-size:12px;color:#8fa3ba;}
.warning {color:#ffcc7a;font-size:12px;}
[data-testid="stMetricDelta"] {font-size:12px;}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def density_from_pressure_temperature(ps, temperature):
    if ps <= 0 or temperature <= 0:
        raise ValueError("Pressure and temperature must be positive.")
    return ps / (R * temperature)


def pressure_altitude_m(ps, p_ref, t_ref):
    exponent = R * LAPSE / G0
    altitude = (t_ref / LAPSE) * (
        1 - (ps / p_ref) ** exponent
    )
    return clamp(altitude, -500, 11000)


def airspeeds(pt, ps, temperature, p0=P0, rho0=RHO0, t0=T0_ISA):
    if pt <= 0 or ps <= 0:
        raise ValueError("Pt and Ps must be positive.")
    if pt < ps:
        raise ValueError("Pt must be greater than or equal to Ps.")
    if temperature <= 0:
        raise ValueError("Temperature must be positive Kelvin.")

    qc = pt - ps

    mach2 = (2 / (GAMMA - 1)) * (
        (pt / ps) ** ((GAMMA - 1) / GAMMA) - 1
    )
    mach = math.sqrt(max(0, mach2))

    cas2 = (2 / (GAMMA - 1)) * (
        (1 + qc / p0) ** ((GAMMA - 1) / GAMMA) - 1
    )
    a0 = math.sqrt(GAMMA * R * t0)
    cas = a0 * math.sqrt(max(0, cas2))

    rho = density_from_pressure_temperature(ps, temperature)
    tas = mach * math.sqrt(GAMMA * R * temperature)
    eas = tas * math.sqrt(rho / rho0)

    tas_low = math.sqrt(max(0, 2 * qc / rho))
    eas_low = math.sqrt(max(0, 2 * qc / rho0))

    return {
        "qc": qc,
        "mach": mach,
        "rho": rho,
        "ias": cas,
        "cas": cas,
        "eas": eas,
        "tas": tas,
        "tas_low": tas_low,
        "eas_low": eas_low,
    }


def horizon_svg(pitch, bank):
    horizon_y = clamp(105 - pitch * 2, 25, 185)

    return f"""
    <div style="display:flex;justify-content:center;padding:10px">
    <svg width="100%" height="280" viewBox="0 0 360 280"
         xmlns="http://www.w3.org/2000/svg">
      <defs>
        <clipPath id="horizonClip">
          <circle cx="180" cy="130" r="105"/>
        </clipPath>
      </defs>
      <circle cx="180" cy="130" r="110" fill="#07101a"
              stroke="#41556d" stroke-width="2"/>
      <g clip-path="url(#horizonClip)">
        <rect x="75" y="25" width="210" height="210" fill="#2475a8"/>
        <g transform="rotate({-bank} 180 130)">
          <rect x="30" y="{horizon_y}" width="300" height="180"
                fill="#986443"/>
          <line x1="25" y1="{horizon_y}" x2="335" y2="{horizon_y}"
                stroke="#f5d7a1" stroke-width="3"/>
          {''.join(
              f'<line x1="{180-(55 if d > 0 else 40)}" '
              f'y1="{130-d*3}" x2="{180+(55 if d > 0 else 40)}" '
              f'y2="{130-d*3}" stroke="#f4f7fb" stroke-width="2"/>'
              for d in [-20,-10,10,20]
          )}
        </g>
      </g>
      <circle cx="180" cy="130" r="105" fill="none"
              stroke="#dbe7f4" stroke-width="2"/>
      <path d="M120 130 H157 M203 130 H240
               M157 130 L166 138 H194 L203 130"
            fill="none" stroke="#ffd45e" stroke-width="4"
            stroke-linecap="round"/>
      <text x="180" y="263" fill="#c9d7e7" text-anchor="middle"
            font-family="monospace" font-size="12">
        PITCH {pitch:+.0f}°  /  BANK {bank:+.0f}°
      </text>
    </svg>
    </div>
    """


def instrument_card(title, value, unit):
    st.markdown(
        f"""
        <div class="panel">
          <div style="color:#91a5bd;font-size:12px;
                      letter-spacing:1px">{title}</div>
          <div style="font-size:27px;font-weight:750;
                      color:#f0f6ff;margin-top:8px">{value}</div>
          <div class="small">{unit}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# HEADER
st.markdown("""
<div class="hero">
  <div class="eyebrow">AIR DATA SYSTEMS / PROTOTYPE 01</div>
  <div class="hero-title">AEROPANEL</div>
  <div class="hero-sub">
    Primary Flight Instruments · Pressure-based flight data
  </div>
</div>
""", unsafe_allow_html=True)

st.warning("EXPERIMENTAL SIMULATION — NOT FOR FLIGHT USE")

# SIDEBAR
with st.sidebar:
    st.markdown("## ✈ Flight Setup")
    st.caption("Configure the air-data inputs.")

    mode = st.radio(
        "Data source",
        ["Manual input", "Simulated variation"]
    )

    pt = st.number_input(
        "Total pressure Pt (Pa)",
        min_value=1.0, max_value=150000.0,
        value=112000.0, step=100.0
    )

    ps = st.number_input(
        "Static pressure Ps (Pa)",
        min_value=1.0, max_value=120000.0,
        value=101325.0, step=100.0
    )

    temp_c = st.number_input(
        "Static temperature (°C)",
        min_value=-80.0, max_value=60.0,
        value=15.0, step=0.5
    )

    st.markdown("---")
    st.markdown("### Atmospheric reference")

    reference = st.selectbox(
        "Reference temperature",
        ["Standard ISA · 288.15 K", "Custom · 287.15 K"]
    )
    t0 = T0_ISA if reference.startswith("Standard") else T0_CUSTOM

    st.markdown("---")
    st.markdown("### Altimeter / Kollsman")

    kollsman = st.number_input(
        "Pressure setting (hPa)",
        min_value=800.0, max_value=1100.0,
        value=1013.25, step=0.25
    )

    units = st.radio("Altitude units", ["ft", "m"], horizontal=True)

    st.markdown("---")
    st.markdown("### Attitude reference")

    pitch = st.slider("Pitch angle", -30.0, 30.0, 3.0, 1.0)
    bank = st.slider("Bank angle", -90.0, 90.0, 12.0, 1.0)

    st.caption("Real attitude data will require an IMU.")


if mode == "Simulated variation":
    pt += 150 * math.sin(time.time() * 0.7)


# CALCULATIONS AND DISPLAY
try:
    data = airspeeds(pt, ps, temp_c + 273.15, P0, RHO0, t0)

    altitude = pressure_altitude_m(ps, kollsman * 100, t0)
    pressure_alt = pressure_altitude_m(ps, P0, t0)

    now = time.monotonic()
    previous = st.session_state.get("alt_sample")

    vsi = 0.0
    if previous:
        old_time, old_altitude = previous
        dt = max(0.1, now - old_time)
        vsi = clamp(
            (altitude - old_altitude) / dt * FEET * 60,
            -6000, 6000
        )

    st.session_state["alt_sample"] = (now, altitude)
    old_vsi = st.session_state.get("vsi_smoothed", 0.0)
    vsi = 0.75 * old_vsi + 0.25 * vsi
    st.session_state["vsi_smoothed"] = vsi

    # AIRSPEED STRIP
    st.markdown('<div class="section">01 / AIRSPEED INDICATOR</div>',
                unsafe_allow_html=True)

    cols = st.columns(4)
    readings = [
        ("IAS", f"{data['ias']*KNOTS:.1f}", "kt · approx. CAS"),
        ("CAS", f"{data['cas']*KNOTS:.1f}", "knots"),
        ("EAS", f"{data['eas']*KNOTS:.1f}", "knots"),
        ("TAS", f"{data['tas']*KNOTS:.1f}", "knots"),
    ]

    for col, (title, value, unit) in zip(cols, readings):
        with col:
            instrument_card(title, value, unit)

    # AIR DATA
    st.markdown('<div class="section">02 / AIR DATA</div>',
                unsafe_allow_html=True)

    cols = st.columns(4)
    with cols[0]:
        instrument_card("MACH NUMBER", f"{data['mach']:.3f}", "Mach")
    with cols[1]:
        instrument_card("IMPACT PRESSURE", f"{data['qc']:.0f}", "Pa")
    with cols[2]:
        instrument_card("AIR DENSITY", f"{data['rho']:.4f}", "kg/m³")
    with cols[3]:
        instrument_card("VERTICAL SPEED", f"{vsi:+.0f}", "ft/min")

    # ALTIMETER AND HORIZON
    left, right = st.columns([1.1, 1])

    with left:
        st.markdown('<div class="section">03 / ALTIMETER</div>',
                    unsafe_allow_html=True)

        alt_value = altitude * FEET if units == "ft" else altitude
        pa_value = pressure_alt * FEET if units == "ft" else pressure_alt

        instrument_card(
            "INDICATED ALTITUDE",
            f"{alt_value:,.0f}",
            units
        )
        instrument_card(
            "PRESSURE ALTITUDE",
            f"{pa_value:,.0f}",
            units
        )
        instrument_card(
            "KOLLSMAN SETTING",
            f"{kollsman:.2f}",
            f"hPa  /  {kollsman / 33.8638867:.2f} inHg"
        )

    with right:
        st.markdown('<div class="section">04 / ATTITUDE INDICATOR</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(horizon_svg(pitch, bank), unsafe_allow_html=True)
        st.markdown(
            f"<div style='text-align:center;color:#9aafc5'>"
            f"PITCH <b>{pitch:+.0f}°</b>"
            f"&nbsp;&nbsp;&nbsp; BANK <b>{bank:+.0f}°</b></div>",
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("Low-speed approximations from your formulas"):
        c1, c2 = st.columns(2)
        c1.metric("TAS approximation", f"{data['tas_low']*KNOTS:.1f} kt")
        c2.metric("EAS approximation", f"{data['eas_low']*KNOTS:.1f} kt")

    st.markdown("---")
    st.markdown(
        '<div class="small">AEROPANEL · Experimental air-data prototype · '
        'IAS approximated as CAS · Artificial horizon simulated · '
        'Not certified for aircraft operation.</div>',
        unsafe_allow_html=True
    )

except (ValueError, OverflowError, ZeroDivisionError) as exc:
    st.error(f"Input error: {exc}")
