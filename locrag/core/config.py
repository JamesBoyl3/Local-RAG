from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(
			env_file=".env"
			)
	
	RAG_API_URL: str


settings = Settings()
