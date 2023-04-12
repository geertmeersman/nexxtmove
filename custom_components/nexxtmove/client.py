"""Nexxtmove API Client."""
from __future__ import annotations

from requests import (
    Session,
)

from .const import BASE_HEADERS
from .const import CONNECTION_RETRY
from .const import DEFAULT_NEXXTMOVE_ENVIRONMENT
from .const import REQUEST_TIMEOUT
from .exceptions import BadCredentialsException
from .exceptions import NexxtmoveServiceException
from .models import NexxtmoveEnvironment
from .models import NexxtmoveItem
from .utils import format_entity_name
from .utils import log_debug


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
        self.session = session if session else Session()
        self.username = username
        self.password = password
        self.environment = environment
        self.session.headers = headers
        self.profile = {}
        self.request_error = {}
        self.token = None

    def request(
        self,
        url,
        caller="Not set",
        data=None,
        expected="200",
        log=False,
        retrying=False,
        connection_retry_left=CONNECTION_RETRY,
    ) -> dict:
        """Send a request to Nexxtmove."""
        if data is None:
            log_debug(f"{caller} Calling GET {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
        else:
            log_debug(f"{caller} Calling POST {url} with {data}")
            response = self.session.post(url, json=data, timeout=REQUEST_TIMEOUT)
        log_debug(
            f"{caller} http status code = {response.status_code} (expecting {expected})"
        )
        if log:
            log_debug(f"{caller} Response:\n{response.text}")
        if expected is not None and response.status_code != expected:
            if response.status_code == 404:
                self.request_error = response.json()
                return False
            if (
                response.status_code != 403
                and response.status_code != 401
                and response.status_code != 500
                and connection_retry_left > 0
                and not retrying
            ):
                raise NexxtmoveServiceException(
                    f"[{caller}] Expecting HTTP {expected} | Response HTTP {response.status_code}, Response: {response.text}, Url: {response.url}"
                )
            log_debug(
                f"[NexxtmoveClient|request] Received a HTTP {response.status_code}, nothing to worry about! We give it another try :-)"
            )
            self.login()
            response = self.request(
                url, caller, data, expected, log, True, connection_retry_left - 1
            )
        return response

    def login(self) -> dict:
        """Start a new Nexxtmove session with a user & password."""

        log_debug("[NexxtmoveClient|login|start]")
        """Login process"""
        if self.username is None or self.password is None:
            return False
        response = self.request(
            f"{self.environment.api_endpoint}/user/authenticate",
            "[NexxtmoveClient|login|authenticate]",
            {"username": self.username, "password": self.password},
            200,
        )
        result = response.json()
        try:
            self.token = result.get("authToken")
            self.session.headers |= {"Authorize": f"Token {self.token}"}
            self.profile = result.get("profile")
        except Exception as exception:
            raise BadCredentialsException(
                f"HTTP {response.status_code} authToken {exception}"
            )
        return self.profile

    def fetch_data(self):
        """Fetch Nexxtmove data."""
        data = {}
        self.login()
        company = self.company()

        device_key = format_entity_name(f"{self.username} company")
        device_name = company.get("name")
        device_model = company.get("type")

        key = format_entity_name(f"{self.username} company")
        data[key] = NexxtmoveItem(
            name=company.get("name"),
            key=key,
            type="company",
            sensor_type="sensor",
            device_key=device_key,
            device_name=device_name,
            device_model=device_model,
            state=company.get("type"),
            extra_attributes=company,
        )
        buildings = self.work_buildings()
        if buildings.get("locations") and len(buildings.get("locations")):
            for location in buildings.get("locations"):
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
        charge_latest = self.charge_latest()
        if charge_latest.get("charges") and len(charge_latest.get("charges")):
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
        consumption = self.consumption()
        if consumption.get("consumptionInKwh") is not None:
            key = format_entity_name(f"{self.username} consumption")
            data[key] = NexxtmoveItem(
                name="Consumption",
                key=key,
                type="consumption",
                sensor_type="sensor",
                device_key=device_key,
                device_name=device_name,
                device_model=device_model,
                state=consumption.get("consumptionInKwh"),
            )
        buildings = self.residential_buildings()
        if buildings.get("locations") and len(buildings.get("locations")):
            for location in buildings.get("locations"):
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

        device_list = self.device_list()
        for charging_device in device_list.get("chargingDevices"):
            key = format_entity_name(
                f"{self.username} charging device {charging_device.get('id')}"
            )
            device_key = key
            device_name = charging_device.get("name")
            device_model = charging_device.get("type")
            data[key] = NexxtmoveItem(
                name=charging_device.get("name"),
                key=key,
                type="charging_device",
                sensor_type="sensor",
                device_key=device_key,
                device_name=device_name,
                device_model=device_model,
                state=charging_device.get("buildingName"),
                extra_attributes=charging_device,
            )

            """
            #Switch will be used when it becomes useful
            key = format_entity_name(
                f"{self.username} charging device {charging_device.get('id')} switch"
            )
            data[key] = NexxtmoveItem(
                name=charging_device.get("name"),
                key=key,
                type="charging_device",
                sensor_type="switch",
                device_key=device_key,
                device_name=device_name,
                device_model=device_model,
                state=False,
            )
            """

            pin = self.device_pin(charging_device.get("id"))
            key = format_entity_name(
                f"{self.username} charging device {charging_device.get('id')} pin"
            )
            data[key] = NexxtmoveItem(
                name=f"{charging_device.get('name')} PIN",
                key=key,
                type="charging_device_pin",
                sensor_type="sensor",
                device_key=device_key,
                device_name=device_name,
                device_model=device_model,
                state=pin.get("pin"),
            )

            events = self.device_events(charging_device.get("id"))
            if events.get("events") and len(events.get("events")):
                key = format_entity_name(
                    f"{self.username} charging device {charging_device.get('id')} events"
                )
                data[key] = NexxtmoveItem(
                    name=f"{charging_device.get('name')} events",
                    key=key,
                    type="charging_events",
                    sensor_type="sensor",
                    device_key=device_key,
                    device_name=device_name,
                    device_model=device_model,
                    state=len(events.get("events")),
                    extra_attributes=events,
                )

            if len(charging_device.get("chargingPoints")):
                for charging_point in charging_device.get("chargingPoints"):
                    id = charging_point.get("id")
                    charging_point = self.charging_point(id)
                    key = format_entity_name(f"{self.username} charging point {id}")
                    data[key] = NexxtmoveItem(
                        name=charging_point.get("name"),
                        key=key,
                        type="charging_point",
                        sensor_type="sensor",
                        device_key=device_key,
                        device_name=device_name,
                        device_model=device_model,
                        state=charging_point.get("status"),
                        extra_attributes=charging_point,
                    )
                    events = self.charging_point_events(id)
                    if events.get("events") and len(events.get("events")):
                        key = format_entity_name(
                            f"{self.username} charging point {id} events"
                        )
                        data[key] = NexxtmoveItem(
                            name=f"{charging_point.get('name')} events",
                            key=key,
                            type="charging_events",
                            sensor_type="sensor",
                            device_key=device_key,
                            device_name=device_name,
                            device_model=device_model,
                            state=len(events.get("events")),
                            extra_attributes=events,
                        )
        return data

    def company(self):
        """Fetch Company info."""
        log_debug("[NexxtmoveClient|company] Fetching company info from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/company",
            "[NexxtmoveClient|company]",
            None,
            200,
        )
        if response is False:
            return False
        return response.json()

    def device_list(self):
        """Fetch Device list."""
        log_debug("[NexxtmoveClient|device_list] Fetching device list from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/device/list",
            "[NexxtmoveClient|device_list]",
            None,
            200,
        )
        if response is False:
            return False
        return response.json()

    def device_events(self, device_id):
        """Fetch Device events."""
        log_debug(
            "[NexxtmoveClient|device_events] Fetching device events from Nexxtmove"
        )
        response = self.request(
            f"{self.environment.api_endpoint}/device/{device_id}/events",
            "[NexxtmoveClient|device_events]",
            None,
            200,
        )
        if response is False:
            return False
        return response.json()

    def device_pin(self, device_id):
        """Fetch Device pin."""
        log_debug("[NexxtmoveClient|device_pin] Fetching device pin from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/device/{device_id}/pin",
            "[NexxtmoveClient|device_pin]",
            None,
            200,
        )
        if response is False:
            return False
        return response.json()

    def charging_point(self, charging_point_id):
        """Fetch Charging point info."""
        log_debug(
            "[NexxtmoveClient|charging_point] Fetching charging point info from Nexxtmove"
        )
        response = self.request(
            f"{self.environment.api_endpoint}/point/{charging_point_id}",
            "[NexxtmoveClient|charging_point]",
            None,
            200,
        )
        if response is False:
            return False
        return response.json()

    def charging_point_events(self, device_id):
        """Fetch charging point events."""
        log_debug(
            "[NexxtmoveClient|charging_point_events] Fetching charging point events from Nexxtmove"
        )
        response = self.request(
            f"{self.environment.api_endpoint}/point/{device_id}/events",
            "[NexxtmoveClient|charging_point_events]",
            None,
            200,
        )
        if response is False:
            return False
        return response.json()

    def charge_latest(self):
        """Fetch charges."""
        log_debug("[NexxtmoveClient|charge_latest] Fetching charges from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/charge/latest?maxRows=20&offset=0",
            "[NexxtmoveClient|charge_latest]",
            None,
            200,
        )
        if response is False:
            return False
        return response.json()

    def consumption(self):
        """Fetch consumption."""
        log_debug("[NexxtmoveClient|consumption] Fetching consumption from Nexxtmove")
        response = self.request(
            f"{self.environment.api_endpoint}/charge/consumption",
            "[NexxtmoveClient|consumption]",
            None,
            200,
        )
        if response is False:
            return False
        return response.json()

    def residential_buildings(self):
        """Fetch residential buildings."""
        log_debug(
            "[NexxtmoveClient|residential_buildings] Fetching residential buildings from Nexxtmove"
        )
        response = self.request(
            f"{self.environment.api_endpoint}/building/residential?maxRows=20&offset=0",
            "[NexxtmoveClient|residential_buildings]",
            None,
            200,
        )
        if response is False:
            return False
        return response.json()

    def work_buildings(self):
        """Fetch work buildings."""
        log_debug(
            "[NexxtmoveClient|work_buildings] Fetching work buildings from Nexxtmove"
        )
        response = self.request(
            f"{self.environment.api_endpoint}/building/list/work?maxRows=20&offset=0",
            "[NexxtmoveClient|work_buildings]",
            None,
            200,
        )
        if response is False:
            return False
        return response.json()
