"""
Example suite demonstrating this framework's API testing conventions:
GET/POST/PUT/PATCH/DELETE via core.common.request, lemoncheesecake matchers
for assertions, and status/URL-behavior checks. Runs against the public
httpbin.org service so it works out of the box with no backend of your own.
"""
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common import endpoints
from core.common import request

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


@lcc.suite("Httpbin demo suite")
class HttpbinDemo:

    @lcc.test("GET request echoes back the query params that were sent")
    def test_get_request(self):
        params = {"framework": "lemoncheesecake"}
        response = request.get(url=endpoints.GET, headers=HEADERS, params=params)
        check_that("response code", response.status_code, equal_to(200))
        check_that("echoed args", response.json()["args"], equal_to(params))

    @lcc.test("POST request echoes back the form data that was sent")
    def test_post_request(self):
        data = {"name": "lcc-automation"}
        response = request.post(url=endpoints.POST, headers=HEADERS, data=data)
        check_that("response code", response.status_code, equal_to(200))
        check_that("echoed form data", response.json()["form"], equal_to(data))

    @lcc.test("PUT request echoes back the data that was sent")
    def test_put_request(self):
        data = {"status": "updated"}
        response = request.put(url=endpoints.PUT, data=data, headers=HEADERS)
        check_that("response code", response.status_code, equal_to(200))
        check_that("echoed form data", response.json()["form"], equal_to(data))

    @lcc.test("PATCH request echoes back the data that was sent")
    def test_patch_request(self):
        data = {"status": "patched"}
        response = request.patch(url=endpoints.PATCH, data=data, headers=HEADERS)
        check_that("response code", response.status_code, equal_to(200))
        check_that("echoed form data", response.json()["form"], equal_to(data))

    @lcc.test("DELETE request returns a successful response")
    def test_delete_request(self):
        response = request.delete(url=endpoints.DELETE, headers=HEADERS)
        check_that("response code", response.status_code, equal_to(200))

    @lcc.test("Requesting a URL that returns 404 is correctly reported as a client error")
    def test_url_returns_not_found(self):
        response = request.get(url=endpoints.STATUS.format(404), headers=HEADERS)
        check_that("response code", response.status_code, equal_to(404))

    @lcc.test("A URL configured to redirect resolves to its target location")
    def test_url_redirect(self):
        target_url = endpoints.GET
        response = request.get(
            url=endpoints.REDIRECT_TO, headers=HEADERS, params={"url": target_url}
        )
        check_that("response code", response.status_code, equal_to(200))
        check_that("final resolved URL", response.url, equal_to(target_url))
        check_that(
            "redirect history", len(response.history) > 0, equal_to(True)
        )
