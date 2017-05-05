from django.views.generic import View
from django.http import JsonResponse
import jwt
import time
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
            return JsonResponse({
                'error': False,
                'user': user.pk,
                'token': generateJwt(user)
            })
        return JsonResponse({
            'error': True,
            'message': 'Bad credentials'
        })


def generateJwt(user):
    payload = {
        'pk': user.pk,
        'iat': time.time()
    }
    secret = 'kcr,i4kij&hbb02yiy=63rd!+2lw^0!!7p6niv6c4t6cixkohnd_mnjnrn'
    algorithm = 'HS256'

    token = jwt.encode(payload, secret, algorithm)
    return token.decode('utf-8')
