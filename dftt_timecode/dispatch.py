from functools import wraps


class InstanceMethodDispatch(object):
    _dispatch_router = {}

    @classmethod
    def dispatch(cls, prefix=''):
        def outter_wrapper(func):
            function_id = '{}.{}'.format(prefix, func.__name__) if prefix else func.__name__
            cls._dispatch_router[function_id] = {}

            @wraps(func)
            def wrapper(*args, **kwargs):
                dispatch_func = cls._dispatch_router.get(function_id, {}).get(type(args[1]), None)
                if dispatch_func:
                    return dispatch_func(*args, **kwargs)
                else:
                    return None

            return wrapper

        return outter_wrapper

    @classmethod
    def register(cls, function_id, data_type):
        def outter_wrapper(func):
            router = cls._dispatch_router.setdefault(function_id, {})
            router[data_type] = func
        return outter_wrapper
