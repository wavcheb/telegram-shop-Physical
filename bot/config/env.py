import os
from abc import ABC
from typing import Final


class EnvKeys(ABC):
    """Secure environment configuration with validation"""

    # Telegram
    TOKEN: Final = os.environ.get('TOKEN')
    OWNER_ID: Final = os.environ.get('OWNER_ID')

    PAY_CURRENCY: Final = os.getenv("PAY_CURRENCY", "USD")
    MIN_AMOUNT: Final = int(os.getenv("MIN_AMOUNT", 20))
    MAX_AMOUNT: Final = int(os.getenv("MAX_AMOUNT", 10_000))

    # Links / UI
    CHANNEL_URL: Final = os.getenv("CHANNEL_URL")
    HELPER_ID: Final = os.getenv("HELPER_ID")
    RULES: Final = os.getenv("RULES")

    # Locale & logs
    BOT_LOCALE: Final = os.getenv("BOT_LOCALE", "en")
    BOT_LOGFILE: Final = os.getenv("BOT_LOGFILE", "logs/bot.log")
    BOT_AUDITFILE: Final = os.getenv("BOT_AUDITFILE", "logs/audit.log")
    LOG_TO_STDOUT: Final = os.getenv("LOG_TO_STDOUT", "1")
    LOG_TO_FILE: Final = os.getenv("LOG_TO_FILE", "1")
    DEBUG: Final = os.getenv("DEBUG", "0")

    # Redis
    REDIS_HOST: Final = os.getenv("REDIS_HOST")
    REDIS_PORT: Final = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: Final = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: Final = os.getenv("REDIS_PASSWORD")

    # Database (MariaDB/MySQL)
    DB_HOST: Final = os.getenv("DB_HOST", "localhost")
    DB_PORT: Final = int(os.getenv("DB_PORT", 3306))
    DB_NAME: Final = os.getenv("DB_NAME", "telegram_shop")
    DB_USER: Final = os.getenv("DB_USER", "shop_user")
    DB_PASSWORD: Final = os.getenv("DB_PASSWORD", "")
    DB_DRIVER: Final = os.getenv("DB_DRIVER", "mysql+pymysql")

    # Monitoring
    MONITORING_HOST: Final = os.getenv("MONITORING_HOST", "localhost")
    MONITORING_PORT: Final = int(os.getenv("MONITORING_PORT", 9090))
