import hashlib
import re

from django.views.generic import View
from django.http import JsonResponse, Http404
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from users.models import User
from shops.models import ContainerCase, Shop

# TODO: right error code, refer to phabricator.iresam.org/T199
# TODO: right docstrings

## BE CAREFUL: THESES FUNCTIONS ARE NOT COMMON, THEY ARE ONLY USED FOR ENSAM METZ

class ArduinoRequest(object):
    def dispatch(self, request, *args, **kwargs):
        '''
        Check hash MD5 authentification
        '''
        concat = ''
        for k, v in sorted(request.GET.items()):
            if k != 'key':
                concat += (k + v)
        concat += settings.ARDUINO_PRIVATE
        try:
            if hashlib.md5(concat.encode('utf-8')).hexdigest() != request.GET['key']:
                raise Http404
        except KeyError:
            raise Http404
        return super(ArduinoRequest, self).dispatch(request, *args, **kwargs)


def errorJsonResponse(code, parameter = None):
    """
    Return a JsonResponse with the object error giving information about the
    error code with a message.

    :param code: error code
    :type code: integer
    :param parameter: missing parameter for code 2
    :type parameter: string
    :returns: JsonResponse object error with code and message
    """
    message = None
    # Miscellaneous
    if code == 1:
        message = 'unknown error'
    if code == 2:
        message = 'missing parameter ' + parameter
    # Token 1XX
    if code == 101:
        message = 'void token'
    if code == 102:
        message = 'linked user not found'
    # User 2XX
    if code == 201:
        message = 'unactiv user'
    if code == 202:
        message = 'void balance'
    # Tap place 3XX
    if code == 301:
        message = 'unknown tap number'
    if code == 302:
        message = 'no current container for this tap'
    if code == 303:
        message = 'empty container for this tap'
    # Purchase 6XX
    if code == 601:
        message = 'void requested volume'

    # Default
    if message is None:
        message = 'unknown error'
    return JsonResponse({'error': {
        'code': code,
        'message': message
    }})


class ArduinoConnect(View):
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
        return JsonResponse({'true': True})


class ArduinoCheckUser(ArduinoRequest, View):
    def get(self, request, *args, **kwargs):
        try:
            token = request.GET['token']
            if not re.match('^[0-9A-Z]{12}$', token):
                return errorJsonResponse(101)
        except KeyError:
            return errorJsonResponse(2, 'token')
        try:
            user = User.objects.get(token_id=token)
        except ObjectDoesNotExist:
            return errorJsonResponse(102)
        if not user.is_active:
            return errorJsonResponse(201)
        if user.balance <= 0:
            return errorJsonResponse(202)

        return JsonResponse({
            'token': token,
            'balance': user.balance
        })


class ArduinoCheckVolumeAvailable(ArduinoRequest, View):
    def get(self, request, *args, **kwargs):
        try:
            token = request.GET['token']
            if not re.match('^[0-9A-Z]{12}$', token):
                return errorJsonResponse(101)
        except KeyError:
            return errorJsonResponse(2, 'token')
        try:
            foyer = Shop.objects.get(name='foyer')
        except KeyError:
            return errorJsonResponse(1)
        try:
            place_id = request.GET['place']
        except KeyError:
            return errorJsonResponse(2, 'place')

        try:
            user = User.objects.get(token_id=token)
        except ObjectDoesNotExist:
            return errorJsonResponse(102)
        try:
            place = ContainerCase.objects.get(
                shop=foyer,
                name="Tireuse " + place_id
            )
        except ObjectDoesNotExist:
            return errorJsonResponse(301)
        if place.product is None:
            return errorJsonResponse(302)
        if place.product.quantity_remaining <= 0:
            return errorJsonResponse(303)

        volume_available = round((
            (place.product.product_base.quantity
             * user.balance)
            / place.product.product_base.get_moded_price()
        ), 0)
        if volume_available > place.product.quantity_remaining:
            volume_available = quantity_remaining
        if volume_available < 15:
            volume_available = 15
        if volume_available > 999:
            volume_available = 999

        return JsonResponse({
            'token': token,
            'place': place_id,
            'volume': volume_available
            })
