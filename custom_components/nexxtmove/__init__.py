"""Nexxtmove integration."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from requests.exceptions import ConnectionError

from .client import NexxtmoveClient
from .const import (
    API_RATE_LIMIT,
    COORDINATOR_RATE_LIMITED_UPDATE_INTERVAL,
    COORDINATOR_UPDATE_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .exceptions import NexxtmoveException, NexxtmoveServiceException
from .models import NexxtmoveItem

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nexxtmove from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client = NexxtmoveClient(
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
    )

    dev_reg = dr.async_get(hass)
    store = Store(hass, 1, f"{DOMAIN}/{entry.entry_id}/charges")
    hass.data[DOMAIN][entry.entry_id] = coordinator = NexxtmoveDataUpdateCoordinator(
        hass,
        config_entry=entry,
        dev_reg=dev_reg,
        client=client,
        store=store,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove a config entry and clean up stored data."""
    store = Store(hass, 1, f"{DOMAIN}/{entry.entry_id}/charges")
    await store.async_remove()
    _LOGGER.debug(f"Removed charges store for {entry.entry_id}")

    def _cleanup_dir():
        storage_dir = Path(hass.config.path(".storage")) / DOMAIN / entry.entry_id
        if storage_dir.is_dir() and not any(storage_dir.iterdir()):
            storage_dir.rmdir()
        parent = storage_dir.parent
        if parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()

    await hass.async_add_executor_job(_cleanup_dir)


class NexxtmoveDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Nexxtmove."""

    data: list[NexxtmoveItem]
    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        dev_reg: dr.DeviceRegistry,
        client: NexxtmoveClient,
        store: Store,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=COORDINATOR_UPDATE_INTERVAL,
            config_entry=config_entry,
        )
        self._config_entry_id = config_entry.entry_id
        self._device_registry = dev_reg
        self.client = client
        self.hass = hass
        self.store = store
        self.charges_history: dict = {}
        self.last_success_time = None
        _LOGGER.debug("Init")

    async def async_config_entry_first_refresh(self) -> None:
        """Load data, charges history and last_success_time from store before first refresh."""
        stored = await self.store.async_load()
        if stored:
            self.charges_history = stored.get("charges", {})
            last_success = stored.get("last_success_time")
            if last_success:
                self.last_success_time = datetime.fromisoformat(last_success)
            stored_data = stored.get("data", {})
            if stored_data:
                self.data = {
                    key: NexxtmoveItem.from_dict(item)
                    for key, item in stored_data.items()
                }
            _LOGGER.debug(
                f"Loaded {len(self.charges_history)} charges from store, last success: {self.last_success_time}"
            )
        await super().async_config_entry_first_refresh()

    async def _save_store(self) -> None:
        """Save charges, data and last_success_time to store."""
        await self.store.async_save(
            {
                "charges": self.charges_history,
                "last_success_time": (
                    self.last_success_time.isoformat()
                    if self.last_success_time
                    else None
                ),
                "data": {
                    key: item.to_dict() for key, item in (self.data or {}).items()
                },
            }
        )

    async def _merge_charges(self, new_charges: list) -> None:
        """Merge new charges into history, overwriting existing by csid."""
        for charge in new_charges:
            csid = str(charge.get("csid"))
            if csid:
                self.charges_history[csid] = charge
        await self._save_store()
        _LOGGER.debug(
            f"Charges history now contains {len(self.charges_history)} entries"
        )

    async def _async_update_data(self) -> dict | None:
        """Update data."""
        now = datetime.now(timezone.utc)

        if self.last_success_time and self.data:
            last = self.last_success_time
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            if now - last < API_RATE_LIMIT:
                _LOGGER.debug("Skipping update: within rate limit window")
                return self.data
        _LOGGER.debug("Updating")

        try:
            items = await self.hass.async_add_executor_job(
                self.client.fetch_data, self.charges_history
            )
        except ConnectionError as exception:
            raise UpdateFailed(f"ConnectionError {exception}") from exception
        except NexxtmoveServiceException as exception:
            raise UpdateFailed(f"NexxtmoveServiceException {exception}") from exception
        except NexxtmoveException as exception:
            raise UpdateFailed(f"NexxtmoveException {exception}") from exception
        except Exception as exception:
            raise UpdateFailed(f"Exception {exception}") from exception

        if self.client.is_rate_limited:
            _LOGGER.debug("Rate limited, backing off")
            self.client.is_rate_limited = False
            self.update_interval = COORDINATOR_RATE_LIMITED_UPDATE_INTERVAL
        else:
            self.update_interval = COORDINATOR_UPDATE_INTERVAL
            self.last_success_time = datetime.now(timezone.utc)

        items: list[NexxtmoveItem] = items

        if not items:
            _LOGGER.debug("fetch_data returned empty, returning stored data")
            return self.data or {}

        # Merge new charges into persistent history
        self.data = items
        charges_merged = False
        for item in (items or {}).values():
            if item.type == "charges" and isinstance(
                item.extra_attributes.get("charges"), list
            ):
                await self._merge_charges(item.extra_attributes["charges"])
                item.extra_attributes["charges"] = list(self.charges_history.values())
                item.state = len(self.charges_history)
                charges_merged = True
                break

        if not charges_merged:
            await self._save_store()

        current_items = {
            list(device.identifiers)[0][1]
            for device in dr.async_entries_for_config_entry(
                self._device_registry, self._config_entry_id
            )
        }

        if items:
            fetched_items = {str(item.device_key) for item in items.values()}

            if stale_items := current_items - fetched_items:
                for device_key in stale_items:
                    if device := self._device_registry.async_get_device_by_identifier(
                        (DOMAIN, device_key)
                    ):
                        self._device_registry.async_remove_device(device.id)

        return items or {}
