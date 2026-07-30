from pages.dashboard_page import DashboardPage


def test_dashboard_loads_after_login(authenticated_page):
    dashboard_page = DashboardPage(authenticated_page)   # 👈 built manually, like LoginPage
    assert dashboard_page.is_dashboard_loaded()


def test_dashboard_title_text(authenticated_page):
    dashboard_page = DashboardPage(authenticated_page)
    title = dashboard_page.get_dashboard_title()
    assert title.strip() == "Dashboard"