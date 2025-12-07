from abc import ABC, abstractmethod


class Query:
    pass


class QueryHandler(ABC):
    @abstractmethod
    def handle(self, command: Query) -> None:
        pass
