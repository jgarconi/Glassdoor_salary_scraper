"""
Author: Juliana Garçoni dos Santos
Date of Modification: 13-07-2024
GitHub: https://github.com/jgarconi

Description:
Utility functions for Glassdoor web scraping.
"""

# Standard library imports
import time  # For time-related functions
import re  # For regular expression operations

# Third-party imports
import pandas as pd  # For data manipulation and analysis
from selenium import webdriver  # For web browser automation
from selenium.webdriver.chrome.service import Service  # For managing ChromeDriver service
from selenium.webdriver.common.by import By  # For locating elements
from selenium.webdriver.support.ui import WebDriverWait  # For waiting until conditions are met
from selenium.webdriver.support import expected_conditions as EC  # For defining expected conditions
from selenium.common.exceptions import TimeoutException, NoSuchElementException  # For handling specific exceptions

# Init chrome driver
def init_driver():
    service = Service(executable_path = "/usr/lib/chromium-browser/czhromedriver")
    driver = webdriver.Chrome(service=service)
    driver.wait = WebDriverWait(driver, 10)
    return driver

# Login process
def login(driver, username, password, login_url):
    driver.get(login_url)
    try:
		# Wait for first login page load
        driver.wait.until(EC.presence_of_element_located((By.ID, "inlineUserEmail")))
        time.sleep(.1)
            
		# Find the field and input the username
        user_input = driver.find_element(By.ID, "inlineUserEmail")    
        user_input.send_keys(username)
        time.sleep(.1)
        
        # Find and click the continue botton
        continue_button = driver.find_element(By.CLASS_NAME, "emailButton")
        continue_button.click()
        time.sleep(2)
        
        # Find the field and input the password
        password_input = driver.find_element(By.ID, "inlineUserPassword")
        password_input.send_keys(password)
        time.sleep(.1)

        # Find and click the login button
        login_button = driver.find_element(By.CLASS_NAME, "emailButton")
        login_button.click()
        time.sleep(2)
        
		# Repeat the process in the second login page
        user_input = driver.find_element(By.ID, "inlineUserEmail")    
        user_input.send_keys(username)
        time.sleep(.1)
        
        continue_button = driver.find_element(By.CLASS_NAME, "emailButton")
        continue_button.click()
        time.sleep(2)
        
        password_input = driver.find_element(By.ID, "inlineUserPassword")
        password_input.send_keys(password)
        time.sleep(.1)
        
        login_button = driver.find_element(By.CLASS_NAME, "emailButton")
        login_button.click()
        time.sleep(2)
        
    except TimeoutException:
        print("TimeoutException! Username/password field or login button not found on glassdoor.com.br")

# Load company page and select pay period monthly
def load_page(driver, url, startPage, refresh):
    current_url = url + "_P" + str(startPage) + ".htm"

    if refresh:
        driver.get(current_url)
        print("Getting " + current_url)
        time.sleep(2)

        try:
            # Wait for the dropdown menu to be present
            dropdown = driver.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@data-test-id, 'pay-period-Pagamento anual')]")))

            # Execute JavaScript to click on the dropdown
            driver.execute_script("arguments[0].click();", dropdown)

            # Wait for the monthly pay period option to be present and click it
            option = driver.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[contains(@data-test-id, 'data-select-value-Pagamento mensal')]")))
            option.click()

        except TimeoutException:
            print("TimeoutException! Button not found on glassdoor.com")

# Data scrapping process
def scrap_data(driver, url, startPage, endPage, salaries, refresh):
	pages_failed = []
	salaries = []

    # Extract data from every page
	for page in range(startPage, endPage + 1):
		try:
			load_page(driver, url, page, refresh)
			time.sleep(3)
		
			# Find salary table
			table = driver.find_element(By.XPATH, '/html/body/div[3]/div/main/section[1]/table')

			# Find the table rows, except the first one that contains the headers
			rows = table.find_elements(By.XPATH, './tbody/tr[position() > 1]')

            # For every row found in the table rows
			for row in rows:
				# Extract the job title
				job_title = row.find_element(By.XPATH, './td[1]/a').text.strip()
				
				# Extract the number of salaries submitted
				salaries_submitted = row.find_element(By.XPATH, './td[1]/p').text.strip()
				submission_count = re.search(r'\d+', salaries_submitted).group(0)
				
				# Extract the mean salary and bonus as a float number
				if submission_count == "1":
					# Process to sigle salary submission
					salary_string = row.find_element(By.XPATH, './td[2]/p').text.strip()
					if 'R$' in salary_string:
						try:
							salary_min, salary_max = map(float, salary_string.replace("R$ ", "").replace(" mil", "000").split("-"))
							mean_salary = (salary_min + salary_max)/2
							bonus = 0.0
						except:
							print("Error converting string to float. Skipping row.")
							continue
					else:
						continue
				else:
					# Process to multiple salaries submission
					salary_string = row.find_element(By.XPATH, './td[2]/p[2]').text.strip()
					if "R$" in salary_string:
						try:
							salary_parts = salary_string.replace(" mil", "000").split('|')
							mean_salary = float(salary_parts[0].split()[1])
							bonus = float(salary_parts[1].split()[1])
						except:
							print("Error converting string to float. Skipping row.")
							continue
					else:
						continue

				salaries.append({"Cargo": job_title, "Salários Enviados": submission_count, "Salário Médio": mean_salary, "Bônus": bonus})
		
		except NoSuchElementException:
			pages_failed.append(page)
			print(f"Failed to extract data from page {page}. Skipping to the next page.")

	if pages_failed:
		print(f"Failed to extract data from the following pages: {', '.join(map(str, pages_failed))}")
	else:
		print("All data were extracted successfully!")

	return pd.DataFrame(salaries)

