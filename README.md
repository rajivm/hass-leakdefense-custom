# Unofficial Leak Defense for Home Assistant

An unofficial Home Assistant integration for [Leak Defense](https://www.catchaleak.com) smart water leak detection system.

> **This project is not affiliated with, endorsed by, or in any way connected to Leak Defense, Sentinel Hydrosolutions, LLC, Watts, or any of their affiliates or subsidiaries. "Leak Defense" is a trademark of its respective owner. Use of the name here is solely for identification purposes.**

---

## Warning

**This integration controls physical water shutoff valves and alarm thresholds in your home or building. Incorrect configuration or software defects could result in your water being shut off unexpectedly, alarms failing to trigger, or other unintended physical consequences. Use entirely at your own risk.**

The author(s) of this software make no guarantees of correctness, reliability, or fitness for any purpose. See the [license](#license) for the full disclaimer.

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

## Disclaimer and Limitation of Liability

This software is an independent, community-developed project and is provided **"as is"**, without warranty of any kind, express or implied.

- This project is **not affiliated with, sponsored by, or endorsed by** LeakDefense, CatchALeak, Sentinel Hydrosolutions, LLC, Watts, or any related entity.
- The LeakDefense name and any associated trademarks belong to their respective owners.
- This integration uses an **unofficial API** that is not publicly documented and may change or break at any time without notice.
- The author(s) provide **no support**, make no commitment to maintain this project, and accept no responsibility for any outcome resulting from its use.
- Use of this integration may **violate the LeakDefense Terms of Service**. You are solely responsible for determining whether your use is permitted.
- Because this software can **open and close water valves and modify alarm thresholds**, a defect or misconfiguration could cause property damage, flooding, or failure to detect a leak. The author(s) expressly disclaim all liability for any such outcomes.

See `LICENSE` for the full terms.

---

## License

BSD 3-Clause License. See [LICENSE](LICENSE).
