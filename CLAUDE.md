# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Home Assistant custom integration for the EARN-E energy monitor. The device reads a smart meter's P1 port and broadcasts real-time energy data via UDP on the local network. This integration listens for those broadcasts and exposes them as sensor entities in Home Assistant.

- **Integration domain:** `earn_e_p1`
- **IoT class:** `local_push` (no polling; data pushed via UDP on port 16121)
- **Platform:** Sensor only
- **Distributed via:** HACS (Home Assistant Community Store)
- **Minimum HA version:** 2024.1.0
- **No external pip dependencies**

## Development

There is no build system, test suite, or linter configured. The integration is pure Python with no compilation step. To test, install into a Home Assistant development environment by copying `custom_components/earn_e_p1/` into the HA config directory.

## Architecture

```
custom_components/earn_e_p1/
├── __init__.py       # Entry point: async_setup_entry / async_unload_entry
├── config_flow.py    # Config flow with manual IP entry + UDP auto-discovery
├── const.py          # Domain, port, P1SensorFieldDescriptor dataclass, SENSOR_FIELDS tuple
├── coordinator.py    # DataUpdateCoordinator + asyncio DatagramProtocol (UDP listener)
├── sensor.py         # SensorEntity subclass, creates entities from SENSOR_FIELDS descriptors
├── manifest.json     # Integration metadata
├── strings.json      # UI strings (config flow steps, entity names)
└── translations/en.json
```

**Data flow:** Device UDP broadcast → `EarnEP1UDPProtocol` (port 16121) → `EarnEP1Coordinator` merges JSON payload → `EarnEP1Sensor` entities read from coordinator data.

**Key patterns:**
- All sensors are defined declaratively via `SENSOR_FIELDS` tuple of `P1SensorFieldDescriptor` dataclasses in `const.py`. To add a new sensor, add a descriptor there.
- The coordinator extends HA's `DataUpdateCoordinator` but does not poll — it receives pushes from the UDP protocol handler and calls `async_set_updated_data()`.
- Config flow supports three paths: manual IP entry, UDP broadcast auto-discovery (10s listen), and reconfiguration.
- Device identity (serial, model, sw_version) is extracted from the first UDP payload and stored on the coordinator.
- Sensor availability depends on the sensor's JSON key being present in the coordinator's merged data dict.

## Conventions

- All modules use `from __future__ import annotations`
- Async/await throughout; all HA lifecycle methods are async
- Module-level `_LOGGER = logging.getLogger(__name__)`
- Type hints on all function signatures
- Follows standard Home Assistant integration structure and naming conventions