import os

class Settings:
    DATABASE_URL = os.getenv("OFFICEAI_DB_URL", "sqlite:///./officeai.db")
    SECRET_SALT = os.getenv("OFFICEAI_SECRET_SALT", "officeai-local-safe-salt")
    BUDGET_LIMIT = 50000.0
    COST_PER_MISS = 0.12

settings = Settings()
