from constants.constants import ErrorCode, ErrorDetail, ErrorMessage


def error_response(request, code=400, model_info="Model"):
    res = {
        "status_code": code,
        "error_code": ErrorCode[code],
        "message": model_info + " " + ErrorMessage[code],
        "detail": ErrorDetail[code],
        "path": request.path,
    }
    return res


def success_response(data):
    res = {"data": data}
    return res
