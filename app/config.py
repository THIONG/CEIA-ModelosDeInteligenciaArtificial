class Config:
    DEBUG = False
    MAX_HISTORY = 10
    LLM_MODEL = "mistral"
    PORT = 5000

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = DevelopmentConfig()