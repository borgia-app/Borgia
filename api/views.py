from django.views.generic import View
from django.http import JsonResponse
import jwt
import time
from datetime import datetime
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from users.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateformat import format
from django.utils import timezone
from django.core import serializers


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
        return JsonResponse(verifyJwt(token, pk))


def generateJwt(user):
    # Save the last iat posix time
    user.jwt_iat = timezone.now()
    user.save()

    # Generate token based on this iat
    payload = {
        'pk': user.pk,
        'iat': user.jwt_iat
    }
    secret = 'kcr,i4kij&hbb02yiy=63rd!+2lw^0!!7p6niv6c4t6cixkohnd_mnjnrn'
    algorithm = 'HS256'

    token = jwt.encode(payload, secret, algorithm)
    return token.decode('utf-8')


def verifyJwt(token, user_pk):
    secret = 'kcr,i4kij&hbb02yiy=63rd!+2lw^0!!7p6niv6c4t6cixkohnd_mnjnrn'
    algorithm = 'HS256'

    try:
        decoded = jwt.decode(token, secret, algorithm)
    except jwt.InvalidTokenError:
        return { 'valid': False, 'message': 'Invalid signature'}

    if user_pk != decoded['pk']:
        return { 'valid': False, 'message': 'Not the right user'}

    try:
        user = User.objects.get(pk=decoded['pk'])
    except ObjectDoesNotExist:
        return { 'valid': False, 'message': 'Unknown user'}

    if int(format(user.jwt_iat, 'U')) != decoded['iat']:
        return { 'valid': False, 'message': 'Token expired'}

    return { 'valid': True, 'user': userObject(user) }


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
