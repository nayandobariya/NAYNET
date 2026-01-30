from django.core.exceptions import PermissionDenied

def user_is_employer(function):

    def wrap(request, *args, **kwargs):   

        if request.user.role == 'employer' or request.user.is_staff:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap



def user_is_employee(function):

    def wrap(request, *args, **kwargs):
        id = kwargs.get('id')
        if request.user.is_authenticated and (request.user.role == 'employee' or request.user.is_staff or str(request.user.id) == str(id)):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap
