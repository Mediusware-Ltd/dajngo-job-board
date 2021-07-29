from functools import wraps


def admin_required(view_func, arg):
    def decorated_function(request, *args, **kwargs):
        print(request)
        print(arg)
        return view_func(request, *args, **kwargs)

    return decorated_function
