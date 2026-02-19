# Dongle Connect P1 Meter

Home Assistant custom integration for the Dongle Connect P1 Meter. The dongle broadcasts real-time energy data via UDP on the local network, and this integration exposes it as sensor entities in Home Assistant.

## Features

- Real-time power and voltage/current updates (~1s)
- Energy and gas meter totals from full telegrams (~60s)
- WiFi signal strength monitoring
- All sensors grouped under a single device
- No cloud, no polling — pure local push via UDP

## Sensors

| Sensor | Unit | Update Frequency |
|--------|------|-----------------|
| Power Delivered | kW | ~1s |
| Power Returned | kW | ~1s |
| Voltage L1 | V | ~1s |
| Current L1 | A | ~1s |
| Energy Delivered Tariff 1 | kWh | ~60s |
| Energy Delivered Tariff 2 | kWh | ~60s |
| Energy Returned Tariff 1 | kWh | ~60s |
| Energy Returned Tariff 2 | kWh | ~60s |
| Gas Delivered | m³ | ~60s |
| WiFi RSSI | dBm | ~60s |

## Installation

### HACS

1. In HACS, go to **Integrations → ⋮ → Custom repositories**
2. Add this repository URL with category **Integration**
3. Search for "Dongle Connect P1 Meter" and click **Download**
4. Restart Home Assistant

### Manual

1. Copy `custom_components/p1_meter/` to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for "Dongle Connect P1 Meter"
3. Enter the IP address of your dongle

The integration listens for UDP broadcasts on port 16121. Sensors will populate once the first packets arrive.
