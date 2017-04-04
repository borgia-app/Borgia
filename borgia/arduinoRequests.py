import hashlib

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
            return JsonResponse({
                'token': request.GET['token'],
                'balance': User.objects.get(
                    token_id=request.GET['token']).balance
                })
        except KeyError:
            raise Http404
        except ObjectDoesNotExist:
            raise Http404


class ArduinoCheckVolumeAvailable(ArduinoRequest, View):
    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(token_id=request.GET['token'])
            foyer = Shop.objects.get(name='foyer')
            place = ContainerCase.objects.get(
                shop=foyer,
                name="Tireuse " + request.GET['place']
            )
            if place.product is None:
                raise Http404
            volume_available = round((
                (place.product.product_base.quantity
                 * user.balance)
                / place.product.product_base.get_moded_price()
            ), 0)
            if volume_available < 15:
                volume_available = 15
            if volume_available > 999:
                volume_available = 999
            return JsonResponse({
                'token': request.GET['token'],
                'place': request.GET['place'],
                'volume': volume_available
                })
        except KeyError:
            raise Http404
        except ObjectDoesNotExist:
            raise Http404
        except ValueError:
            raise Http404
