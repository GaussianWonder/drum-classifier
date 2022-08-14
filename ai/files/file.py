from os import path as opath
import hashlib
from typing import TypeVar, Callable, AnyStr

T = TypeVar("T")


class File:
    path: str = ''
    name: str = ''
    ext: str = ''

    def __init__(self, path: str):
        if not opath.exists(path):
            raise Exception('File {} does not exist!'.format(path))

        self.path = path
        name, ext = opath.splitext(path)
        self.name = name
        self.ext = ext

    def chunk_reducer(self, reducer: Callable[[T, AnyStr | str | bytes], T], init: T, chunk_size: int = 1024) -> T:
        next_iter: T = init
        with open(self.path, 'rb') as file:
            chunk: AnyStr | str | bytes = b'?'
            while chunk != b'':
                chunk = file.read(chunk_size)
                next_iter = reducer(next_iter, chunk)
        return next_iter

    def file_hash(self, hash_function) -> str:
        reduced = self.chunk_reducer(  # type: ignore
            reducer=lambda hasher, chunk: hasher.update(chunk),
            init=hash_function
        )
        return reduced.hexdigest()

    def sha1(self):
        return self.file_hash(hashlib.sha1())

    def sha256(self):
        return self.file_hash(hashlib.sha256())

    def md5(self):
        return self.file_hash(hashlib.md5())

    def identity(self):
        return '{}:{}:{}'.format(self.md5(), self.sha1(), self.sha256())
