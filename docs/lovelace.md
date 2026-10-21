# Lovelace examples

## Period graphs

![Period Graphs](https://github.com/geertmeersman/nexxtmove/raw/main/images/screenshots/period_graphs.png)

<details><summary>Show markdown code</summary>

**Replace `<username>` by your Nexxtmove username and `<deviceid>` by your Nexxtmove charging device id**

```yaml
type: custom:config-template-card
variables:
  sensor:
    cost: sensor.nexxtmove_<username>_charging_device_<deviceid>_period_cost
    energy: sensor.nexxtmove_<username>_charging_device_<deviceid>_period_energy
    charges: sensor.nexxtmove_<username>_charging_device_<deviceid>_period_charges
entities:
  - ${sensor.cost}
  - ${sensor.energy}
  - ${sensor.charges}
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
        - entity: ${sensor.cost}
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
        - entity: ${sensor.cost}
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
        - entity: ${sensor.cost}
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
        - entity: ${sensor.cost}
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

## Last month period graphs

![Last Month Period Graphs](https://github.com/geertmeersman/nexxtmove/raw/main/images/screenshots/lovelace_past_month_consumption.png)

<details><summary>Show markdown code</summary>

**Replace `<username>` by your Nexxtmove username and `<deviceid>` by your Nexxtmove charging device id**

```yaml
type: custom:config-template-card
variables:
  sensor:
    cost: sensor.nexxtmove_<username>_charging_device_<deviceid>_month_cost
    energy: sensor.nexxtmove_<username>_charging_device_<deviceid>_month_energy
    charges: sensor.nexxtmove_<username>_charging_device_<deviceid>_month_charges
entities:
  - ${sensor.cost}
  - ${sensor.energy}
  - ${sensor.charges}
card:
  type: vertical-stack
  cards:
    - type: custom:apexcharts-card
      graph_span: 1month
      header:
        show: true
        title: ${'Nexxtmove costs for the past month €'}
      series:
        - entity: ${sensor.cost}
          name: Home
          type: column
          color: 73C56C
          data_generator: |
            return entity.attributes.dates.map((day, index) => {
              return [new Date(day), entity.attributes.values[index].home];
            });
```

</details>

## Latest charges table

![Latest charges](https://github.com/geertmeersman/nexxtmove/raw/main/images/screenshots/latest_charges.png)

<details><summary>Show markdown code</summary>

**Replace `<username>` by your Nexxtmove username**

```yaml
type: markdown
content: >
  |Date/Time|Duration|Consumption|Cost|Status|

  |----:|----:|----:|----:|----:|

  {%- set charges = state_attr('sensor.nexxtmove_<username>_recent_charges', 'charges') or [] -%}
  {%- set ns = namespace(total_kwh=0, total_cost=0) -%}
  {%- for charge in charges -%}
    {%- set start_ts = as_timestamp(charge.startTimestamp, default=0) -%}
    {%- set end_ts = as_timestamp(charge.endTimestamp, default=0) -%}
    {%- set cost = charge.costVat | float(default=0) | round(2) -%}
    {%- set duration = end_ts - start_ts -%}
    {%- set hours = (duration // 3600) | int(default=0) -%}
    {%- set minutes = ((duration % 3600) // 60) | int(default=0) -%}
    {%- set kwh = charge.energyConsumedKWh | float(default=0) | round(1) -%}
    {%- set is_cleared = charge.cleared | bool(default=false) -%}
    {%- set status_icon = "✅" if is_cleared else "⏳" -%}
    {%- if not is_cleared -%}
      {%- set ns.total_kwh = ns.total_kwh + kwh -%}
      {%- set ns.total_cost = ns.total_cost + cost -%}
    {%- endif %}
  | {{ start_ts | timestamp_custom("%d-%m %H:%M") }} | {{ hours }}u {{ minutes }}m | {{ kwh }} kWh | € {{ "%.2f" | format(cost) }} | {{ status_icon }} |
  {%- endfor %}
  | **Total (⏳)** | | **{{ ns.total_kwh | round(1) }} kWh** | **€ {{ "%.2f" | format(ns.total_cost) }}** | |
title: Latest charges
```

</details>
