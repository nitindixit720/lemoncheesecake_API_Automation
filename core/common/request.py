import inspect

import lemoncheesecake.api as lcc
import requests


def print_request_details(url, headers, params=None, data=None):
    caller_function_name = inspect.stack()[1][3]
    lcc.log_info("{} request to --> {}".format(caller_function_name.upper(), url))
    lcc.log_info("Headers: {}".format(str(headers)))
    if caller_function_name == "get":
        lcc.log_info("Params: {}".format(str(params)))
    elif caller_function_name in ["post", "put", "patch"]:
        lcc.log_info("Payload: {}".format(str(data)))


def print_response_details(response):
    lcc.log_info("Response code: {}".format(response.status_code))
    lcc.log_info("Response body: {}".format(response.text))
    lcc.log_info("Response time: {}".format(response.elapsed.total_seconds()))
    if response.elapsed.total_seconds() > 2:
        lcc.log_warning("API Response time is greater than 2 second")
    lcc.log_info(
        "*****************************************************************************************************"
        "******************************************************")


def get(url, headers, params=None):
    print_request_details(url=url, headers=headers, params=params)
    response = requests.get(url=url, params=params, headers=headers)
    print_response_details(response)
    return response


def post(url, headers, data=None, files=None):
    if data is not None or files is None:
        print_request_details(url=url, headers=headers, data=data)
        response = requests.post(url=url, data=data, headers=headers)
    elif files is not None:
        print_request_details(url=url, headers=headers)
        response = requests.post(url=url, files=files, headers=headers)
    print_response_details(response)
    return response


def put(url, data, headers, credentials=None):
    print_request_details(url=url, headers=headers, data=data)
    if credentials is None:
        response = requests.put(url=url, data=data, headers=headers)
    else:
        response = requests.put(url=url, data=data, headers=headers, auth=credentials)
    print_response_details(response)
    return response


def patch(url, data, headers, credentials=None):
    print_request_details(url=url, headers=headers, data=data)
    if credentials is None:
        response = requests.patch(url=url, data=data, headers=headers)
    else:
        response = requests.patch(url=url, data=data, headers=headers, auth=credentials)
    print_response_details(response)
    return response


def delete(url, headers):
    print_request_details(url=url, headers=headers)
    response = requests.delete(url=url, headers=headers)
    print_response_details(response)
    return response
