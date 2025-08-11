# Libraries
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os


def initiate_driver(headless=False, download_directory=None):
    """
    Initiate selenium webdriver with optimized parameters

    Parameters
    ----------
    headless : bool, optional
        Option to open chrome in headless mode, by default False

    Returns
    -------
    driver : selenium webdriver
        Selenium webdriver with chrome driver manager.
    """
    chrome_options = webdriver.ChromeOptions()

    if not download_directory:
        download_directory = os.path.abspath("")

    prefs = {
        "download.default_directory": download_directory,
        # "profile.managed_default_content_settings.images": 2,
        # "profile.default_content_setting_values.notifications": 2,
        # "profile.managed_default_content_settings.stylesheets": 2,
        # "profile.managed_default_content_settings.cookies": 2,
        # "profile.managed_default_content_settings.javascript": 1,
        # "profile.managed_default_content_settings.plugins": 1,
        # "profile.managed_default_content_settings.popups": 2,
        # "profile.managed_default_content_settings.geolocation": 2,
        # "profile.managed_default_content_settings.media_stream": 2,
    }  # Settings speeds up selenium to avoid loading images and other stuff

    # Other optimization options
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("enable-automation")
    chrome_options.add_argument(
        '--user-agent=""Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36""'
    )

    if headless:
        chrome_options.add_argument("--headless")

    # Start driver with all options
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    return driver