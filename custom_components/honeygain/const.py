"""Constants for the Honeygain integration."""

from datetime import timedelta

DOMAIN = "honeygain"
UPDATE_INTERVAL = timedelta(minutes=30)

API_METHODS = {
    "account": "me",
    "devices": "devices",
    "earnings": "stats",
    "jumptask_earnings": "stats_jt",
    "earnings_today": "stats_today",
    "jumptask_earnings_today": "stats_today_jt",
    "wallet_stats": "wallet_stats",
    "notifications": "notifications",
    "balances": "balances",
    "payouts": "payouts",
    "honeypot": "get_honeypot_status",
    "jumptask_wallet": "get_bsc_wallet_settings",
}

SENSOR_NAMES = {
    "account": "Account",
    "devices": "Devices",
    "earnings": "Earnings",
    "jumptask_earnings": "JumpTask earnings",
    "earnings_today": "Earnings today",
    "jumptask_earnings_today": "JumpTask earnings today",
    "wallet_stats": "Wallet stats",
    "notifications": "Notifications",
    "balances": "Balances",
    "payouts": "Payouts",
    "honeypot": "Honey Pot",
    "jumptask_wallet": "JumpTask wallet",
}
