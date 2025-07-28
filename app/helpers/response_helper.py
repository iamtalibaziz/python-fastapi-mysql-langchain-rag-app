from fastapi.responses import JSONResponse
from fastapi import status
def success_response(data, status_code=status.HTTP_200_OK):
    # return JSONResponse(
    #     status_code=status_code,
    #     content={
    #         "success": True,
    #         "data": data
    #     }
    # )
    return {
        "success": True,
        "data": data
    }

def error_response(message, status_code=status.HTTP_400_BAD_REQUEST, errors=None):
    response = {
        "success": False,
        "message": message
    }
    if errors:
        response["errors"] = errors

    return JSONResponse(
        status_code=status_code,
        content=response
    )

def validation_error_response(errors):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": errors
        }
    )

def internal_server_error_response():
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Unable to process request"
        }
    )
