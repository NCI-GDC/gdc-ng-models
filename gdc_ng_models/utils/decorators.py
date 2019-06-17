from functools import wraps


def try_or_log_error(logger):
    def try_or_log_error_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(e)
        return func_wrapper
    return try_or_log_error_decorator
