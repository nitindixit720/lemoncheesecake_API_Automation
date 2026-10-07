# lemoncheesecake API Automation

API test automation framework built on [lemoncheesecake](https://lemoncheesecake.io), a Python test
storytelling framework. It wraps `requests` with logging/response-time helpers, organizes suites by
service, and can publish results to Slack and an HTML report archive on S3.

## Requirements

- Python 3.9+
- pip

## Setup

```bash
git clone <repo-url>
cd Lcc
python3 -m venv venv
source venv/bin/activate
pip install -r requirement.txt
```

## Running the tests

```bash
source venv/bin/activate
export PYTHONPATH=.
lcc run --reporting console html --exit-error-on-failure
```

- `--reporting` selects which reporting backends to enable for the run (`console`, `html`, `json`, ...).
- `--exit-error-on-failure` makes the process exit non-zero when any test doesn't pass, for CI gating.
- An HTML report is written to `report/report.html`.

Run a single suite or test with a path filter, e.g. `lcc run suites.httpbin_demo`.

### CI / full pipeline run

`entrypoint.sh` wraps the same `lcc run` invocation with: venv setup, a timestamped report
directory, an S3 upload of the report via `scripts/upload_report_to_s3.py`, and a pass/fail
Slack notification via `scripts/send_message_to_slack.py`. It expects the following environment
variables to be set (the script has placeholder values you must replace):

| Variable | Used by | Purpose |
|---|---|---|
| `TEST_ENV` | `entrypoint.sh` | Environment label included in report paths and Slack messages |
| `SLACK_AUTH_TOKEN` | `scripts/send_message_to_slack.py` | Slack bot token used to post the run result |
| `SLACK_CHANNEL` | `scripts/send_message_to_slack.py` | Slack channel to notify |
| `S3_BUCKET_NAME` | `scripts/upload_report_to_s3.py` | S3 bucket the HTML report is uploaded to |
| `S3_HOST` | `scripts/upload_report_to_s3.py` | S3-compatible endpoint host (defaults to `s3.ap-south-1.amazonaws.com`) |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | `boto3` (via `scripts/upload_report_to_s3.py`) | AWS credentials, picked up automatically by `boto3` -- do not hardcode them anywhere in the repo |

Run it with:

```bash
./entrypoint.sh
```

## Project structure

```
project.py              lemoncheesecake project definition (suites/fixtures discovery)
common/endpoints.py      API base URL and endpoint path constants
core/common/request.py   requests wrapper: logs request/response, flags slow responses (>2s)
core/common/singleton.py Singleton base class
core/utils/utils.py      Shared test-data generators and response assertion helpers
suites/                  Test suites (one module/class per service or feature area)
scripts/                 CI helpers: Slack notification, S3 report upload
entrypoint.sh            Full CI pipeline: install, run tests, upload report, notify Slack
```

## API testing conventions used in this framework

- **Use the shared request helpers** in `core/common/request.py` (`get`, `post`, `put`, `patch`,
  `delete`) instead of calling `requests` directly in a suite. They log the request/response and
  flag any response slower than 2 seconds.
- **One suite class per service/feature**, decorated with `@lcc.suite(...)`; one method per test
  case, decorated with `@lcc.test("description")`. See `suites/httpbin_demo.py` for the pattern.
- **Assert with lemoncheesecake matchers** (`lemoncheesecake.matching.check_that`, `equal_to`, etc.)
  rather than bare `assert` statements, so failures show up with context in the HTML/console report.
- **Endpoint URLs live in `common/endpoints.py`**, not inlined in suites, so a base URL change is a
  one-line edit.
- **Cover the positive and negative path** for each endpoint: at least one 2xx case and one expected
  error/edge case (see `test_url_returns_not_found` and `test_url_redirect` in the example suite).
- **Environment-based configuration**: target environment (`TEST_ENV`), secrets, and S3/Slack config
  are all read from environment variables, never hardcoded in source.

## Example suite

`suites/httpbin_demo.py` is a self-contained example that exercises GET/POST/PUT/PATCH/DELETE,
a 404 response, and a URL redirect, against the public [httpbin.org](https://httpbin.org) service --
useful as a template for a new suite and as a smoke test that the framework itself is working.

## Dependency notes (2026-10 modernization)

This project was initially built in 2019-2020 against now-unmaintained dependency versions. As of
this update:

- `lemoncheesecake` was migrated from the unmaintained `0.22.10` line to the current `1.15.0`. This
  is a breaking change in lemoncheesecake itself: `project.py` now uses the `Project` class instead
  of the removed `SimpleProjectConfiguration`, and the CLI flag is `--reporting` (was
  `--enable-reporting`).
- `boto` (unmaintained since ~2018) was replaced with `boto3` (AWS's current, actively maintained
  SDK) in `scripts/upload_report_to_s3.py`. Credentials are now read from the environment via
  boto3's default credential chain instead of being hardcoded placeholder strings in source.
- `requests` was bumped to `2.34.2` and `slacker` to `0.14.0` (latest available).
- `aiohttp`, `python-slugify` (as a direct pin), `attrs`, `cryptography`, `pyOpenSSL`, and other
  transitive packages were removed from `requirement.txt`: they were not imported anywhere in this
  codebase and are already pulled in automatically as dependencies of `lemoncheesecake`/`requests`/
  `boto3` where actually needed. `requirement.txt` now pins only the packages this codebase imports
  directly.
- Fixed a bug in `entrypoint.sh` where `--enable-reporting slack ...` enabled lemoncheesecake's
  built-in Slack reporting backend, but the Slack env vars it requires (`LCC_SLACK_AUTH_TOKEN`,
  `LCC_SLACK_CHANNEL`) were never set (the script set `SLACK_AUTH_TOKEN`/`SLACK_CHANNEL` instead,
  which are only read by the separate `scripts/send_message_to_slack.py`). The built-in Slack
  backend was dropped from `--reporting` since `scripts/send_message_to_slack.py` already sends a
  pass/fail-aware notification after the run; keeping both would have been redundant once fixed.
- Fixed `core/common/request.py` comparing a string with `is` instead of `==` (undefined behavior /
  `SyntaxWarning` on Python 3.8+).
- Switched `entrypoint.sh` from `virtualenv` to the standard-library `python3 -m venv`, removing a
  dependency on an external tool for environment setup.

All of the above were verified by installing into a clean virtual environment and running the full
suite (`lcc run --reporting console html --exit-error-on-failure`) end to end -- 7/7 tests pass.
