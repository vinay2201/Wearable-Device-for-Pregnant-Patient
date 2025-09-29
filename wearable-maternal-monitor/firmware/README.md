# Firmware (Embedded C) — Example

Reference-only firmware sketch showing how sensor values could be packed into a LoRa frame.

- Reads mock sensors (replace with real I2C/SPI drivers)
- Encodes a compact binary payload (little-endian floats)
- Sends via `lora_send()` (replace with your LoRa driver, e.g., SX1276 HAL or LMIC)
- Also prints JSON to UART for debugging

> This is a generic example; integrate with your MCU HAL/SDK and LoRa stack.
