from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


ForecastType = Literal["hourly", "daily"]


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float
    label: str
    country_code: str | None = None


@dataclass(frozen=True)
class ToolResult:
    payload: dict[str, Any]


FALLBACK_CITIES: dict[str, tuple[float, float, str]] = {
    "amsterdam": (52.3676, 4.9041, "NL"),
    "athens": (37.9838, 23.7275, "GR"),
    "barcelona": (41.3874, 2.1686, "ES"),
    "belgrade": (44.7866, 20.4489, "RS"),
    "berlin": (52.52, 13.405, "DE"),
    "bratislava": (48.1486, 17.1077, "SK"),
    "brussels": (50.8503, 4.3517, "BE"),
    "bucharest": (44.4268, 26.1025, "RO"),
    "budapest": (47.4979, 19.0402, "HU"),
    "copenhagen": (55.6761, 12.5683, "DK"),
    "dublin": (53.3498, -6.2603, "IE"),
    "edinburgh": (55.9533, -3.1883, "GB"),
    "geneva": (46.2044, 6.1432, "CH"),
    "hamburg": (53.5511, 9.9937, "DE"),
    "helsinki": (60.1699, 24.9384, "FI"),
    "istanbul": (41.0082, 28.9784, "TR"),
    "kyiv": (50.4501, 30.5234, "UA"),
    "lisbon": (38.7223, -9.1393, "PT"),
    "ljubljana": (46.0569, 14.5058, "SI"),
    "london": (51.5072, -0.1276, "GB"),
    "luxembourg": (49.6116, 6.1319, "LU"),
    "madrid": (40.4168, -3.7038, "ES"),
    "manchester": (53.4808, -2.2426, "GB"),
    "marseille": (43.2965, 5.3698, "FR"),
    "milan": (45.4642, 9.19, "IT"),
    "munich": (48.1351, 11.582, "DE"),
    "naples": (40.8518, 14.2681, "IT"),
    "oslo": (59.9139, 10.7522, "NO"),
    "paris": (48.8566, 2.3522, "FR"),
    "porto": (41.1579, -8.6291, "PT"),
    "prague": (50.0755, 14.4378, "CZ"),
    "reykjavik": (64.1466, -21.9426, "IS"),
    "riga": (56.9496, 24.1052, "LV"),
    "rome": (41.9028, 12.4964, "IT"),
    "sarajevo": (43.8563, 18.4131, "BA"),
    "sofia": (42.6977, 23.3219, "BG"),
    "stockholm": (59.3293, 18.0686, "SE"),
    "tallinn": (59.437, 24.7536, "EE"),
    "tirana": (41.3275, 19.8187, "AL"),
    "valencia": (39.4699, -0.3763, "ES"),
    "vienna": (48.2082, 16.3738, "AT"),
    "vilnius": (54.6872, 25.2797, "LT"),
    "warsaw": (52.2297, 21.0122, "PL"),
    "zagreb": (45.815, 15.9819, "HR"),
    "zurich": (47.3769, 8.5417, "CH"),
}
