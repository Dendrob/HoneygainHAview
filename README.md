# HoneygainHAview for Home Assistant

HoneygainHAview is a custom Home Assistant integration that retrieves account,
device, earnings, wallet, payout, notification, and Honey Pot data from
Honeygain. It uses
[pyHoneygain](https://pypi.org/project/pyHoneygain/), an unofficial library for
the Honeygain dashboard API, and refreshes data every 30 minutes.

> [!WARNING]
> This integration relies on Honeygain's private dashboard API, which may
> change without notice. Your Honeygain credentials grant access to your
> account. Never share them or commit them to a public repository.

## Features

- Configurable through Home Assistant's integration setup flow.
- Periodic updates every 30 minutes.
- Account, device, earnings, wallet, payout, notification, and Honey Pot data.
- Complete API responses available as sensor attributes.
- Read-only access: the integration does not request payouts or change account
  settings.

## Installation

### HACS

1. In HACS, open **Integrations**.
2. Add `https://github.com/Dendrob/HoneygainHAview` as a custom repository with
   the **Integration** category.
3. Install **HoneygainHAview**, then restart Home Assistant.
4. Go to **Settings > Devices & services > Add integration**.
5. Search for **HoneygainHAview** and enter your Honeygain account email and
   password.

The credentials are stored in the Home Assistant config entry and used by
pyHoneygain to obtain an access token.

## Sensors and data

Each sensor stores the complete API response in its `data` attribute. The
returned fields depend on the response provided by Honeygain's API.

| Category | Data |
| --- | --- |
| Account and devices | Account details and device information |
| Earnings | Honeygain and JumpTask earnings for the last 30 days and today |
| Wallet | Wallet statistics, balances, and JumpTask wallet settings |
| Activity | Payouts, notifications, and Honey Pot status |

## Dashboard

The [`dashboard/honeygain.yaml`](dashboard/honeygain.yaml) file provides a
Lovelace dashboard that displays the complete data returned by each endpoint.
Create a YAML dashboard in Home Assistant and copy the file contents into it.
If Home Assistant assigned different entity IDs, update the dashboard's
`sensor.honeygain_*` references to match the IDs shown under
**Settings > Devices & services > Entities**.

## Limitations

`pyHoneygain` is an unofficial library and Honeygain's private API may change
without notice. This integration performs read-only requests; it does not
request payouts, open the Honey Pot, or modify account settings.
