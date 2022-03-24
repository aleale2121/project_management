from app.constants.constants import ErrorCode, ErrorDetail, ErrorMessage
from django.http import JsonResponse



def ErrorResponse(code=400 ,model_info="",path=""):
    ErrRes={
        "status_code" :code,
        "error_code"  : ErrorCode[code],
        "message"    : ErrorMessage[code],
        "detail"     :ErrorDetail[code],
        "path"       :path     
    }
    return JsonResponse(ErrRes)
