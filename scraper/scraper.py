import csv
import pprint
import logging
import requests
from bs4 import BeautifulSoup
from dataclasses import asdict
from models import Headphone, InEarMonitor

logging.basicConfig(filename="logs.log", level=logging.INFO)
# truncating log file before new run
with open("logs.log", "w"):
    pass


class Scraper:
    """
    Encapsulates all the logic for the web scraper.
    """

    def __init__(self) -> None:
        self.base_url = "https://crinacle.com/rankings/"

    def convert_to_model(self, device_data: list[dict], device_type: str) -> list:
        """Converts list of dictionary to their respective list of model type

        Args:
            device_data (list[dict]): List of dictionaries containing each device
            device_type (str): String specifiying the type of device: headphones or iems

        Returns:
            list: List containing the dictionaries converted to the specific model type
        """
        if device_type == "headphones":
            converted_data = [Headphone(device) for device in device_data]
        else:
            converted_data = [InEarMonitor(device) for device in device_data]

        return converted_data

    def scrape(self, device_type: str) -> list[dict]:
        """
        Scrapes Crinacle's databases containing technical information about Headphones and IEMs.

        Args:
            device_type (str): specifies the device type and url to be scraped.
        """
        url = self.base_url + device_type
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            logging.log(e)

        # Find all tables within page, in this case, the only one
        data_table = soup.findChildren("table")[0]

        # Get all the headers for the table
        thead = data_table.find_all("thead", recursive=False)
        headers = thead[0].findChildren("th")
        headers = [cell.text for cell in headers]

        # Get all rows within the table (excluding links)
        tbody = data_table.find_all("tbody", recursive=False)
        rows = tbody[0].find_all("tr", recursive=False)

        device_data = []

        for row in rows:
            row_data = {}
            for i, cell in enumerate(row.find_all("td", recursive=False)):
                row_data[headers[i]] = cell.get_text()
            device_data.append(row_data)

        device_data = self.convert_to_model(device_data=device_data, device_type=device_type)
        return device_data

    def convert_to_csv(self, device_data: list[dict], device_type: str) -> None:
        """Converts a list of dictionaries to a csv file

        Args:
            device_data (list[dict]): List of dictionaries containing each device
            device_type (str): String specifiying the type of device: headphones or iems
        """
        with open(f"{device_type}.csv", "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=device_data[0].keys())
            writer.writeheader()
            writer.writerows(device_data)


if __name__ == "__main__":
    scraper = Scraper()
    headphones = scraper.scrape(device_type="headphones")
    headphones = [asdict(headphone) for headphone in headphones]

    iems = scraper.scrape(device_type="iems")
    iems = [asdict(iem) for iem in iems]

    scraper.convert_to_csv(device_data=headphones, device_type="headphones")
    scraper.convert_to_csv(device_data=iems, device_type="iems")
