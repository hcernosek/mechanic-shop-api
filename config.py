
# MySQL database configuration
class DevelopmentConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:Hcc,0801@localhost/mechanic_shop_db"
    
class TestingConfig:
    pass

class ProductionConfig:
    pass 