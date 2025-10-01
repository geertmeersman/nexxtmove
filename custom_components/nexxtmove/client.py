"""Nexxtmove API Client."""

from __future__ import annotations

import copy
from datetime import datetime, timedelta
import logging

from dateutil.relativedelta import relativedelta
from requests import Session

from .const import (
    BASE_HEADERS,
    CONNECTION_RETRY,
    DEFAULT_NEXXTMOVE_ENVIRONMENT,
    MAX_ROWS,
    REQUEST_TIMEOUT,
)
from .exceptions import BadCredentialsException, NexxtmoveServiceException
from .models import NexxtmoveEnvironment, NexxtmoveItem
from .utils import format_entity_name, mask_fields

_LOGGER = logging.getLogger(__name__)


class NexxtmoveClient:
    """Nexxtmove client."""

    session: Session
    environment: NexxtmoveEnvironment

    def __init__(
        self,
        session: Session | None = None,
        username: str | None = None,
        password: str | None = None,
        headers: dict | None = BASE_HEADERS,
        environment: NexxtmoveEnvironment = DEFAULT_NEXXTMOVE_ENVIRONMENT,
    ) -> None:
        """Initialize NexxtmoveClient."""
        self.session = Session()
        self.username = username
        self.password = password
        self.environment = environment
        self._headers = headers
        self.profile = {}
        self.request_error = {}
        self.token = None

    def request(
        self,
        url,
        caller="Not set",
        data=None,
        expected=200,
        log=False,
        retrying=False,
        connection_retry_left=CONNECTION_RETRY,
    ) -> dict | bool:
        """Send a request to Nexxtmove with token and optional retries."""
        if data is None:
            _LOGGER.debug(f"{caller} Calling GET {url}")
            response = self.session.get(
                url,
                timeout=REQUEST_TIMEOUT,
                headers=self._headers | {"Authorize": f"Token {self.token}"},
            )
        else:
            data_copy = copy.deepcopy(data)
            mask_fields(data_copy, ["password"])
            _LOGGER.debug(f"{caller} Calling POST {url} with {data_copy}")
            response = self.session.post(
                url,
                json=data,
                timeout=REQUEST_TIMEOUT,
                headers=self._headers | {"Authorize": f"Token {self.token}"},
            )

        _LOGGER.debug(
            f"{caller} http status code = {response.status_code} (expecting {expected})"
        )

        if log:
            _LOGGER.debug(f"{caller} Response:\n{response.text}")

        if expected is not None and response.status_code != expected:
            if response.status_code in (404, 406, 400):
                self.request_error = response.json() if response.content else {}
                return False

            if 500 <= response.status_code < 600:
                return False

            if (
                response.status_code in (401, 403)
                and connection_retry_left > 0
                and not retrying
            ):
                _LOGGER.debug("[request] Token expired, retrying login...")
                self.token = None
                self.login()
                return self.request(
                    url, caller, data, expected, log, True, connection_retry_left - 1
                )

            raise NexxtmoveServiceException(
                f"[{caller}] Expecting HTTP {expected} | "
                f"Response HTTP {response.status_code}, "
                f"Response: {response.text}, Url: {response.url}"
            )

        return response

    def login(self) -> dict | bool:
        """Authenticate and get a session token."""
        _LOGGER.debug("[login|start]")

        if self.token is not None:
            return self.profile

        if self.username is None or self.password is None:
            return False

        response = self.request(
            f"{self.environment.api_endpoint}/user/authenticate",
            "[login|authenticate]",
            {"username": self.username, "password": self.password},
            200,
        )

        if response is False:
            return False

        result = response.json()
        try:
            self.token = result.get("authToken")
            self.profile = result.get("profile")
        except Exception as exception:
            raise BadCredentialsException(
                f"HTTP {response.status_code} authToken {exception}"
            )

        return self.profile

    def fetch_data(self) -> dict:
        """Fetch all Nexxtmove data for the account."""
        data: dict = {}
        self.login()
        company = self.company()

        device_key = format_entity_name(f"{self.username} company")
        device_name = company.get("name")
        device_model = company.get("type")

        # Company info
        key = format_entity_name(f"{self.username} company")
        data[key] = NexxtmoveItem(
            name=device_name,
            key=key,
            type="company",
            sensor_type="sensor",
            device_key=device_key,
            device_name=device_name,
            device_model=device_model,
            state=company.get("type"),
            extra_attributes=company,
        )

        # Work locations
        buildings = self.work_buildings()
        for location in buildings.get("locations", []):
            key = format_entity_name(
                f"{self.username} work location {location.get('id')}"
            )
            data[key] = NexxtmoveItem(
                name=location.get("name"),
                key=key,
                type="work_location",
                sensor_type="sensor",
                device_key=device_key,
                device_name=device_name,
                device_model=device_model,
                state=location.get("city"),
                extra_attributes=location,
            )

        # Profile info
        device_key = format_entity_name(f"{self.username} account")
        device_name = f"Profile {self.username}"
        device_model = "Profile"
        key = format_entity_name(f"{self.username} profile")
        data[key] = NexxtmoveItem(
            name="Profile",
            key=key,
            type="profile",
            sensor_type="sensor",
            device_key=device_key,
            device_name=device_name,
            device_model=device_model,
            state=self.profile.get("username"),
            extra_attributes=self.profile,
        )

        # Charges
        charge_latest = self.charge_latest()
        if charge_latest and charge_latest.get("charges"):
            key = format_entity_name(f"{self.username} recent charges")
            data[key] = NexxtmoveItem(
                name="Recent charges",
                key=key,
                type="charges",
                sensor_type="sensor",
                device_key=device_key,
                device_name=device_name,
                device_model=device_model,
                state=len(charge_latest.get("charges")),
                extra_attributes=charge_latest,
            )

            # Non invoiced
            non_invoiced_charges = []
            non_invoiced_amount = 0
            for charge in charge_latest.get("charges"):
                if charge.get("cleared") is False:
                    non_invoiced_charges.append(charge)
                    cost = charge.get("costVat")
                    if isinstance(cost, int | float):
                        non_invoiced_amount += cost
            key = format_entity_name(f"{self.username} non invoiced")
            data[key] = NexxtmoveItem(
                name="Non invoiced",
                key=key,
                type="euro",
                sensor_type="sensor",
                device_key=device_key,
                device_name=device_name,
                device_model=device_model,
                state=non_invoiced_amount,
                extra_attributes={"charges": non_invoiced_charges},
            )

        # Consumption
        consumption = self.consumption()
        if consumption.get("consumptionInKwh") is not None:
            charges = self.charges() or {}
            key = format_entity_name(f"{self.username} consumption")
            data[key] = NexxtmoveItem(
                name="Consumption",
                key=key,
                type="consumptionTotal",
                sensor_type="sensor",
                device_key=device_key,
                device_name=device_name,
                device_model=device_model,
                state=consumption.get("consumptionInKwh"),
                extra_attributes=charges,
            )

        # Residential buildings
        buildings = self.residential_buildings()
        for location in buildings.get("locations", []):
            key = format_entity_name(
                f"{self.username} residential location {location.get('id')}"
            )
            data[key] = NexxtmoveItem(
                name=location.get("name"),
                key=key,
                type="residential_location",
                sensor_type="sensor",
                device_key=device_key,
                device_name=device_name,
                device_model=device_model,
                state=location.get("city"),
                extra_attributes=location,
            )

        # Charging devices
        device_list = self.device_list()
        for charging_device in device_list.get("chargingDevices", []):
            self._fetch_charging_device_data(charging_device, data)

        return data

    # ------------------------
    # Charging device helpers
    # ------------------------
    def _fetch_charging_device_data(self, charging_device: dict, data: dict) -> None:
        """Fetch all data related to a single charging device."""
        device_id = charging_device.get("id")
        device_key = format_entity_name(f"{self.username} charging device {device_id}")
        device_name = charging_device.get("name")
        device_model = charging_device.get("type")

        # Device info
        data[device_key] = NexxtmoveItem(
            name=device_name,
            key=device_key,
            type="charging_device",
            sensor_type="sensor",
            device_key=device_key,
            device_name=device_name,
            device_model=device_model,
            state=charging_device.get("buildingName"),
            extra_attributes=charging_device,
        )

        # Period & monthly graphs
        self._fetch_charging_graphs(charging_device, data, device_key)

        # Device PIN
        pin = self.device_pin(device_id)
        if pin:
            key = format_entity_name(f"{self.username} charging device {device_id} pin")
            data[key] = NexxtmoveItem(
                name=f"{device_name} PIN",
                key=key,
                type="charging_device_pin",
                sensor_type="sensor",
                device_key=device_key,
                device_name=device_name,
                device_model=device_model,
                state=pin.get("pin"),
            )

        # Device events
        events = self.device_events(device_id)
        if events and events.get("events"):
            key = format_entity_name(
                f"{self.username} charging device {device_id} events"
            )
            data[key] = NexxtmoveItem(
                name=f"{device_name} events",
                key=key,
                type="charging_events",
                sensor_type="sensor",
                device_key=device_key,
                device_name=device_name,
                device_model=device_model,
                state=len(events.get("events")),
                extra_attributes=events,
            )

        # Charging points
        for charging_point_info in charging_device.get("chargingPoints", []):
            self._fetch_charging_point_data(charging_point_info, device_key, data)

    def _fetch_charging_graphs(
        self, charging_device: dict, data: dict, device_key: str
    ) -> None:
        """Fetch period and monthly graph data for a charging device."""
        device_id = charging_device.get("id")
        end_date = datetime.now().strftime("%Y%m%d")
        start_date_period = (
            (datetime.now().replace(day=1) - timedelta(days=datetime.now().day))
            .replace(day=1)
            .strftime("%Y%m%d")
        )
        start_date_month = (
            datetime.now() - relativedelta(months=1) + relativedelta(days=1)
        ).strftime("%Y%m%d")

        for period_name, start_date in [
            ("period", start_date_period),
            ("month", start_date_month),
        ]:
            extra_attributes = {"start_date": start_date, "end_date": end_date}
            graph_data = self.charging_device_graph(device_id, start_date, end_date)
            if not graph_data:
                continue

            totals = graph_data.get("totals", {})
            records = graph_data.get("records", [])

            # Totals
            for suffix, key_value in [
                ("reimbursed", totals.get("totalReimbursed", 0)),
                ("cost", totals.get("totalCost", 0)),
                ("energy", totals.get("totalEnergyWh", 0)),
            ]:
                key = format_entity_name(
                    f"{self.username} charging device {device_id} {period_name} {suffix}"
                )
                value = key_value
                if suffix == "energy":
                    value = value / 1000  # Wh → kWh
                data[key] = NexxtmoveItem(
                    name=f"{charging_device.get('name')} {period_name} {suffix}",
                    key=key,
                    type="euro" if suffix != "energy" else "consumption",
                    sensor_type="sensor",
                    device_key=device_key,
                    device_name=charging_device.get("name"),
                    device_model=charging_device.get("type"),
                    state=value,
                    extra_attributes=extra_attributes,
                )

            # Detailed per-category
            monthly_date, monthly_cost, monthly_energy, monthly_charges = [], [], [], []
            period_charges = 0
            for record in records:
                monthly_date.append(record.get("date"))
                cost, energy, charges = {}, {}, {}
                for category in ["home", "payment", "guest", "work"]:
                    details = record.get("detailsPerAccount", {}).get(
                        category.upper(), {}
                    )
                    cost[category] = details.get("cost")
                    energy[category] = details.get("energyWh")
                    charges[category] = details.get("charges")
                    period_charges += details.get("charges", 0)
                monthly_cost.append(cost)
                monthly_energy.append(energy)
                monthly_charges.append(charges)

            # Store per-category counters
            for suffix, values in [
                ("cost", monthly_cost),
                ("energy", monthly_energy),
                ("charges", monthly_charges),
            ]:
                key = format_entity_name(
                    f"{self.username} charging device {device_id} {period_name} {suffix}"
                )
                state_value = period_charges if suffix == "charges" else None
                if suffix == "energy":
                    state_value = (
                        sum([sum(e.values()) for e in monthly_energy]) / 1000
                    )  # Wh → kWh
                elif suffix == "cost":
                    state_value = sum([sum(c.values()) for c in monthly_cost])
                data[key] = NexxtmoveItem(
                    name=f"{charging_device.get('name')} {period_name} {suffix}",
                    key=key,
                    type=(
                        "euro"
                        if suffix != "energy"
                        else "consumption" if suffix == "energy" else "counter"
                    ),
                    sensor_type="sensor",
                    device_key=device_key,
                    device_name=charging_device.get("name"),
                    device_model=charging_device.get("type"),
                    state=state_value,
                    extra_attributes=extra_attributes
                    | {"dates": monthly_date, "values": values},
                )

    def _fetch_charging_point_data(
        self, charging_point_info: dict, device_key: str, data: dict
    ) -> None:
        """Fetch info and events for a single charging point."""
        cp_id = charging_point_info.get("id")
        charging_point = self.charging_point(cp_id)
        if not charging_point:
            return
        key = format_entity_name(f"{self.username} charging point {cp_id}")
        data[key] = NexxtmoveItem(
            name=charging_point.get("name"),
            key=key,
            type="charging_point",
            sensor_type="sensor",
            device_key=device_key,
            device_name=charging_point.get("name"),
            device_model=charging_point.get("type"),
            state=charging_point.get("status"),
            extra_attributes=charging_point,
        )

        # Price info
        price = charging_point.get("price")
        if price:
            price_info = price.split(" ")
            key = format_entity_name(f"{self.username} charging point {cp_id} price")
            data[key] = NexxtmoveItem(
                name=f"{charging_point.get('name')} price",
                key=key,
                type="pricekwh",
                sensor_type="sensor",
                device_key=device_key,
                device_name=charging_point.get("name"),
                device_model=charging_point.get("type"),
                state=price_info[0],
                native_unit_of_measurement=self.price_to_ISO4217(price_info[1]),
            )

        # Events
        events = self.charging_point_events(cp_id)
        if events and events.get("events"):
            key = format_entity_name(f"{self.username} charging point {cp_id} events")
            data[key] = NexxtmoveItem(
                name=f"{charging_point.get('name')} events",
                key=key,
                type="charging_events",
                sensor_type="sensor",
                device_key=device_key,
                device_name=charging_point.get("name"),
                device_model=charging_point.get("type"),
                state=len(events.get("events")),
                extra_attributes=events,
            )

    # ------------------------
    # Utility functions
    # ------------------------
    def price_to_ISO4217(self, unit: str) -> str:
        """Convert price info to ISO4217."""
        return unit.replace("€", "EUR")

    def company(self) -> dict | bool:
        """Fetch Company info."""
        _LOGGER.debug("[company] Fetching company info from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/company",
            "[company]",
            None,
            200,
        )
        return response.json() if response else False

    def device_list(self) -> dict | bool:
        """Fetch Device list."""
        _LOGGER.debug("[device_list] Fetching device list from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/device/list",
            "[device_list]",
            None,
            200,
        )
        return response.json() if response else False

    def device_events(self, device_id: str) -> dict | bool:
        """Fetch Device events."""
        _LOGGER.debug("[device_events] Fetching device events from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/device/{device_id}/events",
            "[device_events]",
            None,
            200,
        )
        return response.json() if response else False

    def device_pin(self, device_id: str) -> dict | bool:
        """Fetch Device PIN."""
        _LOGGER.debug("[device_pin] Fetching device pin from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/device/{device_id}/pin",
            "[device_pin]",
            None,
            200,
        )
        return response.json() if response else False

    def charging_device_tokens(self, device_id: str) -> dict | bool:
        """Fetch Device tokens."""
        _LOGGER.debug("[charging_device_tokens] Fetching device tokens from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/charging-device-token/list?chargingDeviceId={device_id}",
            "[charging_device_tokens]",
            None,
            200,
        )
        return response.json() if response else False

    def charging_device_graph(
        self, device_id: str, start_date: str, end_date: str
    ) -> dict | bool:
        """Fetch Charging graph data."""
        _LOGGER.debug(
            "[charging_device_graph] Fetching charging graph data from Nexxtmove"
        )
        response = self.request(
            f"{self.environment.api_endpoint}/graph/graph/{device_id}?startDate={start_date}&endDate={end_date}",
            "[charging_device_graph]",
            None,
            200,
        )
        return response.json() if response else False

    def charging_point(self, charging_point_id: str) -> dict | bool:
        """Fetch Charging point info."""
        _LOGGER.debug("[charging_point] Fetching charging point info from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/point/{charging_point_id}",
            "[charging_point]",
            None,
            200,
        )
        return response.json() if response else False

    def charging_point_events(self, device_id: str) -> dict | bool:
        """Fetch charging point events."""
        _LOGGER.debug(
            "[charging_point_events] Fetching charging point events from Nexxtmove"
        )
        response = self.request(
            f"{self.environment.api_endpoint}/point/{device_id}/events",
            "[charging_point_events]",
            None,
            200,
        )
        return response.json() if response else False

    def charge_latest(self) -> dict:
        """Fetch latest charges."""
        _LOGGER.debug("[charge_latest] Fetching charges from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/charge/latest?maxRows={MAX_ROWS}&offset=0",
            "[charge_latest]",
            None,
            200,
        )
        return response.json() if response else {}

    def consumption(self) -> dict | bool:
        """Fetch consumption."""
        _LOGGER.debug("[consumption] Fetching consumption from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/charge/consumption",
            "[consumption]",
            None,
            200,
        )
        return response.json() if response else False

    def charges(self) -> dict | bool:
        """Fetch current charges."""
        _LOGGER.debug("[charges] Fetching charges from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/charge/current?maxRows={MAX_ROWS}&offset=0",
            "[charges]",
            None,
            200,
        )
        return response.json() if response else False

    def residential_buildings(self) -> dict | bool:
        """Fetch residential buildings."""
        _LOGGER.debug(
            "[residential_buildings] Fetching residential buildings from Nexxtmove"
        )
        response = self.request(
            f"{self.environment.api_endpoint}/building/residential?maxRows={MAX_ROWS}&offset=0",
            "[residential_buildings]",
            None,
            200,
        )
        return response.json() if response else False

    def work_buildings(self) -> dict | bool:
        """Fetch work buildings."""
        _LOGGER.debug("[work_buildings] Fetching work buildings from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/building/list/work?maxRows={MAX_ROWS}&offset=0",
            "[work_buildings]",
            None,
            200,
        )
        return response.json() if response else False
