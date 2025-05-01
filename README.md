# eMShome Smart Meter Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This custom integration allows you to monitor your eMShome Smart Meter in Home Assistant.

## Features

- Monitor total active power consumption
- Monitor active power consumption per phase (L1, L2, L3)
- Real-time updates via WebSocket connection

## Screenshots

![eMShome Integration](https://via.placeholder.com/800x450.png?text=eMShome+Integration)

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

- `sensor.total_active_power`: Total active power consumption
- `sensor.l1_active_power`: Phase L1 active power consumption
- `sensor.l2_active_power`: Phase L2 active power consumption
- `sensor.l3_active_power`: Phase L3 active power consumption

## Examples

### Energy Dashboard Integration

```yaml
energy:
  grid:
    - name: Grid Consumption
      entity_id: sensor.total_active_power
```

### Lovelace Card Example

```yaml
type: entities
title: eMShome Smart Meter
entities:
  - entity: sensor.total_active_power
  - entity: sensor.l1_active_power
  - entity: sensor.l2_active_power
  - entity: sensor.l3_active_power
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.****
