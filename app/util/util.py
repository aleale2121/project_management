import pathlib

import django.urls
import users
from app.constants.constants import ErrorCode, ErrorDetail, ErrorMessage
from app.users.views import LogoutView
from app.util.util import ErrorResponse
from constant import *
from django.http import JsonResponse


def ErrorResponse(code int,model_info,path=""):
    ErrorResponse={
        "status_code" :code,
        "error_code"  : ErrorCode[code],
        "message"    : model_info+ErrorMessage[code],
        "detail"     :ErrorDetail[code],
        "path"       :path     
    }
    return JsonResponse(ErrorResponse)
    

