"""create v1 schema

Revision ID: 0002_step4_create_v1_schema
Revises: 0001_step3_bootstrap
Create Date: 2026-03-27 00:00:01
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002_step4_create_v1_schema"
down_revision: str | None = "0001_step3_bootstrap"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

asset_type_enum = sa.Enum(
    "stock",
    "etf",
    name="asset_type_enum",
    native_enum=False,
    create_constraint=True,
)

market_data_interval_enum = sa.Enum(
    "15m",
    "1d",
    name="market_data_interval_enum",
    native_enum=False,
    create_constraint=True,
)

alert_type_enum = sa.Enum(
    "price_above",
    "price_below",
    "pct_move_up_1d",
    "pct_move_down_1d",
    name="alert_type_enum",
    native_enum=False,
    create_constraint=True,
)

ingestion_run_status_enum = sa.Enum(
    "running",
    "succeeded",
    "failed",
    name="ingestion_run_status_enum",
    native_enum=False,
    create_constraint=True,
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("asset_type", asset_type_enum, nullable=False),
        sa.Column("exchange", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("symbol", "exchange", name="uq_assets_symbol_exchange"),
    )
    op.create_index("ix_assets_symbol", "assets", ["symbol"], unique=False)
    op.create_index("ix_assets_is_active", "assets", ["is_active"], unique=False)

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "started_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("finished_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "status",
            ingestion_run_status_enum,
            nullable=False,
            server_default=sa.text("'running'"),
        ),
        sa.Column(
            "records_written",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "records_written >= 0",
            name="ck_ingestion_runs_records_written_non_negative",
        ),
    )
    op.create_index("ix_ingestion_runs_started_at", "ingestion_runs", ["started_at"], unique=False)

    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_watchlists_user_id_users"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("user_id", "name", name="uq_watchlists_user_id_name"),
    )

    op.create_table(
        "market_data_points",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "asset_id",
            sa.Integer(),
            sa.ForeignKey("assets.id", ondelete="RESTRICT", name="fk_market_data_points_asset_id_assets"),
            nullable=False,
        ),
        sa.Column("timestamp", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("interval", market_data_interval_enum, nullable=False),
        sa.Column("open", sa.Numeric(18, 6), nullable=False),
        sa.Column("high", sa.Numeric(18, 6), nullable=False),
        sa.Column("low", sa.Numeric(18, 6), nullable=False),
        sa.Column("close", sa.Numeric(18, 6), nullable=False),
        sa.Column("volume", sa.BigInteger(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "volume >= 0",
            name="ck_market_data_points_volume_non_negative",
        ),
        sa.UniqueConstraint(
            "asset_id",
            "interval",
            "timestamp",
            name="uq_market_data_points_asset_id_interval_timestamp",
        ),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_alerts_user_id_users"),
            nullable=False,
        ),
        sa.Column(
            "asset_id",
            sa.Integer(),
            sa.ForeignKey("assets.id", ondelete="RESTRICT", name="fk_alerts_asset_id_assets"),
            nullable=False,
        ),
        sa.Column("alert_type", alert_type_enum, nullable=False),
        sa.Column("threshold_value", sa.Numeric(18, 6), nullable=True),
        sa.Column("percent_value", sa.Numeric(8, 4), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "cooldown_minutes",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("60"),
        ),
        sa.Column("last_triggered_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
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
            name="ck_alerts_value_fields_match_type",
        ),
        sa.CheckConstraint(
            "cooldown_minutes >= 0",
            name="ck_alerts_cooldown_minutes_non_negative",
        ),
        sa.CheckConstraint(
            "threshold_value IS NULL OR threshold_value > 0",
            name="ck_alerts_threshold_value_positive",
        ),
        sa.CheckConstraint(
            "percent_value IS NULL OR percent_value > 0",
            name="ck_alerts_percent_value_positive",
        ),
    )
    op.create_index("ix_alerts_user_id_is_active", "alerts", ["user_id", "is_active"], unique=False)
    op.create_index("ix_alerts_asset_id_is_active", "alerts", ["asset_id", "is_active"], unique=False)
    op.create_index(
        "uq_alerts_active_price_rule",
        "alerts",
        ["user_id", "asset_id", "alert_type", "threshold_value"],
        unique=True,
        postgresql_where=sa.text("is_active AND threshold_value IS NOT NULL"),
    )
    op.create_index(
        "uq_alerts_active_percent_rule",
        "alerts",
        ["user_id", "asset_id", "alert_type", "percent_value"],
        unique=True,
        postgresql_where=sa.text("is_active AND percent_value IS NOT NULL"),
    )

    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "watchlist_id",
            sa.Integer(),
            sa.ForeignKey(
                "watchlists.id",
                ondelete="CASCADE",
                name="fk_watchlist_items_watchlist_id_watchlists",
            ),
            nullable=False,
        ),
        sa.Column(
            "asset_id",
            sa.Integer(),
            sa.ForeignKey("assets.id", ondelete="RESTRICT", name="fk_watchlist_items_asset_id_assets"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("watchlist_id", "asset_id", name="uq_watchlist_items_watchlist_id_asset_id"),
    )
    op.create_index("ix_watchlist_items_asset_id", "watchlist_items", ["asset_id"], unique=False)

    op.create_table(
        "alert_events",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "alert_id",
            sa.Integer(),
            sa.ForeignKey("alerts.id", ondelete="SET NULL", name="fk_alert_events_alert_id_alerts"),
            nullable=True,
        ),
        sa.Column(
            "asset_id",
            sa.Integer(),
            sa.ForeignKey("assets.id", ondelete="RESTRICT", name="fk_alert_events_asset_id_assets"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_alert_events_user_id_users"),
            nullable=False,
        ),
        sa.Column(
            "triggered_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("observed_price", sa.Numeric(18, 6), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "event_payload_json",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.create_index(
        "ix_alert_events_user_id_triggered_at",
        "alert_events",
        ["user_id", "triggered_at"],
        unique=False,
    )
    op.create_index(
        "ix_alert_events_asset_id_triggered_at",
        "alert_events",
        ["asset_id", "triggered_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_alert_events_asset_id_triggered_at", table_name="alert_events")
    op.drop_index("ix_alert_events_user_id_triggered_at", table_name="alert_events")
    op.drop_table("alert_events")

    op.drop_index("ix_watchlist_items_asset_id", table_name="watchlist_items")
    op.drop_table("watchlist_items")

    op.drop_index("uq_alerts_active_percent_rule", table_name="alerts")
    op.drop_index("uq_alerts_active_price_rule", table_name="alerts")
    op.drop_index("ix_alerts_asset_id_is_active", table_name="alerts")
    op.drop_index("ix_alerts_user_id_is_active", table_name="alerts")
    op.drop_table("alerts")

    op.drop_table("market_data_points")
    op.drop_table("watchlists")

    op.drop_index("ix_ingestion_runs_started_at", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")

    op.drop_index("ix_assets_is_active", table_name="assets")
    op.drop_index("ix_assets_symbol", table_name="assets")
    op.drop_table("assets")

    op.drop_table("users")