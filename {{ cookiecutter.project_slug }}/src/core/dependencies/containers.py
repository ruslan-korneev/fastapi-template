from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration

from src.db.session import AsyncSessionMaker


class Container(DeclarativeContainer):
    wiring_config = WiringConfiguration(packages=["src"])

    db_session_maker = providers.Factory(AsyncSessionMaker)
