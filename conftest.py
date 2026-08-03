# conftest.py
from playwright.async_api import async_playwright
import pytest
import allure
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
print("******** conftest imported ********")


def pytest_addoption(parser):
    print("******** pytest_addoption called ********")
    parser.addoption("--browser", action="store")
    parser.addoption("--headed", action="store_true")
    parser.addoption("--base-url", action="store")
    parser.addoption("--video", action="store")
    parser.addoption("--screenshot", action="store")
    parser.addoption("--tracing", action="store")
    parser.addoption("--dashboard-url", action="store")
    parser.addoption("--env", action="store", default="qa_env")

def get_opt(config, name):
    try:
        val = config.getoption(name)
        print(f"{name} = {val} (type={type(val)})")
        if isinstance(val, list):
            return val[0] if val else None
        return val
    except Exception:
        pass

    try:
        val = config.getini(name)
        print(f"INI {name} = {val}")
        return val
    except Exception:
        return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


# ------------------------------------------------------------------
# Shared browser/context launcher — used by BOTH authenticated and
# non-authenticated fixtures, so browser-launch logic lives ONE place.
# ------------------------------------------------------------------
def _launch_browser_context(request, storage_state=None):
    browser_name = get_opt(request.config, "browser") or "chromium"
    headed = bool(get_opt(request.config, "headed"))
    video_policy = get_opt(request.config, "video") or "retain-on-failure"

    print(f"[INFO] Launching browser: {browser_name} (headed={headed})")

#    pw = sync_playwright().start()
    pw = async_playwright().start()

    browser_attr = browser_name.lower()
    if not hasattr(pw, browser_attr):
        pw.stop()
        raise ValueError(f"Unsupported browser: {browser_name}")

    browser = getattr(pw, browser_attr).launch(headless=not headed)

    Path("reports/videos").mkdir(parents=True, exist_ok=True)
    Path("reports/screenshots").mkdir(parents=True, exist_ok=True)
    Path("reports/traces").mkdir(parents=True, exist_ok=True)

    context_args = {}
    if video_policy in ("on", "retain-on-failure"):
        context_args["record_video_dir"] = "reports/videos"
    if storage_state:
        context_args["storage_state"] = storage_state   # 👈 the only new bit

    context = browser.new_context(**context_args)

    return pw, browser, context


def _teardown_browser_context(pw, browser, context):
    try:
        context.close()
    except Exception:
        pass
    try:
        browser.close()
    except Exception:
        pass
    try:
        pw.stop()
    except Exception:
        pass
    print("[INFO] Playwright stopped and browser closed.")


# ------------------------------------------------------------------
# Existing fixture — UNCHANGED behavior, just calls the helper now
# ------------------------------------------------------------------
@pytest.fixture(scope="function")
def browser_context(request):
    pw, browser, context = _launch_browser_context(request, storage_state=None)
    yield context
    _teardown_browser_context(pw, browser, context)


# ------------------------------------------------------------------
# NEW fixture — identical launch logic, but pre-authenticated
# ------------------------------------------------------------------
@pytest.fixture(scope="function")
def authenticated_browser_context(request, auth_state):
    pw, browser, context = _launch_browser_context(request, storage_state=auth_state)
    yield context
    _teardown_browser_context(pw, browser, context)


# ------------------------------------------------------------------
# Shared page-instrumentation logic (tracing/screenshot/video hooks)
# used by BOTH page fixtures below
# ------------------------------------------------------------------
def _build_page(request, browser_context, start_url):
    screenshot_policy = get_opt(request.config, "screenshot") or "only-on-failure"
    tracing_policy = get_opt(request.config, "tracing") or "retain-on-failure"
    video_policy = get_opt(request.config, "video") or "retain-on-failure"

    tracing_started = False
    if tracing_policy in ("on", "retain-on-failure"):
        try:
            browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
            tracing_started = True
        except Exception:
            tracing_started = False

    page = browser_context.new_page()
    page.goto(start_url)

    yield page

    test_name = request.node.name
    test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed

    if tracing_started:
        trace_file = f"reports/traces/{test_name}_trace.zip"
        try:
            browser_context.tracing.stop(path=trace_file)
            if test_failed:
                try:
                    allure.attach.file(trace_file, name=f"{test_name}_trace", attachment_type=allure.attachment_type.ZIP)
                except Exception:
                    pass
        except Exception:
            pass

    if test_failed and screenshot_policy in ("on", "only-on-failure"):
        shot_path = Path(f"reports/screenshots/{test_name}.png")
        try:
            shot_path.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(shot_path))
            try:
                allure.attach.file(str(shot_path), name=f"{test_name}_screenshot", attachment_type=allure.attachment_type.PNG)
            except Exception:
                pass
        except Exception:
            pass

    if test_failed and video_policy in ("on", "retain-on-failure"):
        try:
            video_obj = getattr(page, "video", None)
            video_path = None
            if video_obj:
                try:
                    video_path = video_obj.path()
                except Exception:
                    video_path = None

            if video_path and Path(video_path).exists():
                try:
                    allure.attach.file(video_path, name=f"{test_name}_video", attachment_type=allure.attachment_type.WEBM)
                except Exception:
                    pass
            else:
                vids = list(Path("reports/videos").glob(f"*{test_name}*"))
                if vids:
                    for v in vids:
                        try:
                            allure.attach.file(str(v), name=f"{test_name}_video_fallback", attachment_type=allure.attachment_type.WEBM)
                        except Exception:
                            pass
        except Exception:
            pass


