from django.shortcuts import redirect
from functools import wraps

def citizen_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('citizen_id'):
            return redirect('citizen_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def company_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('company_id'):
            return redirect('company_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def worker_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('worker_id'):
            return redirect('worker_login')
        return view_func(request, *args, **kwargs)
    return wrapper
