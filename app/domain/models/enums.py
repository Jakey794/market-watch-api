from enum import Enum
from typing import TypeVar

from sqlalchemy import Enum as SAEnum

EnumType = TypeVar("EnumType", bound=Enum)


class AssetType(str, Enum):
    STOCK = "stock"
    ETF = "etf"


class MarketDataInterval(str, Enum):
    FIFTEEN_MINUTES = "15m"
    ONE_DAY = "1d"


class AlertType(str, Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PCT_MOVE_UP_1D = "pct_move_up_1d"
    PCT_MOVE_DOWN_1D = "pct_move_down_1d"


class IngestionRunStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


def string_enum(enum_cls: type[EnumType], *, name: str) -> SAEnum:
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        values_callable=lambda members: [member.value for member in members],
    )