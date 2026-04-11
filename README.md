<p align="center">
  <img src="icon.svg" alt="ABL Logo" width="200">
</p>

# eMShome Smart Meter Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This custom integration allows you to monitor your eMShome Smart Meter in Home Assistant.

## Features

- Monitor and control EV charging modes (Lock, PV, Grid, Hybrid)
- Monitor current EV charging power
- Configure minimum PV power quota for charging modes
- Real-time updates via WebSocket connection


## Installation

### HACS (recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS > Integrations
3. Click the "..." menu and select "Custom repositories"
4. Add the URL of this repository and select "Integration" as the category
5. Click "ADD"
6. Search for "eMShome"
7. Click "Install"
8. Restart Home Assistant

### Manual installation

1. Download the latest release from GitHub
2. Unzip the release and copy the `custom_components/emshome` directory to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to Configuration > Integrations
2. Click the "+ Add Integration" button
3. Search for "eMShome Smart Meter"
4. Enter the IP address of your eMShome device and the password
5. Click "Submit"

## Available Entities

The integration creates the following entities:

- `sensor.current_charging_mode`: Current EV charging mode
- `sensor.current_pv_prozentage`: Current minimum PV power quota percentage
- `sensor.ev_charging_power_total`: Total EV charging power

## Available Services

### emshome.set_charging_mode

Set the charging mode for the EV charger.

**Parameters:**
- `mode` (required): The charging mode to set. Options: `lock`, `pv`, `grid`, `hybrid`
- `minpvpowerquota` (optional): for the hybrid mode

**Example:**
```yaml
service: emshome.set_charging_mode
data:
  mode: hybrid
  minpvpowerquota: 75
```

### emshome.prozentage

Set the minimum PV power quota percentage for hybrid mode.

**Parameters:**
- `prozentage` (required): Percentage value between 1-100

**Example:**
```yaml
service: emshome.prozentage
data:
  prozentage: 60
```

## Examples

### Energy Dashboard Integration

```yaml
energy:
  grid:
    - name: Grid Consumption
      entity_id: sensor.total_active_power
```

### Lovelace Card 
[See here](https://github.com/thetechnikfreak/emshomeevcard)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.****
