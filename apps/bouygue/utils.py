from django.utils.http import url_has_allowed_host_and_scheme


def safe_next(request, default):
    """The ?next= address when it stays on this site, `default` otherwise.

    Without the check, a link such as ?next=https://example.com would send the
    user to another site after the action.
    """
    next_url = request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return next_url
    return default
