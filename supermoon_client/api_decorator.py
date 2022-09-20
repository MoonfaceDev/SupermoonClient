from functools import wraps
from time import time
from typing import Callable

from supermoon_client.logger import get_logger


def supermoon_api(func: Callable):
    logger = get_logger()

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
