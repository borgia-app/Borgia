from django.views.generic import View
from django.http import JsonResponse
import jwt
import time
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from users.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateformat import format
from django.utils import timezone
from django.core import serializers
from graphene_django.views import GraphQLView
from django.conf import settings


class GraphQLJwtProtectedView(GraphQLView):
    def dispatch(self, request, *args, **kwargs):
        if (verifyJwt(
                request.META['HTTP_AUTHORIZATION'],
                int(request.META['HTTP_USER']))['valid']):
                return super(GraphQLJwtProtectedView,
                            self).dispatch(request, *args, **kwargs)
        else:
            return JsonResponse({
                'error': True,
                'message': 'Access denied'
            })


@method_decorator(csrf_exempt, name='dispatch')
class AuthGenerateJWT(View):
    def post(self, request, *args, **kwargs):
        try:
            username = request.POST['username']
            password = request.POST['password']
        except KeyError:
            return JsonResponse({
                'error': True,
                'message': 'Credentials must be provided'
            })

        user = authenticate(
            username=username,
            password=password
        )

        if user is not None:
            token = generateJwt(user)
            return JsonResponse({
                'error': False,
                'token': token,
                'pk': user.pk
            })
        return JsonResponse({
            'error': True,
            'message': 'Bad credentials'
        })


@method_decorator(csrf_exempt, name='dispatch')
class AuthVerifyJWT(View):
    def get(self, request, *args, **kwargs):
        pk = int(kwargs['pk'])
        token = kwargs['token']
        if verifyJwt(token, pk)['valid']:
            return JsonResponse({
                'valid': True,
                'user': userObject(User.objects.get(pk=pk))
            })
        return JsonResponse(verifyJwt(token, pk))


@method_decorator(csrf_exempt, name='dispatch')
class AuthInvalidateJWT(View):
    def get(self, request, *args, **kwargs):
        pk = int(kwargs['pk'])
        token = kwargs['token']
        verified = verifyJwt(token, pk)
        if verified['valid']:
            # Invalidate the last token by changing the jwt_iat
            user = User.objects.get(pk=pk)
            user.jwt_iat = timezone.now()
            user.save()
            return JsonResponse({
                'valid': True
            })
        return JsonResponse(verified)


def generateJwt(user):
    # Save the last iat posix time
    user.jwt_iat = timezone.now()
    user.save()

    # Generate token based on this iat
    payload = {
        'pk': user.pk,
        'iat': user.jwt_iat,
        'exp': (user.jwt_iat + timedelta(days=settings.JWT_TOKEN_TIMEOUT))
    }
    secret = settings.MOBILE_SECRET_KEY
    algorithm = settings.JWT_ALGORITHM

    token = jwt.encode(payload, secret, algorithm)
    return token.decode('utf-8')


def verifyJwt(token, user_pk):
    secret = settings.MOBILE_SECRET_KEY
    algorithm = settings.JWT_ALGORITHM

    try:
        decoded = jwt.decode(token, secret, algorithm)
    except jwt.ExpiredSignatureError:
        return { 'valid': False, 'message': 'Expired token' }
    except jwt.InvalidTokenError:
        return { 'valid': False, 'message': 'Invalid signature' }

    if user_pk != decoded['pk']:
        return { 'valid': False, 'message': 'Not the right user' }

    try:
        user = User.objects.get(pk=decoded['pk'])
    except ObjectDoesNotExist:
        return { 'valid': False, 'message': 'Unknown user' }

    if int(format(user.jwt_iat, 'U')) != decoded['iat']:
        return { 'valid': False, 'message': 'Invalid token' }

    return { 'valid': True, 'message': None }


def userObject(user):
    return {
        'pk': user.pk,
        'username': user.username,
        'last_name': user.last_name,
        'first_name': user.first_name,
        'avatar': user.avatar.url,
        'surname': user.surname,
        'family': user.family,
        'campus': user.campus,
        'year': user.year,
        'balance': user.balance
    }
