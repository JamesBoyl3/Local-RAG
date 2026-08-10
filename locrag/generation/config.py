from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file="LLM.env")

    TEMP: float
    MAX_TOKENS: int
    N_CTX: int
    


llmsettings = LLMSettings()
