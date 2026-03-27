# PROJECT_SCOPE.md

## Project Name
market-watch-api

## One-Line Description
Backend service that ingests market data and triggers user-defined alerts for tracked symbols.

## Target User
You first, but implemented as multi-user.

## V1 Users
Authenticated users with personal watchlists and alerts.

## Supported Assets
- Stocks
- ETFs only

## V1 Features
- User authentication
- Personal watchlists
- Add and remove tracked symbols
- User-defined alerts
- Scheduled market data ingestion
- Background alert evaluation
- Alert event history stored and exposed through the API

## Chosen Market Data Cadence
Scheduled polling every 15 minutes during US market hours on trading days.

## Chosen Alert Types
- price_above
- price_below
- pct_move_up_1d
- pct_move_down_1d

## Chosen Deployment Target
Render:
- one FastAPI web service
- one background worker
- one managed PostgreSQL database

## Not Now / Out of Scope
- real-time streaming quotes
- options data
- crypto
- Slack/SMS/push notifications
- dashboards/frontend
- ML predictions
- multi-provider failover
- portfolio analytics
- social/shared watchlists

## Scope Rule
V1 stays backend-first, recruiter-credible, and narrow enough to finish. Do not add frontend, streaming, ML, or additional asset classes before V1 is complete.
