# Keenetic SMS Integration for Home Assistant

This custom integration reads and decodes UCS2 SMS messages from a Keenetic LTE router.

## Installation

1. Add this repository as a custom repository in HACS (type: integration).
2. Install "Keenetic SMS".
3. Go to Settings → Devices & Services → Add Integration → Keenetic SMS.
4. Enter URL and scan interval.

## Features

- Periodic polling via HTTP
- Decodes UCS2 messages from AT+CMGL=4
- Displays result in a single sensor