# Entities

All entity IDs are prefixed with `sensor.nexxtmove_<username>_` or `switch.nexxtmove_<username>_`.

## Account device

| Entity | Type | Description |
| --- | --- | --- |
| `profile` | `sensor` | Profile info (username, email, ...) |
| `recent_charges` | `sensor` | Number of charges in history, with full charge history in attributes |
| `non_invoiced` | `sensor` | Total non-invoiced amount (€) with list of non-invoiced charges in attributes |
| `consumption` | `sensor` | Total energy consumption (kWh) |

## Company device

| Entity | Type | Description |
| --- | --- | --- |
| `company` | `sensor` | Company info (name, type, ...) |

## Residential location device

| Entity | Type | Description |
| --- | --- | --- |
| `residential_location_<id>` | `sensor` | Residential location info (name, city, ...) |

## Work location device

| Entity | Type | Description |
| --- | --- | --- |
| `work_location_<id>` | `sensor` | Work location info (name, city, ...) |

## Charging device

| Entity | Type | Description |
| --- | --- | --- |
| `charging_device_<id>` | `sensor` | Charging device info (name, type, building, ...) |
| `charging_device_<id>_period_cost` | `sensor` | Total cost (€) for the current period |
| `charging_device_<id>_period_energy` | `sensor` | Total energy (kWh) for the current period |
| `charging_device_<id>_period_reimbursed` | `sensor` | Total reimbursed (€) for the current period |
| `charging_device_<id>_period_charges` | `sensor` | Number of charges for the current period |
| `charging_device_<id>_month_cost` | `sensor` | Total cost (€) for the past month |
| `charging_device_<id>_month_energy` | `sensor` | Total energy (kWh) for the past month |
| `charging_device_<id>_month_reimbursed` | `sensor` | Total reimbursed (€) for the past month |
| `charging_device_<id>_month_charges` | `sensor` | Number of charges for the past month |
| `charging_device_<id>_events` | `sensor` | Number of events, with event list in attributes |

## Charging point device

| Entity | Type | Description |
| --- | --- | --- |
| `charging_point_<id>` | `sensor` | Charging point info (name, type, status, ...) |
| `charging_point_<id>_price` | `sensor` | Price per kWh |
| `charging_point_<id>_events` | `sensor` | Number of events, with event list in attributes |

## Notes

- `recent_charges` accumulates a persistent history of charge sessions across updates (merged by `csid`)
- `period` = from the 1st of the previous month until today
- `month` = the past 30 days
- Attributes containing large lists (`charges`, `events`, `dates`, `values`, `locations`) are excluded from the HA recorder
