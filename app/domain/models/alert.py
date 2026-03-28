from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import AuditTimestampMixin, Base
from app.domain.models.enums import AlertType, string_enum

if TYPE_CHECKING:
    from app.domain.models.asset import Asset
    from app.domain.models.user import User


class Alert(AuditTimestampMixin, Base):
    __tablename__ = "alerts"
    __table_args__ = (
        CheckConstraint(
            """
            (
                alert_type IN ('price_above', 'price_below')
                AND threshold_value IS NOT NULL
                AND percent_value IS NULL
            )
            OR
            (
                alert_type IN ('pct_move_up_1d', 'pct_move_down_1d')
                AND percent_value IS NOT NULL
                AND threshold_value IS NULL
            )
            """,
            name="value_fields_match_type",
        ),
        CheckConstraint("cooldown_minutes >= 0", name="cooldown_minutes_non_negative"),
        CheckConstraint(
            "threshold_value IS NULL OR threshold_value > 0",
            name="threshold_value_positive",
        ),
        CheckConstraint(
            "percent_value IS NULL OR percent_value > 0",
            name="percent_value_positive",
        ),
        Index("ix_alerts_user_id_is_active", "user_id", "is_active"),
        Index("ix_alerts_asset_id_is_active", "asset_id", "is_active"),
        Index(
            "uq_alerts_active_price_rule",
            "user_id",
            "asset_id",
            "alert_type",
            "threshold_value",
            unique=True,
            postgresql_where=text("is_active AND threshold_value IS NOT NULL"),
        ),
        Index(
            "uq_alerts_active_percent_rule",
            "user_id",
            "asset_id",
            "alert_type",
            "percent_value",
            unique=True,
            postgresql_where=text("is_active AND percent_value IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
    )
    alert_type: Mapped[AlertType] = mapped_column(
        string_enum(AlertType, name="alert_type_enum"),
        nullable=False,
    )
    threshold_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    percent_value: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    cooldown_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=60,
        server_default="60",
    )
    last_triggered_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(back_populates="alerts")
    asset: Mapped["Asset"] = relationship(back_populates="alerts")
    alert_events: Mapped[list["AlertEvent"]] = relationship(
        back_populates="alert",
        passive_deletes=True,
    )


class AlertEvent(Base):
    __tablename__ = "alert_events"
    __table_args__ = (
        Index("ix_alert_events_user_id_triggered_at", "user_id", "triggered_at"),
        Index("ix_alert_events_asset_id_triggered_at", "asset_id", "triggered_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_id: Mapped[int | None] = mapped_column(
        ForeignKey("alerts.id", ondelete="SET NULL"),
        nullable=True,
    )
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    triggered_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    observed_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    event_payload_json: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    alert: Mapped["Alert | None"] = relationship(back_populates="alert_events")
    asset: Mapped["Asset"] = relationship(back_populates="alert_events")
    user: Mapped["User"] = relationship(back_populates="alert_events")