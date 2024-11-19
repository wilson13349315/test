"""Utils for Selenium-based crawlers.

Author: Murilo Romera
"""

import glob
import os
import shutil
import time
from datetime import datetime, timedelta

from selenium import webdriver


class WebdriverUtils:
    """Utils for Selenium-based crawlers.

    Created by Murilo Romera
    """

    def initiate_driver(self, download_directory=None):
        """Initiates the Chrome webdriver with the standard settings.

        Parameters
        ----------
        download_directory : str
            (optional) Sets the default download directory.

        Returns
        -------
        WebDriver
            Chrome WebDriver with the default settings applied.

        """

        chrome_options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": download_directory}
        chrome_options.add_experimental_option("prefs", prefs)

        # Initiate selenium
        browser = webdriver.Chrome(options=chrome_options)
        return browser

    def wait_for_downloads(self, download_directory):
        """Waits for all downloads to be finished.

        Parameters
        ----------
        download_directory : str
            Download folder.

        """

        print("Waiting for downloads to be finished", end="")
        while any(
            [
                filename.endswith(".crdownload") or filename.endswith(".tmp")
                for filename in os.listdir(download_directory)
            ],
        ):
            time.sleep(2)
            print(".", end="")
        print("... Done.")

    def clear_download_folder(self, download_directory):
        """Clears the download folder from previous downloads.

        Parameters
        ----------
        download_directory : str
            Download folder.

        """

        for file in glob.glob(f"{download_directory}/*"):
            if os.path.isfile(file):
                os.remove(file)
            else:
                shutil.rmtree(file)

    def excel_date_to_datetime(self, xl_date):
        """Converts from Excel date ID to datetime.

        Parameters
        ----------
        xl_date : int
            Excel date code.

        Returns
        -------
        datetime
            The same date converted to datetime.

        """

        epoch = datetime(1899, 12, 30)
        delta = timedelta(hours=round(xl_date * 24))
        return epoch + delta

    def get_unpacked_folder_name(self, download_dir) -> str:
        """Returns the unpacked folder name. Unpacks it if not already unpacked.

        Parameters
        ----------
        download_dir : str
            Download folder.

        Returns
        -------
        str
            The unpacked folder name.

        """
        file = [filename for filename in os.listdir(download_dir) if ".zip" not in filename]

        if len(file):
            return file[0]

        downloaded_files = os.listdir(download_dir)
        shutil.unpack_archive(
            download_dir + "/" + downloaded_files[0],
            download_dir,
        )

        return [filename for filename in os.listdir(download_dir) if ".zip" not in filename][0]
