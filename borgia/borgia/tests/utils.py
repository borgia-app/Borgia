"""
Utils for borgia tests.
"""

from django.contrib.auth import REDIRECT_FIELD_NAME

from borgia.settings import LOGIN_URL


def get_login_url_redirected(url_redirected):
    """
    Return login_url with redirect url.
    """
    return LOGIN_URL + '?' + REDIRECT_FIELD_NAME + '=' + url_redirected
