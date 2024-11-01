from flask import make_response

def create_response(data={}, msg="", headers={}, error=False, status_code=200):
    """An easy way to create consitent responses from within the request handlers. 
    Builds a flask response object based on the provided parameters.

    The body format of the response depends upon the value of `error`. If there
    was an error during the handling of a request, set `error` to True.

    :param data: Data to send the client within the body of the response, defaults to {}
    :type data: dict, optional
    :param msg: Message to include in the body of the response, 
    defaults to ""
    :type msg: str, optional
    :param status_code: The HTTP response status code, defaults to 200
    :type status_code: int, optional
    :param headers: Headers that should be added to the response, defaults to {}
    :type headers: dict, optional
    :param error: Whether or not the handler experienced an error while processing the 
    incoming request, defaults to False
    :type error: bool, optional
    :return: A response object to send back to the client
    :rtype: Flask Response object
    """

    if error:
        body = {
                "error": {
                    "code": status_code,
                    "msg": msg
                }
            }
    else:
        body = {
            "data": data, 
            "msg": msg
        }
        

    response = make_response(body, status_code, headers)
    return response
