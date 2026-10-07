BASE_URL = "https://httpbin.org"

GET = "{}/get".format(BASE_URL)
POST = "{}/post".format(BASE_URL)
PUT = "{}/put".format(BASE_URL)
PATCH = "{}/patch".format(BASE_URL)
DELETE = "{}/delete".format(BASE_URL)
STATUS = "{}/status/{{}}".format(BASE_URL)
REDIRECT_TO = "{}/redirect-to".format(BASE_URL)
