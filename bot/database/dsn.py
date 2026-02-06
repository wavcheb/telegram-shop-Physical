import os


def dsn() -> str:
    """Build MariaDB/MySQL connection string from environment variables.

    Supports DATABASE_URL override for testing and custom deployments.
    """
    # Allow full override via DATABASE_URL (used in tests, custom setups)
    override = os.getenv("DATABASE_URL")
    if override:
        return override

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "shop_user")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "telegram_shop")
    driver = os.getenv("DB_DRIVER", "mysql+pymysql")

    return f"{driver}://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
