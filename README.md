# Unofficial Leak Defense Integration for Home Assistant

An unofficial Home Assistant integration for [Leak Defense](https://www.catchaleak.com) smart water leak detection system.

> **This project is not affiliated with, endorsed by, or in any way connected to Leak Defense, Sentinel Hydrosolutions, LLC, Watts, or any of their affiliates or subsidiaries. "Leak Defense" is a trademark of its respective owner. Use of the name here is solely for identification purposes.**

---

## ⚠️ IMPORTANT: LEGAL DISCLAIMER & LIABILITY WAIVER

**By installing or using this software, you acknowledge and agree to the following:**

1.  **PHYSICAL IMPACT & RISK:** This software controls physical water valves and alarm thresholds. Defects in code, Home Assistant logic errors, or network latency can result in **unintended water shutoffs** or **failure to detect/stop a leak**.
2.  **NO WARRANTY:** This integration is provided "as is" and "as available." The authors make no guarantees of reliability, accuracy, or fitness for the purpose of leak detection.
3.  **LIMITATION OF LIABILITY:** In no event shall the authors be liable for any claims or damages (whether in contract, tort, or otherwise), including but not limited to:
    * **Property Damage:** Water damage, flooding, mold, or structural issues.
    * **Financial Loss:** High water bills, plumbing costs, or loss of insurance coverage.
    * **Life Safety:** This software is **NOT** intended for use in systems where failure could lead to personal injury (e.g., shared fire sprinkler lines).
4.  **INSURANCE & WARRANTY:** Use of this integration may void your manufacturer warranty or invalidate homeowners' insurance credits related to leak detection. You are responsible for verifying your policy terms.
5.  **UNOFFICIAL API:** This relies on undocumented API behavior obtained via network interception. The manufacturer may change or disable this access at any time without notice.
See `LICENSE` for the full terms.

---

## Features

Each Leak Defense panel registered to your account is exposed as a Home Assistant device with the following entities:

| Entity | Type | Description |
|---|---|---|
| Water | Switch | Open or close the main water shutoff valve |
| Flow Rate | Sensor | Current flow as a percentage of the trip threshold |
| Alarm | Binary Sensor | On when the panel is in a leak alarm state |
| Connectivity | Binary Sensor | On when the panel is online |
| Valve Moving | Binary Sensor | On while the valve is in transit |
| Temperature | Sensor | Pipe temperature (if supported by your sensor) |
| Trip Rate | Number | Flow percentage that starts the alarm countdown |
| Time to Alarm | Number | How long flow must exceed the trip rate before the alarm triggers (minutes) |
| Alarm Countdown | Sensor | Remaining minutes until the alarm fires; unavailable when flow is below the trip rate |

Polling interval: **20 seconds** (matches the LeakDefense app's own update interval).

---

## Installation

This integration is not available in HACS. Install it manually:

1. Copy the `custom_components/leakdefense` directory into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Integrations → Add Integration** and search for **LeakDefense**.
4. Enter your API token and device ID (see [Obtaining Credentials](#obtaining-credentials) below).

---

## Obtaining Credentials

The integration requires two values that are not exposed in the LeakDefense app UI. You will need to capture them from the app's network traffic using a proxy tool (e.g., mitmproxy, Charles, or similar):

- **`token`** — found in the `token` HTTP header of any request made by the app to `www.catchaleak.com`
- **`device_id`** — found in the `deviceid` HTTP header of the same requests

These values do not change and can be reused indefinitely.

---

## License

MIT License. See [LICENSE](LICENSE).
