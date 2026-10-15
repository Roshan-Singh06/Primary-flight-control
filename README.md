# Aircraft Primary Flight Instrument Dashboard

Experimental Streamlit prototype for educational development.
NOT FOR FLIGHT USE.

## Files

- app.py: dashboard and calculations
- requirements.txt: Python dependencies
- README.md: project documentation

## Features

- IAS (approximated as CAS), CAS, EAS and TAS
- Mach number, impact pressure and density
- Altimeter with adjustable Kollsman reference pressure
- Pressure altitude estimate
- VSI estimate from successive Streamlit reruns
- Simulated artificial horizon with pitch and bank controls
- Low-speed airspeed approximations
- Configurable reference temperature

## Requirements

- Python 3.9 or newer
- Streamlit

## Installation and execution

Install the dependency:

    python -m pip install -r requirements.txt

Run the application:

    streamlit run app.py

## Reference constants

- Sea-level pressure: 101325 Pa
- Reference density: 1.225 kg/m^3
- Custom reference temperature: 287.15 K
- Standard ISA sea-level temperature: 288.15 K
- Specific gas constant: 287 J/(kg K)
- Specific heat ratio: 1.4
- Standard gravity: 9.80665 m/s^2

## Limitations

- IAS is approximated as CAS; no instrument or position-error correction.
- Airspeed equations assume subsonic, isentropic flow.
- Altitude uses a tropospheric approximation, not a complete
  multilayer ISA model.
- VSI is estimated between Streamlit reruns.
- Artificial horizon is simulated; real attitude requires an IMU.
- Sensor integration and calibration are not implemented.
- This is not a certified or operational aircraft instrument.
