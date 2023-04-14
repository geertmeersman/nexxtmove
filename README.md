<img src="https://github.com/geertmeersman/nexxtmove/raw/main/images/brand/logo.png"
     alt="Nexxtmove"
     align="right"
     style="width: 200px;margin-right: 10px;" />

# Nexxtmove for Home Assistant

A Home Assistant integration allowing to monitor your EV charging and manage your charging points

---

<!-- [START BADGES] -->
<!-- Please keep comment here to allow auto update -->

[![MIT License](https://img.shields.io/github/license/geertmeersman/nexxtmove?style=for-the-badge)](https://github.com/geertmeersman/nexxtmove/blob/master/LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![maintainer](https://img.shields.io/badge/maintainer-Geert%20Meersman-green?style=for-the-badge&logo=github)](https://github.com/geertmeersman)
[![buyme_coffee](https://img.shields.io/badge/Buy%20me%20a%20Duvel-donate-yellow?style=for-the-badge&logo=buymeacoffee)](https://www.buymeacoffee.com/geertmeersman)
[![discord](https://img.shields.io/discord/1094331679327408320?style=for-the-badge&logo=discord)](https://discord.gg/PTpExQJsWA)

[![GitHub issues](https://img.shields.io/github/issues/geertmeersman/nexxtmove)](https://github.com/geertmeersman/nexxtmove/issues)
[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/geertmeersman/nexxtmove.svg)](http://isitmaintained.com/project/geertmeersman/nexxtmove)
[![Percentage of issues still open](http://isitmaintained.com/badge/open/geertmeersman/nexxtmove.svg)](http://isitmaintained.com/project/geertmeersman/nexxtmove)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/geertmeersman/nexxtmove/pulls)

[![Hacs and Hassfest validation](https://github.com/geertmeersman/nexxtmove/actions/workflows/validate.yml/badge.svg)](https://github.com/geertmeersman/nexxtmove/actions/workflows/validate.yml)
[![Python](https://img.shields.io/badge/Python-FFD43B?logo=python)](https://github.com/geertmeersman/nexxtmove/search?l=python)

[![manifest version](https://img.shields.io/github/manifest-json/v/geertmeersman/nexxtmove/master?filename=custom_components%2Fnexxtmove%2Fmanifest.json)](https://github.com/geertmeersman/nexxtmove)
[![github release](https://img.shields.io/github/v/release/geertmeersman/nexxtmove?logo=github)](https://github.com/geertmeersman/nexxtmove/releases)
[![github release date](https://img.shields.io/github/release-date/geertmeersman/nexxtmove)](https://github.com/geertmeersman/nexxtmove/releases)
[![github last-commit](https://img.shields.io/github/last-commit/geertmeersman/nexxtmove)](https://github.com/geertmeersman/nexxtmove/commits)
[![github contributors](https://img.shields.io/github/contributors/geertmeersman/nexxtmove)](https://github.com/geertmeersman/nexxtmove/graphs/contributors)
[![github commit activity](https://img.shields.io/github/commit-activity/y/geertmeersman/nexxtmove?logo=github)](https://github.com/geertmeersman/nexxtmove/commits/main)

<!-- [END BADGES] -->

## Installation

### Using [HACS](https://hacs.xyz/) (recommended)

1. Simply search for `Nexxtmove` in HACS and install it easily.
2. Restart Home Assistant
3. Add the 'nexxtmove' integration via HA Settings > 'Devices and Services' > 'Integrations'
4. Provide your Nexxtmove username and password

### Manual

1. Copy the `custom_components/nexxtmove` directory of this repository as `config/custom_components/nexxtmove` in your Home Assistant instalation.
2. Restart Home Assistant
3. Add the 'Nexxtmove' integration via HA Settings > 'Devices and Services' > 'Integrations'
4. Provide your Nexxtmove username and password

This integration will set up the following platforms.

| Platform    | Description                                     |
| ----------- | ----------------------------------------------- |
| `nexxtmove` | Home Assistant component for Nexxtmove services |

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Troubleshooting

1. You can enable logging for this integration specifically and share your logs, so I can have a deep dive investigation. To enable logging, update your `configuration.yaml` like this, we can get more information in Configuration -> Logs page

```
logger:
  default: warning
  logs:
    custom_components.nexxtmove: debug
```

## Lovelace examples

### Period graphs

![Period Graphs](https://github.com/geertmeersman/nexxtmove/raw/main/images/screenshots/period_graphs.png)

<details><summary>Show markdown code</summary>

**Replace &lt;username&gt; by your Nexxtmove username**

```
type: custom:config-template-card
variables:
  nexxtmove:
    account: geertgerits
    device_id: 1204969
entities:
  - >-
    ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_cost"}
card:
  type: vertical-stack
  cards:
    - type: custom:apexcharts-card
      apex_config:
        tooltip:
          enabled: true
          followCursor: true
          x:
            show: false
            format: MMMM yyyy
          'y':
            show: true
      graph_span: 1year
      header:
        standard_format: false
        show: true
        show_states: false
        title: ${'Nexxtmove costs for the past year €'}
      now:
        show: true
      series:
        - entity: >-
            ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_cost"}
          name: Home
          type: column
          color: 73C56C
          show:
            legend_value: false
          float_precision: 2
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].home];
            });
        - entity: >-
            ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_cost"}
          name: Work
          type: column
          color: ff8d00
          show:
            legend_value: false
          float_precision: 2
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].work];
            });
        - entity: >-
            ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_cost"}
          name: Payment
          type: column
          color: 00a8ff
          show:
            legend_value: false
          float_precision: 2
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].payment];
            });
        - entity: >-
            ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_cost"}
          name: Guest
          type: column
          color: d100a0
          show:
            legend_value: false
          float_precision: 2
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].guest];
            });
    - type: custom:apexcharts-card
      apex_config:
        tooltip:
          enabled: true
          followCursor: true
          x:
            show: false
            format: MMMM yyyy
          'y':
            show: true
      graph_span: 1year
      header:
        standard_format: false
        show: true
        show_states: false
        title: ${'Nexxtmove energy usage for the past year Wh'}
      now:
        show: true
      series:
        - entity: >-
            ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_energy"}
          name: Home
          type: column
          color: 73C56C
          show:
            legend_value: false
          float_precision: 2
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].home];
            });
        - entity: >-
            ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_energy"}
          name: Work
          type: column
          color: ff8d00
          show:
            legend_value: false
          float_precision: 2
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].work];
            });
        - entity: >-
            ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_energy"}
          name: Payment
          type: column
          color: 00a8ff
          show:
            legend_value: false
          float_precision: 2
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].payment];
            });
        - entity: >-
            ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_energy"}
          name: Guest
          type: column
          color: d100a0
          show:
            legend_value: false
          float_precision: 2
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].guest];
            });
    - type: custom:apexcharts-card
      apex_config:
        tooltip:
          enabled: true
          followCursor: true
          x:
            show: false
            format: MMMM yyyy
          'y':
            show: true
      graph_span: 1year
      header:
        standard_format: false
        show: true
        show_states: false
        title: ${'Nexxtmove charges for the past year \#'}
      now:
        show: true
      series:
        - entity: >-
            ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_charges"}
          name: Home
          type: column
          color: 73C56C
          show:
            legend_value: false
          float_precision: 2
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].home];
            });
        - entity: >-
            ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_charges"}
          name: Work
          type: column
          color: ff8d00
          show:
            legend_value: false
          float_precision: 2
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].work];
            });
        - entity: >-
            ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_charges"}
          name: Payment
          type: column
          color: 00a8ff
          show:
            legend_value: false
          float_precision: 2
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].payment];
            });
        - entity: >-
            ${"sensor.nexxtmove_"+nexxtmove.account+"_charging_device_"+nexxtmove.device_id+"_period_energy"}
          name: Guest
          type: column
          color: d100a0
          show:
            legend_value: false
          float_precision: 2
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].guest];
            });

```

</details>

![Latest charges](https://github.com/geertmeersman/nexxtmove/raw/main/images/screenshots/latest_charges.png)

<details><summary>Show markdown code</summary>

**Replace &lt;username&gt; by your Nexxtmove username**

```
type: markdown
content: >
  |Date/Time|Consumption|Cost|Point ID|Building|

  |----:|----:|----:|----:|----:|

  {% for charge in
  states.sensor.nexxtmove_<username>_recent_charges.attributes.charges -%}

  | {{charge.startTimestamp | as_timestamp | timestamp_custom("%d-%m-%Y
  %H:%M")}} |  {{charge.energyConsumedKWh|round(1)}} KWh | € {{charge.costVat |
  round(2)}} | {{charge.chargingPointName}} | {{charge.buildingName}} |

  {% endfor %}
title: Latest charges

```

</details>

## Screenshots

| Description             | Screenshot                                                                                                                     |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Period Graphs           | ![Period Graphs](https://github.com/geertmeersman/nexxtmove/raw/main/images/screenshots/period_graphs.png)                     |
| Profile                 | ![Profile](https://github.com/geertmeersman/nexxtmove/raw/main/images/screenshots/profile.png)                                 |
| Company                 | ![Company](https://github.com/geertmeersman/nexxtmove/raw/main/images/screenshots/company.png)                                 |
| Nexxtender Mobile Black | ![Nexxtender Mobile Black](https://github.com/geertmeersman/nexxtmove/raw/main/images/screenshots/nexxtender_mobile_black.png) |

## Code origin

The code of this Home Assistant integration has been written by analysing the calls made by the Nexxtmove mobile application to the Nexxtmove.me platform. Goal is to automate as much as possible and to monitor usage.

I have no link with Nexxtmove/Powerdale
