"""MQTT Media Player component for Home Assistant."""
import logging
import json
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.components.mqtt import (
    CONF_STATE_TOPIC,
    CONF_COMMAND_TOPIC,
    CONF_AVAILABILITY_TOPIC,
    CONF_PAYLOAD_AVAILABLE,
    CONF_PAYLOAD_NOT_AVAILABLE,
    subscription,
)
from homeassistant.const import (
    CONF_NAME,
    CONF_DEVICE_CLASS,
    CONF_DEVICE,
    CONF_IDENTIFIERS,
    CONF_MANUFACTURER,
    CONF_MODEL,
    CONF_SW_VERSION,
    CONF_VIA_DEVICE,
    ATTR_ENTITY_ID,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

_LOGGER = logging.getLogger(__name__)

CONF_UNIQUE_ID = "unique_id"
CONF_DEVICE_INFO = "device_info"

DEFAULT_NAME = "MQTT Media Player"
DEFAULT_DEVICE_CLASS = "speaker"

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
        vol.Optional(CONF_DEVICE_CLASS, default=DEFAULT_DEVICE_CLASS): cv.string,
        vol.Optional(CONF_STATE_TOPIC): cv.string,
        vol.Optional(CONF_COMMAND_TOPIC): cv.string,
        vol.Optional(CONF_AVAILABILITY_TOPIC): cv.string,
        vol.Optional(CONF_PAYLOAD_AVAILABLE, default="online"): cv.string,
        vol.Optional(CONF_PAYLOAD_NOT_AVAILABLE, default="offline"): cv.string,
        vol.Optional(CONF_DEVICE): vol.Schema(
            {
                vol.Optional(CONF_IDENTIFIERS): vol.Any(cv.ensure_list, vol.Coerce(str)),
                vol.Optional(CONF_MANUFACTURER): cv.string,
                vol.Optional(CONF_MODEL): cv.string,
                vol.Optional(CONF_SW_VERSION): cv.string,
                vol.Optional(CONF_VIA_DEVICE): cv.string,
            }
        ),
    }
)

async def async_setup_platform(
    hass: HomeAssistantType, config: ConfigType, async_add_entities, discovery_info=None
):
    """Set up the MQTT Media Player platform."""
    name = config[CONF_NAME]
    unique_id = config.get(CONF_UNIQUE_ID)
    device_class = config[CONF_DEVICE_CLASS]
    state_topic = config.get(CONF_STATE_TOPIC)
    command_topic = config.get(CONF_COMMAND_TOPIC)
    availability_topic = config.get(CONF_AVAILABILITY_TOPIC)
    payload_available = config[CONF_PAYLOAD_AVAILABLE]
    payload_not_available = config[CONF_PAYLOAD_NOT_AVAILABLE]
    device_info = config.get(CONF_DEVICE_INFO, {})

    async_add_entities(
        [
            MQTTMediaPlayer(
                name,
                unique_id,
                device_class,
                state_topic,
                command_topic,
                availability_topic,
                payload_available,
                payload_not_available,
                device_info,
            )
        ]
    )


