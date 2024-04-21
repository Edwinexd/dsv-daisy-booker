import requests
from bs4 import BeautifulSoup


def daisy_login(su_username: str, su_password: str):
    # Start a session to keep cookies
    session = requests.Session()

    # 1. Get the initial session cookie by visiting the main page
    session.get(
        "https://daisy.dsv.su.se/index.jspa",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
            "X-Powered-By": "dsv-daisy-booker (https://github.com/Edwinexd/dsv-daisy-booker); Contact (edwin.sundberg@dsv.su.se)",
        },
    )

    # 2. Navigate to the login URL which may be needed to retrieve further login form details
    login_response = session.get(
        "https://daisy.dsv.su.se/Shibboleth.sso/Login?entityID=https://idp.it.su.se/idp/shibboleth&target=https://daisy.dsv.su.se/login_sso_student.jspa"
    )

    # Parse the form action URL and other necessary parameters from the login page
    soup = BeautifulSoup(login_response.text, "html.parser")
    # This depends heavily on the actual form structure and might need to be adjusted
    form = soup.find("form")
    form_data = {tag["name"]: tag.get("value", "") for tag in form.find_all("input")} # type: ignore

    # Add username and password to the form data
    form_data.update(
        {"j_username": su_username, "j_password": su_password, "_eventId_proceed": ""}
    )

    form_data.pop("_eventId_authn/SPNEGO")

    # 3. Submit the login form
    action_url = (
        login_response.url.split(";")[0]
        + "?"
        + login_response.url.split(";")[1].split("?")[1]
    )

    post_response = session.post(action_url, data=form_data)

    assert post_response.ok

    # Parse with BeautifulSoup and get RelayState and SAMLResponse to submit the form
    soup = BeautifulSoup(post_response.text, "html.parser")

    form = soup.find("form")
    # (form data is placed in hidden input fields)
    form_data = {
        tag.get("name"): tag.get("value")
        for tag in form.find_all("input")
        if tag.get("name") and tag.get("value")
    } # type: ignore

    # Submit the form
    action_url = form["action"] # type: ignore
    post_response = session.post(action_url, data=form_data) # type: ignore

    # 4. Return the session cookie if login is successful
    return session.cookies.get_dict()
