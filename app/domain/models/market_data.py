from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin
from app.domain.models.enums import MarketDataInterval, string_enum

if TYPE_CHECKING:
    from app.domain.models.asset import Asset


class MarketDataPoint(TimestampMixin, Base):
    __tablename__ = "market_data_points"
    __table_args__ = (
        UniqueConstraint(
            "asset_id",
            "interval",
            "timestamp",
            name="market_data_points_asset_id_interval_timestamp",
        ),
        CheckConstraint("volume >= 0", name="volume_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    interval: Mapped[MarketDataInterval] = mapped_column(
        string_enum(MarketDataInterval, name="market_data_interval_enum"),
        nullable=False,
    )
    open: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)

    asset: Mapped["Asset"] = relationship(back_populates="market_data_points")