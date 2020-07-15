#!/usr/bin/python3
import os
from slack import WebClient
import ssl
import time
from selenium import webdriver
from slack.errors import SlackApiError
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def getProfile():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.privatebrowsing.autostart", True)
    profile.set_preference("geo.prompt.testing", True)
    profile.set_preference("geo.prompt.testing.allow", True)
    return profile


def postMessageOnSlack():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    client = WebClient(token=os.environ['SLACK_API_TOKEN'])

    try:
        response = client.chat_postMessage(
            channel='#status-update',
            text="CHECK IN")
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")


def main():
    browser = webdriver.Firefox(firefox_profile=getProfile())

    #browser shall call the URL
    browser.get("www.some-site-where-we-need-to-manually-login.com")
    delay = 5
    try:
        userName = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'UserName')))
        userName.send_keys(os.environ["WORK_EMAIL"])

        password = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'Password')))
        password.send_keys(os.environ["WORK_EMAIL_PASSWORD"])

        loginBtn = browser.find_element_by_css_selector(".btn-block")
        loginBtn.click()
        print("Successfully Logged In")

        attendance = browser.find_element_by_css_selector(".fa-calendar-o")
        attendance.click()

        manualAttendance = browser.find_element_by_css_selector(".fa-sign-in")
        manualAttendance.click()

        print("Add 10 seconds delay")
        time.sleep(10)
        print("Lets start you checking in")

        checkin_btn = WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.XPATH, "//button[@value='Check In']")))
        checkin_btn.click()

        postMessageOnSlack()
        print("Checked In successfully")

    except TimeoutException:
        print("Something is wrong with the Radiant Page")


if __name__ == "__main__":
    main()
