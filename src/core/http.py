from httpx import AsyncClient

from src.core.types.singleton import SingletonMeta


class AsyncClientSingleton(AsyncClient, metaclass=SingletonMeta): ...
