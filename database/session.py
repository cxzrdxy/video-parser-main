from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import URL

from configs.general_constants import DATABASE_CONFIG


def _build_mysql_url() -> str:
    user = DATABASE_CONFIG.get("user") or ""
    password = DATABASE_CONFIG.get("password") or ""
    host = DATABASE_CONFIG.get("host") or "localhost"
    port = DATABASE_CONFIG.get("port")
    database = DATABASE_CONFIG.get("database") or ""
    if port:
        return str(
            URL.create(
                "mysql+mysqlconnector",
                username=user,
                password=password,
                host=host,
                port=int(port),
                database=database,
            )
        )
    return str(
        URL.create(
            "mysql+mysqlconnector",
            username=user,
            password=password,
            host=host,
            database=database,
        )
    )


engine = create_engine(_build_mysql_url(), echo=False, pool_pre_ping=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
