from typing import Dict
from numpy import ndarray

# Dict containing ndarrays at root, and nested json compatible stuff
BaseVals = int | float | list[int] | list[float]
DictBaseVals = Dict[str, BaseVals]
NestedBaseVals = Dict[str, BaseVals | DictBaseVals]
SPT = Dict[str, ndarray | BaseVals | DictBaseVals]
