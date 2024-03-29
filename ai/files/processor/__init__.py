from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# The File type that processor is working with
FileT = TypeVar("FileT")
# The type of the processing data
T = TypeVar("T")


class DatasetItemProcessor(ABC, Generic[FileT, T]):
    def __init__(self):
        pass

    @abstractmethod  # check if the FileT has anything cached
    def is_cached(self, file: FileT) -> bool:
        pass

    @abstractmethod  # get cache of FileT (this assumes there is cached data)
    def get_cache(self, file: FileT) -> T:
        pass

    @abstractmethod  # cache the processed T
    def cache(self, file: FileT, data: T) -> bool | None:
        pass

    @abstractmethod  # process the FileT
    def process(self, file: FileT) -> T:
        pass

    def features(self, file: FileT) -> T:
        if self.is_cached(file):
            return self.get_cache(file)

        data: T = self.process(file)
        self.cache(file, data)

        return data

    def cache_if_uncached(self, file: FileT):
        if not self.is_cached(file):
            data: T = self.process(file)
            self.cache(file, data)
