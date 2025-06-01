from abc import abstractmethod
from datetime import datetime
from typing import Optional

import math
from asyncpg.pgproto.pgproto import timedelta


def cache(ttl: Optional[int]):
    mapping = {}
    def decorator(func):
        def wrapper(*args, **kwargs):
            if (func.__name__, args) in mapping:
                print(f"Cache hit for {func.__name__}")
                res = mapping[(func.__name__, args)]
                if ttl is not None:
                    pre_time = res[1]
                    boundary = pre_time + timedelta(seconds=ttl)
                    current_time = datetime.now()
                    print(f"function call time: {pre_time}")
                    print(f"function call boundary: {boundary}")
                    print(f"function call current: {current_time}")
                    if boundary > current_time:
                        print("cache is valid")
                        return res[0]
                    else:
                        print("cache is invalid")
                        return func(*args, **kwargs)
                else:
                    print("no need for ttl, returning cache")
                    return res[0]
            print("cache not found")
            res = func(*args, **kwargs)
            mapping[(func.__name__, args)] = (res, datetime.now())
            return res
        return wrapper
    return decorator

@cache(10)
def do_heavy_cpu(*args):
    return [math.acosh(ar) for ar in args]


class Some:

    @abstractmethod
    def get_one(self):
        raise NotImplementedError


class Some2(Some):
    ...

if __name__ == '__main__':
    a = Some2()
