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
from utils import init_driver, login, scrape_data

LOGIN_URL = "http://www.glassdoor.com/profile/login_input.htm"
USERNAME = credentials.get('USERNAME')
PASSWORD = credentials.get('PASSWORD')

if __name__ == "__main__":
    with open("companies.txt", "r") as file:
        lines = file.readlines()

    for line in lines:
        # Ignore comments and blank lines in companies.txt
        if line.startswith('#') or line.strip() == "":
            continue

        company_name, url, start_page, end_page = parts
        start_page = int(start_page)
        end_page = int(end_page)

        if start_page > end_page:
            print("The first page can't be bigger than the last page. Skipping company.")
            continue

        driver = init_driver()
        time.sleep(2)

        print("Logging into Glassdoor account ...")
        login(driver, USERNAME, PASSWORD, LOGIN_URL)
        time.sleep(5)

        print(f"Starting data scraping for {url} ...")
        df = scrape_data(driver, url[:-4], start_page, end_page, [], True)
        time.sleep(2)

        print(f"Exporting table from {url} to {company_name}_salaries.csv")
        df.to_csv(f"{company_name}_salaries.csv", index=False)
        print(f"Terminating execution for {company_name} salary scraping in 5 seconds ...")
        time.sleep(5)

        driver.quit()
