import pathlib

import django.urls
import users
from app.constants.constants import ErrorCode, ErrorDetail, ErrorMessage
from app.users.views import LogoutView
from app.util.util import ErrorResponse
from constant import *
from django.http import JsonResponse


def ErrorResponse(code int,path=""):
    ErrorResponse={
        "status_code" :code,
        "error_code"  : ErrorCode[code],
        "message"    : ErrorMessage[code],
        "detail"     :ErrorDetail[code],
        "path"       :path     
    }
    return JsonResponse(ErrorResponse)
    

