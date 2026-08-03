import pytest
from pages.login_page import LoginPage
from utility.data_reader_file import read_json_data
from playwright.sync_api import expect

test_data = read_json_data("testdata/login_test_data.json")


@pytest.mark.parametrize(
    "test_name,email_username,password,expected_result",
    test_data
)
def test_login(page, test_name, email_username, password, expected_result):

    login_page = LoginPage(page)

    login_page.login(email_username, password)

    if expected_result == "Success":
        assert page.get_by_role("heading", name="Dashboard").is_visible()

    elif expected_result == "Required":
        print("expected result" ,expected_result)
        assert login_page.get_required_fields().count() >= 1
    else:
        expect(login_page.get_error_message()).to_be_visible()
