from dataclasses import dataclass
from typing import Protocol


class AsyncByteReader(Protocol):
    async def read(self, size: int) -> bytes:
        raise NotImplementedError()

    async def close(self) -> None:
        raise NotImplementedError()


@dataclass
class FileDomain:
    content_type: str | None
    file_object: AsyncByteReader
