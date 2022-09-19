from functools import wraps
from logging import getLogger
from time import time
from typing import Callable


def supermoon_api(func: Callable):
    logger = getLogger('supermoon')

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time()
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            raise
        finally:
            logger.info(f'<{func.__name__}> Running time: {time() - start}s')

    return wrapper
