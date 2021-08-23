import os
import flask_security
from functools import wraps

def auth_required(*auth_methods, **kwargs):
    """
    Decorator that checks authentication using the method auth_required from Flask-Security-Too

    The decorator is used to allow testing to disable authentication

    Read https://flask-security-too.readthedocs.io/en/stable/api.html#flask_security.auth_required for more details.
    """

    # Check if the client disabled the authentication
    if "VBOA_TEST" in os.environ and os.environ["VBOA_TEST"] == "TRUE":
        # Return a wrapper that makes nothing
        def wrapper(fn):
            # wraps is used to preserve information about the original function
            @wraps(fn)
            def decorated_view(*pargs, **dkwargs):
                return fn(*pargs, **dkwargs)
            return decorated_view

        return wrapper
    else:
        def wrapper(fn):
            # wraps is used to preserve information about the original function
            @wraps(fn)
            @flask_security.auth_required(*auth_methods, **kwargs)
            def decorated_view(*pargs, **dkwargs):

                return fn(*pargs, **dkwargs)
            return decorated_view

        return wrapper
    # end if

def roles_accepted(*roles):
    """
    Decorator that checks role-based authorization using the method roles_accepted from Flask-Security-Too

    The decorator is used to allow testing to disable authorization

    Read https://flask-security-too.readthedocs.io/en/stable/api.html#flask_security.roles_accepted for more details.
    """

    # Check if the client disabled the authorization
    if "VBOA_TEST" in os.environ and os.environ["VBOA_TEST"] == "TRUE":
        def wrapper(fn):
            # wraps is used to preserve information about the original function
            @wraps(fn)
            def decorated_view(*pargs, **dkwargs):
                return fn(*pargs, **dkwargs)
            return decorated_view

        return wrapper
    else:
        def wrapper(fn):
            # wraps is used to preserve information about the original function
            @wraps(fn)
            @flask_security.roles_accepted(*roles)
            def decorated_view(*pargs, **dkwargs):
                return fn(*pargs, **dkwargs)
            return decorated_view

        return wrapper
    # end if
