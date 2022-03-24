from http import HTTPStatus

# constant variables
MODEL_CREATION_FAILED        =  HTTPStatus.BAD_REQUEST.value
MODEL_UPDATE_FAILED          =  HTTPStatus.BAD_REQUEST.value
MODEL_DELETE_FAILED          =  HTTPStatus.BAD_REQUEST.value
MODEL_RECORD_NOT_FOUND       =  HTTPStatus.NOT_FOUND.value
MODEL_MULTIPLE_RECORD_FOUND  =  HTTPStatus.NOT_ACCEPTABLE.value
MODEL_INTEGRITY_FAILED       =  HTTPStatus.BAD_REQUEST.value
UNAUTHORIZED_REQUEST_FOUND   =  HTTPStatus.UNAUTHORIZED.value
FORBIDDEN_REQUEST_FOUND      =  HTTPStatus.FORBIDDEN.value
RESOURCE_NOT_FOUND           =  HTTPStatus.NOT_FOUND.value
METHOD_NOT_ALLOWED           =  HTTPStatus.METHOD_NOT_ALLOWED.value
CONFLICT_HAPPENED            =  HTTPStatus.CONFLICT.value
INTERNAL_SERVER_ERROR        =  HTTPStatus.INTERNAL_SERVER_ERROR.value
SERVICE_UNAVAILABLE          =  HTTPStatus.SERVICE_UNAVAILABLE.value


# ErrorCode
ErrorCode = {}
ErrorCode[MODEL_CREATION_FAILED] = 6000
ErrorCode[MODEL_UPDATE_FAILED] = 6001
ErrorCode[MODEL_DELETE_FAILED] = 6002
ErrorCode[MODEL_RECORD_NOT_FOUND] = 6003
ErrorCode[MODEL_MULTIPLE_RECORD_FOUND] = 6004
ErrorCode[MODEL_INTEGRITY_FAILED] = 6005
ErrorCode[UNAUTHORIZED_REQUEST_FOUND] = 6006
ErrorCode[FORBIDDEN_REQUEST_FOUND] = 6007
ErrorCode[RESOURCE_NOT_FOUND] = 6008
ErrorCode[METHOD_NOT_ALLOWED] = 6009
ErrorCode[CONFLICT_HAPPENED] = 6010
ErrorCode[INTERNAL_SERVER_ERROR] = 6011
ErrorCode[SERVICE_UNAVAILABLE] = 6012



# ErrorMessage
ErrorMessage = {}
ErrorMessage[MODEL_CREATION_FAILED]         = " Creation Faild!"
ErrorMessage[MODEL_UPDATE_FAILED]           = " Update Faild!"
ErrorMessage[MODEL_DELETE_FAILED]           = " Fetching Faild!"
ErrorMessage[MODEL_RECORD_NOT_FOUND]        = " Record Not Found!"
ErrorMessage[MODEL_MULTIPLE_RECORD_FOUND]   = " Multiple Record Returned Faild!"
ErrorMessage[MODEL_INTEGRITY_FAILED]        = "Field Integrity Faild!"
ErrorMessage[UNAUTHORIZED_REQUEST_FOUND]    = "Unauthorized User REquest Found!"
ErrorMessage[FORBIDDEN_REQUEST_FOUND]       = "Permission Denied for this Request!"
ErrorMessage[RESOURCE_NOT_FOUND]            = "Resource Not Found!"
ErrorMessage[METHOD_NOT_ALLOWED]            = "Request Not Allowed!"
ErrorMessage[CONFLICT_HAPPENED]             = "Request Under Conflict!"
ErrorMessage[INTERNAL_SERVER_ERROR]         = "Server Not Functioning Well! "
ErrorMessage[SERVICE_UNAVAILABLE]           ="Server Out Of Service!"



# ErrorDetail
ErrorDetail = {}
ErrorDetail[MODEL_CREATION_FAILED]        = HTTPStatus.BAD_REQUEST.description
ErrorDetail[MODEL_UPDATE_FAILED]          = HTTPStatus.BAD_REQUEST.description
ErrorDetail[MODEL_DELETE_FAILED]          = HTTPStatus.BAD_REQUEST.description
ErrorDetail[MODEL_RECORD_NOT_FOUND]       = HTTPStatus.NOT_FOUND.description
ErrorDetail[MODEL_MULTIPLE_RECORD_FOUND]  = HTTPStatus.NOT_ACCEPTABLE.description
ErrorDetail[MODEL_INTEGRITY_FAILED]       = HTTPStatus.BAD_REQUEST.description
ErrorDetail[UNAUTHORIZED_REQUEST_FOUND]   = HTTPStatus.UNAUTHORIZED.description
ErrorDetail[FORBIDDEN_REQUEST_FOUND]      = HTTPStatus.FORBIDDEN.description
ErrorDetail[RESOURCE_NOT_FOUND]           = HTTPStatus.NOT_FOUND.description
ErrorDetail[METHOD_NOT_ALLOWED]           = HTTPStatus.METHOD_NOT_ALLOWED.description
ErrorDetail[CONFLICT_HAPPENED]            = HTTPStatus.CONFLICT.description
ErrorDetail[INTERNAL_SERVER_ERROR]        = HTTPStatus.INTERNAL_SERVER_ERROR.description
ErrorDetail[SERVICE_UNAVAILABLE]          = HTTPStatus.SERVICE_UNAVAILABLE.description


# ErrorPath
ErrorPath = ""