# ------------------------------------------------------------------
# Existing fixture — UNCHANGED behavior for your login tests
# ------------------------------------------------------------------
"""@pytest.fixture(scope="function")
def page(request, browser_context):
    base_url = get_opt(request.config, "base_url") or "about:blank"
    yield from _build_page(request, browser_context, base_url)
"""
@pytest.fixture(scope="function")
def page(request, browser_context, env_config):
    base_url = get_opt(request.config, "base_url") or env_config.get("--base-url") or "about:blank"
    yield from _build_page(request, browser_context, base_url)


# ------------------------------------------------------------------
# NEW fixture — for dashboard/post-login tests, full instrumentation
# ------------------------------------------------------------------
"""
@pytest.fixture(scope="function")
def authenticated_page(request, authenticated_browser_context):
    base_url = get_opt(request.config, "base_url") or "about:blank"
    domain_root = base_url.split("/web/")[0]   # or just use urlparse
    yield from _build_page(request, authenticated_browser_context, domain_root)
"""

@pytest.fixture(scope="function")
def authenticated_page(request, authenticated_browser_context, env_config):
    base_url = get_opt(request.config, "base_url") or env_config.get("--base-url") or "about:blank"
    domain_root = base_url.split("/web/")[0]
    yield from _build_page(request, authenticated_browser_context, domain_root)    

# ------------------------------------------------------------------
# Session-scoped: log in ONCE, save storage_state, reuse everywhere
# ------------------------------------------------------------------
@pytest.fixture(scope="session")
def auth_state(request, env_config):
    from pages.login_page import LoginPage
    from pages.dashboard_page import DashboardPage

    Path("auth").mkdir(parents=True, exist_ok=True)
    auth_file = "auth/state.json"

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(env_config["--base-url"])

    login_page = LoginPage(page)
    login_page.login(env_config["username"], env_config["password"])
    print(f'user name from seected env is {env_config['username']}')

    dashboard_page = DashboardPage(page)
    assert dashboard_page.is_dashboard_loaded(), "Login failed — cannot generate auth state"

    context.storage_state(path=auth_file)
    context.close()
    browser.close()
    pw.stop()

    return auth_file
#####################################################################
######## Swith from one environment to other like qa/dev/prod/staging
#####################################################################

@pytest.fixture(scope="session")
def env_config(request):
    env_name = get_opt(request.config, "env") or "dev"
    config_path = Path(f"config/{env_name}.json")
    print(f'selected Enviroment ath{config_path}')

    if not config_path.exists():
        raise FileNotFoundError(f"No config file found for environment: {env_name}")

    with open(config_path) as f:
        config = json.load(f)

    print(f"[INFO] Loaded environment config: {env_name}")
    return config

import subprocess
import shutil


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """
    Runs once, after the entire test session finishes (all tests done).
    Automatically converts raw allure-results into a browsable HTML report.
    """
    allure_cli = shutil.which("allure")

    if not allure_cli:
        print("[WARN] 'allure' CLI not found on PATH — skipping report generation. "
              "Run 'allure generate reports/allure-results --clean -o reports/allure-report' manually.")
        return

    print("[INFO] Generating Allure HTML report...")
    result = subprocess.run(
        [allure_cli, "generate", "reports/allure-results", "--clean", "-o", "reports/allure-report"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("[INFO] Allure report generated at reports/allure-report")
    else:
        print(f"[ERROR] Allure report generation failed:\n{result.stderr}")    