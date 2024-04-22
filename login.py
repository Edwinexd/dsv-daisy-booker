import requests
from bs4 import BeautifulSoup
import dotenv, os

from daisy import is_token_valid


def daisy_login(su_username: str, su_password: str):
    # Start a session to keep cookies
    session = requests.Session()

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,sv;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        # "Host": "daisy.dsv.su.se",
        # "Origin": "https://daisy.dsv.su.se",
        # "Referer": "https://daisy.dsv.su.se/common/schema/bokning.jspa",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        "sec-ch-ua": '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "X-Powered-By": "dsv-daisy-booker (https://github.com/Edwinexd/dsv-daisy-booker); Contact (edwin.sundberg@dsv.su.se)",
    }
    for key, value in headers.items():
        session.headers[key] = value

    # 1. Get the initial session cookie by visiting the main page
    session.get("https://daisy.dsv.su.se/index.jspa")

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
    post_response = session.post(action_url, data=form_data, headers={"Content-Type": "application/x-www-form-urlencoded", "Origin": "https://idp.it.su.se", "Referer": "https://idp.it.su.se/"}) # type: ignore
    
    # 4. Return the session cookie if login is successful
    return session.cookies.get_dict()


if __name__ == "__main__":
    dotenv.load_dotenv()
    su_username = os.getenv("SU_USERNAME", "")
    su_password = os.getenv("SU_PASSWORD", "")
    print(daisy_login(su_username, su_password))
