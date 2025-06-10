
import functools

def log_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        print(res)
        return res
    return wrapper


@log_decorator
def client():
    """some doc string"""
    a = 1 + 2
    return a