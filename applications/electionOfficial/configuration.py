from datetime import timedelta;
import os;

databaseUrl = os.environ["DATABASE_URL"];

class Configuration ( ):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/applications";
    REDIS_HOST = "redis";
    REDIS_VOTES_LIST = "votes";
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    #JSON_SORT_KEYS = False;
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)