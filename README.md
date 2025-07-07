
# Keenetic SMS Integration for Home Assistant

This custom integration reads and decodes UCS2 SMS messages from a Keenetic LTE router.

## Installation

1. Add this repository as a custom repository in HACS (type: integration).
2. Install "Keenetic SMS".
3. Add to your configuration.yaml:

```yaml
keenetic_sms:
  url: "http://192.168.0.1:81/rci/interface/UsbLte0/tty/send"
  interval: 300
```

4. Restart Home Assistant.
