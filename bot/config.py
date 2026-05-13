from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class Config:
    bot_token: str
    admin_id: int
    database_url: str



def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "")
    admin_id = os.getenv("ADMIN_ID", "")
    database_url = os.getenv("DATABASE_URL", "")

    if not bot_token:
        raise ValueError("BOT_TOKEN is not set in environment")
    if not admin_id.isdigit():
        raise ValueError("ADMIN_ID must be a numeric Telegram ID")
    if not database_url:
        raise ValueError("DATABASE_URL is not set in environment")

    return Config(
        bot_token=bot_token,
        admin_id=int(admin_id),
        database_url=database_url,
    )
