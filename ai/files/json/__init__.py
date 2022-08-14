from json import JSONEncoder, JSONDecoder
from typing import Callable, Any

import numpy as np


class NpEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


class NpDecoder(JSONDecoder):
    # Keep default implementation for now
    pass
