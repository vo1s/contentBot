from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    crypto_bot_token: SecretStr
    db_name: SecretStr
    bot_name: SecretStr
    channel_name: SecretStr
    channel_link: SecretStr
    contact_admin: SecretStr
    moderation_chat_id: SecretStr
    admins: SecretStr
    db: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
