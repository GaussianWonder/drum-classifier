from os import path as opath, remove
import hashlib
from typing import TypeVar, Callable, AnyStr

T = TypeVar("T")


class File:
    path: str
    name: str
    ext: str
    identity: str

    def __init__(self, path: str):
        if not opath.exists(path):
            raise Exception('File {} does not exist!'.format(path))
        if not opath.isfile(path):
            raise Exception('File {} is not actually a file!'.format(path))

        self.path = path
        name, ext = opath.splitext(opath.basename(path))
        self.name = name
        self.ext = ext
        self.identity = self.calculate_identity()

    def chunk_reducer(self, reducer: Callable[[T, AnyStr | str | bytes], T], init: T, chunk_size: int = 65536) -> T:
        next_iter: T = init
        with open(self.path, 'rb') as file:
            chunk: AnyStr | str | bytes = b'?'
            while chunk:
                chunk = file.read(chunk_size)
                next_iter = reducer(next_iter, chunk)
        return next_iter

    def file_hash(self, hash_function) -> str:
        reduced = self.chunk_reducer(  # type: ignore
            reducer=hash_reducer,
            init=hash_function
        )
        return reduced.hexdigest()

    def sha1(self):
        return self.file_hash(hashlib.sha1())

    def md5(self):
        return self.file_hash(hashlib.md5())

    def calculate_identity(self):
        return '{}.{}'.format(self.md5(), self.sha1())

    def delete(self):
        remove(self.path)


def hash_reducer(hasher, chunk):
    hasher.update(chunk)
    return hasher
