"""
Author: Juliana Garçoni dos Santos
Date of Modification: 13-07-2024
GitHub: https://github.com/jgarconi

Description:
Main script for running the Glassdoor web scraping and data processing.
"""

# Standard library imports
import time  # For time-related functions

# Local imports
from credentials import credentials
from utils import init_driver, login, scrap_data

LOGIN_URL = "http://www.glassdoor.com/profile/login_input.htm"

username = credentials.get('USERNAME')
password = credentials.get('PASSWORD')
        
if __name__ == "__main__":
	with open("companies.txt", "r") as file:
		lines = file.readlines()

	for line in lines:
		company_name, url, last_page = line.strip().split(",")
		last_page = int(last_page)

		driver = init_driver()
		time.sleep(2)

		print("Logging into Glassdoor account ...")
		login(driver, username, password, LOGIN_URL)
		time.sleep(5)

		print(f"Starting data scraping for {url} ...")
		df = scrap_data(driver, url[:-4], 1, last_page, [], True)
		time.sleep(2)

		print(f"Exporting table from {url} to {company_name}_salaries.csv")
		df.to_csv(f"{company_name}_salaries.csv", index=False)
		print(f"Terminating execution for {company_name} salary crapping in 5 seconds ...")
		time.sleep(5)

		driver.quit()