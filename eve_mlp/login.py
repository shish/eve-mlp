import requests
from urlparse import urljoin
import re
import logging


log = logging.getLogger(__name__)


LAUNCHER_INFO = 'http://client.eveonline.com/patches/win_launcherinfoTQ_inc.txt'


class LoginFailed(Exception):
    pass


def do_login(username, password):
    log.debug("Using cached SSO login URL")
    #login_action_url = get_login_action_url(LAUNCHER_INFO)
    login_action_url = "https://login.eveonline.com/Account/LogOn?" + \
        "ReturnUrl=%2Foauth%2Fauthorize%2F%3Fclient_id%3DeveLauncherTQ%26lang%3Den%26response_type%3Dtoken%26" + \
        "redirect_uri%3Dhttps%3A%2F%2Flogin.eveonline.com%2Flauncher%3Fclient_id%3DeveLauncherTQ%26scope%3DeveClientToken"

    access_token = submit_login(login_action_url, username, password)
    launch_token = get_launch_token(access_token)

    return launch_token


def get_login_action_url(launcher_url):
    from bs4 import BeautifulSoup
    import yaml

    # get general info
    launcher_info = yaml.load(requests.get(launcher_url))
    landing_url = launcher_info["UISettings"]["LandingPage"]
    landing_url = urljoin(launcher_url, landing_url)

    # load main launcher page
    landing_page = BeautifulSoup(requests.get(landing_url))
    login_url = landing_page.find(id="sso-frame").get("src")
    login_url = urljoin(landing_url, login_url)

    # load login frame
    login_page = BeautifulSoup(requests.get(login_url))
    action_url = login_page.find(name="form").get("action")
    action_url = urljoin(login_url, action_url)

    return action_url


def submit_login(action_url, username, password):
    log.info("Submitting username / password")

    auth_result = requests.post(
        action_url,
        data={"UserName": username, "Password": password},
        verify=False,
    )

    if "<title>License Agreement Update</title>" in auth_result.text:
        raise LoginFailed("Need to accept EULA")

    matches = re.search("#access_token=([^&]+)", auth_result.url)
    if not matches:
        raise LoginFailed("Invalid username / password?")
    return matches.group(1)


def get_launch_token(access_token):
    log.info("Fetching launch token")

    response = requests.get(
        "https://login.eveonline.com/launcher/token?accesstoken="+access_token,
        verify=False,
    )
    matches = re.search("#access_token=([^&]+)", response.url)
    if not matches:
        raise LoginFailed("No launch token?")
    return matches.group(1)