class MQTTMediaPlayer(MediaPlayerEntity):
    """Representation of an MQTT Media Player."""

    def __init__(
        self,
        name: str,
        unique_id: Optional[str],
        device_class: str,
        state_topic: Optional[str],
        command_topic: Optional[str],
        availability_topic: Optional[str],
        payload_available: str,
        payload_not_available: str,
        device_info: Dict[str, Any],
    ):
        """Initialize the MQTT Media Player."""
        self._name = name
        self._unique_id = unique_id
        self._device_class = device_class
        self._state_topic = state_topic
        self._command_topic = command_topic
        self._availability_topic = availability_topic
        self._payload_available = payload_available
        self._payload_not_available = payload_not_available
        self._device_info = device_info

        self._state = MediaPlayerState.OFF
        self._available = True
        self._volume_level = 0.0
        self._is_volume_muted = False
        self._media_title = None
        self._media_artist = None
        self._media_album = None
        self._media_content_type = None
        self._media_duration = None
        self._media_position = None
        self._media_position_updated_at = None

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> Optional[str]:
        """Return the unique ID of the entity."""
        return self._unique_id

    @property
    def device_class(self) -> str:
        """Return the device class of the entity."""
        return self._device_class

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the entity."""
        return self._state

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def volume_level(self) -> Optional[float]:
        """Volume level of the media player (0..1)."""
        return self._volume_level

    @property
    def is_volume_muted(self) -> Optional[bool]:
        """Boolean if volume is currently muted."""
        return self._is_volume_muted

    @property
    def media_title(self) -> Optional[str]:
        """Title of current playing media."""
        return self._media_title

    @property
    def media_artist(self) -> Optional[str]:
        """Artist of current playing media."""
        return self._media_artist

    @property
    def media_album(self) -> Optional[str]:
        """Album of current playing media."""
        return self._media_album

    @property
    def media_content_type(self) -> Optional[MediaType]:
        """Content type of current playing media."""
        return self._media_content_type

    @property
    def media_duration(self) -> Optional[int]:
        """Duration of current playing media in seconds."""
        return self._media_duration

    @property
    def media_position(self) -> Optional[int]:
        """Position of current playing media in seconds."""
        return self._media_position

    @property
    def media_position_updated_at(self) -> Optional[str]:
        """When was the position of the current playing media valid."""
        return self._media_position_updated_at

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag media player features that are supported."""
        features = (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.PLAY_MEDIA
            | MediaPlayerEntityFeature.SEEK
        )
        return features

    @property
    def device_info(self) -> Optional[DeviceInfo]:
        """Return device info."""
        if not self._device_info:
            return None

        return DeviceInfo(
            identifiers=self._device_info.get(CONF_IDENTIFIERS),
            manufacturer=self._device_info.get(CONF_MANUFACTURER),
            model=self._device_info.get(CONF_MODEL),
            sw_version=self._device_info.get(CONF_SW_VERSION),
            via_device=self._device_info.get(CONF_VIA_DEVICE),
        )

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""
        await super().async_added_to_hass()

        if self._state_topic:
            @callback
            def message_received(msg):
                """Handle new MQTT messages."""
                try:
                    payload = json.loads(msg.payload)
                    self._update_state(payload)
                except (ValueError, TypeError):
                    _LOGGER.warning("Invalid JSON payload received: %s", msg.payload)
                    return

            await subscription.async_subscribe(
                self.hass, self._state_topic, message_received
            )

        if self._availability_topic:
            @callback
            def availability_message_received(msg):
                """Handle new MQTT availability messages."""
                self._available = msg.payload == self._payload_available
                self.async_write_ha_state()

            await subscription.async_subscribe(
                self.hass, self._availability_topic, availability_message_received
            )

    def _update_state(self, payload: Dict[str, Any]):
        """Update the state from MQTT payload."""
        if "state" in payload:
            state_str = payload["state"].lower()
            if state_str == "playing":
                self._state = MediaPlayerState.PLAYING
            elif state_str == "paused":
                self._state = MediaPlayerState.PAUSED
            elif state_str == "stopped":
                self._state = MediaPlayerState.IDLE
            elif state_str == "off":
                self._state = MediaPlayerState.OFF
            else:
                self._state = MediaPlayerState.UNKNOWN

        if "volume" in payload:
            try:
                self._volume_level = float(payload["volume"]) / 100.0
            except (ValueError, TypeError):
                pass

        if "muted" in payload:
            self._is_volume_muted = bool(payload["muted"])

        if "media_title" in payload:
            self._media_title = payload["media_title"]

        if "media_artist" in payload:
            self._media_artist = payload["media_artist"]

        if "media_album" in payload:
            self._media_album = payload["media_album"]

        if "media_content_type" in payload:
            self._media_content_type = payload["media_content_type"]

        if "media_duration" in payload:
            try:
                self._media_duration = int(payload["media_duration"])
            except (ValueError, TypeError):
                pass

        if "media_position" in payload:
            try:
                self._media_position = int(payload["media_position"])
            except (ValueError, TypeError):
                pass

        self.async_write_ha_state()

    async def async_set_volume_level(self, volume: float):
        """Set volume level, range 0..1."""
        if self._command_topic:
            payload = {"volume": int(volume * 100)}
            await self._publish_command(payload)

    async def async_mute_volume(self, mute: bool):
        """Mute the volume."""
        if self._command_topic:
            payload = {"muted": mute}
            await self._publish_command(payload)

    async def async_media_play(self):
        """Send play command."""
        if self._command_topic:
            payload = {"command": "play"}
            await self._publish_command(payload)

    async def async_media_pause(self):
        """Send pause command."""
        if self._command_topic:
            payload = {"command": "pause"}
            await self._publish_command(payload)

    async def async_media_stop(self):
        """Send stop command."""
        if self._command_topic:
            payload = {"command": "stop"}
            await self._publish_command(payload)

    async def async_media_seek(self, position: float):
        """Send seek command."""
        if self._command_topic:
            payload = {"command": "seek", "position": int(position)}
            await self._publish_command(payload)

    async def async_play_media(self, media_type: MediaType, media_id: str, **kwargs):
        """Play a piece of media."""
        if self._command_topic:
            payload = {
                "command": "play_media",
                "media_type": media_type,
                "media_id": media_id,
            }
            await self._publish_command(payload)

    async def _publish_command(self, payload: Dict[str, Any]):
        """Publish command to MQTT topic."""
        if self._command_topic:
            from homeassistant.components.mqtt import publish
            await publish.async_publish(
                self.hass, self._command_topic, json.dumps(payload)
            )