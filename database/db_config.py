from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Example Config
class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:ihab2003*@mysql-container:3306/ecommerce_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False