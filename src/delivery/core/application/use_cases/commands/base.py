from abc import ABC, abstractmethod


class Command:
    pass


class CommandHandler(ABC):
    @abstractmethod
    async def handle(self, command: Command) -> None:
        pass
