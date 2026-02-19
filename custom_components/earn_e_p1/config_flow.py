"""Config flow for the EARN-E P1 Meter integration."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST

from .const import DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

DISCOVERY_TIMEOUT = 10

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


class _DiscoveryProtocol(asyncio.DatagramProtocol):
    """Ephemeral UDP protocol for discovering EARN-E P1 devices on the network."""

    def __init__(self, future: asyncio.Future[dict[str, Any]]) -> None:
        """Initialize the discovery protocol."""
        self.future = future

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Handle incoming UDP datagram during discovery."""
        if self.future.done():
            return
        try:
            payload = json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return
        if not isinstance(payload, dict):
            return
        # Accept packets that look like EARN-E P1 meter data
        if "power_delivered" in payload or "serial" in payload:
            self.future.set_result({"host": addr[0]})


class EarnEP1ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EARN-E P1 Meter."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_host: str | None = None

    async def _async_discover_device(self) -> str | None:
        """Listen for UDP broadcasts and return the IP of the first discovered device."""
        loop = self.hass.loop
        found: asyncio.Future[dict[str, Any]] = loop.create_future()

        transport, _ = await loop.create_datagram_endpoint(
            lambda: _DiscoveryProtocol(found),
            local_addr=("0.0.0.0", DEFAULT_PORT),
            allow_broadcast=True,
        )
        try:
            async with asyncio.timeout(DISCOVERY_TIMEOUT):
                result = await found
                return result["host"]
        except TimeoutError:
            return None
        finally:
            transport.close()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"EARN-E P1 ({user_input[CONF_HOST]})",
                data=user_input,
            )

        # Attempt auto-discovery before showing manual form
        try:
            host = await self._async_discover_device()
        except OSError:
            # Port already in use (e.g. coordinator already listening)
            host = None

        if host:
            self._discovered_host = host
            return await self.async_step_discovery_confirm()

        # Fallback to manual IP entry
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
        )

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm setup of a discovered device."""
        assert self._discovered_host is not None

        if user_input is not None:
            await self.async_set_unique_id(self._discovered_host)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"EARN-E P1 ({self._discovered_host})",
                data={CONF_HOST: self._discovered_host},
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"host": self._discovered_host},
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration."""
        if user_input is None:
            return self.async_show_form(
                step_id="reconfigure",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_HOST,
                            default=self._get_reconfigure_entry().data[CONF_HOST],
                        ): str,
                    }
                ),
            )

        await self.async_set_unique_id(user_input[CONF_HOST])
        self._abort_if_unique_id_configured()

        return self.async_update_reload_and_abort(
            self._get_reconfigure_entry(),
            data_updates=user_input,
        )