import os

# Configuration de base
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    DEBUG = False
    TESTING = False
    
# Configuration de développement
class DevelopmentConfig(Config):
    DEBUG = True
    
# Configuration de production
class ProductionConfig(Config):
    DEBUG = False
    
# Configuration de test
class TestingConfig(Config):
    TESTING = True
    
# Configuration par défaut
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}