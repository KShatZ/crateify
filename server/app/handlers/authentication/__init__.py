from flask import Blueprint

Authentication = Blueprint("Authentication", __name__)
from . import routes



# @Authentication.after_request --- Do not need this at the moment while both hosts are localhost. Might need something like this in production depending on ÇORS or not.
def set_cors_headers(response):
    """Middleware function that sets neccesary headers in order
    to satisfy CORS policy.

    :param response: The response returned by the route handler on it"s way
    to the client.
    :type response: Flask Response object
    :return: The response object with updated headers.
    :rtype: Flask Response object
    """

    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true") # JS Fetch API - Allow and store cookies

    return response
