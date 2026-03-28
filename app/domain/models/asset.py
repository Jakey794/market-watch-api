from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin
from app.domain.models.enums import AssetType, string_enum

if TYPE_CHECKING:
    from app.domain.models.alert import Alert, AlertEvent
    from app.domain.models.market_data import MarketDataPoint
    from app.domain.models.watchlist import WatchlistItem


class Asset(TimestampMixin, Base):
    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint("symbol", "exchange", name="assets_symbol_exchange"),
        Index("ix_assets_symbol", "symbol"),
        Index("ix_assets_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[AssetType] = mapped_column(
        string_enum(AssetType, name="asset_type_enum"),
        nullable=False,
    )
    exchange: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    watchlist_items: Mapped[list["WatchlistItem"]] = relationship(
        back_populates="asset",
        passive_deletes=True,
    )
    market_data_points: Mapped[list["MarketDataPoint"]] = relationship(
        back_populates="asset",
        passive_deletes=True,
    )
    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="asset",
        passive_deletes=True,
    )
    alert_events: Mapped[list["AlertEvent"]] = relationship(
        back_populates="asset",
        passive_deletes=True,
    )