import jwt
from django.conf import settings
from django.http import JsonResponse
from functools import wraps

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, args, **kwargs):
        auth_header = request.headers.get('authorization')

        if not auth_header:
            return JsonResponse({'error': 'Authorization header missing'}, status=401)

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return JsonResponse({'error': 'Invalid authorization header format'}, status=401)

        token = parts[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            request.user_payload = payload  # Attach decoded token to request
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        return view_func(request,args, **kwargs)

    return wrapper