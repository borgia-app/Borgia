from django.views.generic import View
from django.http import JsonResponse


class ArduinoRequest(object):
    def dispatch(self, request, *args, **kwargs):
        '''
        Check hash MD5 authentification
        '''
        return super(ArduinoRequest, self).dispatch(request, *args, **kwargs)

class ArduinoConnect(ArduinoRequest, View):
    '''
    Simply send a boolean response to see if the connection is ok or not.

    :note: Only GET is allowed here. None error codes are listed here, only
    connection errors can happened.
    :note: This function is not concerned with the session authentification.
    Be sure to check the authentification of the request with the class
    ArduinoRequest in the dispatch function.

    :param GET['token']: hash token generated with MD5 algorithm
    :return: connect: always true here
    :rtype: HTTP JSON response object
    '''
    def get(self, request, *args, **kwargs):
        return JsonResponse({'connect': True})
