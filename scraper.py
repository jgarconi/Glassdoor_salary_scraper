import time
import json
import pandas as pd
import re
import Salary
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# INSPIRAÇÃO: https://github.com/arapfaik/scraping-glassdoor-selenium/blob/master/glassdoor%20scraping.ipynb
# https://github.com/ashalan/glassdoor-salary-scraper/blob/master/scraper.py
# https://github.com/williamxie11/glassdoor-interview-scraper/blob/master/scraper_v1.2.py

username = # your email here
password = # your password here

# Manual options for the company, num pages to scrape, and URL
#pages = 6
#companyName = "rede_bahia"
#companyURL = "https://www.glassdoor.com.br/Salário/Rede-Bahia-Salários-E2485970.htm"
loginURL = "http://www.glassdoor.com/profile/login_input.htm"
salaries = []

def obj_dict(obj):
    return obj.__dict__

def init_driver():
    service = Service(executable_path = "/usr/lib/chromium-browser/chromedriver")
    driver = webdriver.Chrome(service=service)
    driver.wait = WebDriverWait(driver, 10)
    return driver

def login(driver, username, password, loginURL):
    driver.get(loginURL)
    try:
		# Wait for first login page load
        element = driver.wait.until(EC.presence_of_element_located(
            (By.ID, "inlineUserEmail")))
        time.sleep(.1)
            
		# Input the username and password
        user_input = driver.find_element(By.ID, "inlineUserEmail")    
        user_input.send_keys(username)
        time.sleep(.1)
        
        continue_button = driver.find_element(By.CLASS_NAME, "emailButton")
        continue_button.click()
        time.sleep(2)
        
        pw_input = driver.find_element(By.ID, "inlineUserPassword")
        pw_input.send_keys(password)
        time.sleep(.1)

        login_button = driver.find_element(By.CLASS_NAME, "emailButton")
        login_button.click()
        time.sleep(2)
        
		# Input the username and password in the second login page
        user_input = driver.find_element(By.ID, "inlineUserEmail")    
        user_input.send_keys(username)
        time.sleep(.1)
        
        continue_button = driver.find_element(By.CLASS_NAME, "emailButton")
        continue_button.click()
        time.sleep(2)
        
        pw_input = driver.find_element(By.ID, "inlineUserPassword")
        pw_input.send_keys(password)
        time.sleep(.1)
        
        login_button = driver.find_element(By.CLASS_NAME, "emailButton")
        login_button.click()
        time.sleep(2)
        
    except TimeoutException:
        print("TimeoutException! Username/password field or login button not found on glassdoor.com")
        
def load_page(driver, URL, startPage, refresh):
	currentURL = URL + "_P" + str(startPage) + ".htm"

	if (refresh):
		driver.get(currentURL)
		print("Getting " + currentURL)
		time.sleep(2)
      
		try:
			dropdown = driver.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@data-test-id, 'pay-period-Pagamento anual')]")))

			# Execute o código JavaScript para clicar no elemento
			driver.execute_script("arguments[0].click();", dropdown)
			
			option = driver.wait.until(EC.presence_of_element_located(
				(By.XPATH, "//button[contains(@data-test-id, 'data-select-value-Pagamento mensal')]")))
			option.click()

		except TimeoutException:
			print("TimeoutException! Button not found on glassdoor.com")
	
def get_data(driver, URL, startPage, endPage, salaries, refresh):
	pages_failed = []

	for page in range(startPage, endPage + 1):
		try:
			load_page(driver, URL, page, refresh)
			time.sleep(3)
		
			# Encontra a tabela com o XPath fornecido
			tabela = driver.find_element(By.XPATH, '/html/body/div[3]/div/main/section[1]/table')

			# Encontra todas as linhas (tr) da tabela, exceto a primeira que contém os cabeçalhos
			linhas = tabela.find_elements(By.XPATH, './tbody/tr[position() > 1]')

			# Itera sobre cada linha da tabela
			for linha in linhas:
				# Extrai o cargo do primeiro elemento da linha (td)
				cargo = linha.find_element(By.XPATH, './td[1]/a').text.strip()
				# Extrai a amostragem do primeiro elemento da linha (td)
				num_envios = linha.find_element(By.XPATH, './td[1]/p').text.strip()
				quantidade = re.search(r'\d+', num_envios)
				amostragem = quantidade.group(0)
				# Extrai o salário do segundo elemento da linha (td)
				if amostragem == "1":
					sal_completo = linha.find_element(By.XPATH, './td[2]/p').text.strip()
					if 'R$' in sal_completo:
						try:
							sal_min, sal_max = map(float, sal_completo.replace("R$ ", "").replace(" mil", "000").split("-"))
							salario = (sal_min + sal_max)/2
							bonus = 0.0
						except:
							print("Erro ao converter string para float. Pulando linha.")
							continue
					else:
						continue
				else:
					sal_completo = linha.find_element(By.XPATH, './td[2]/p[2]').text.strip()
					if "R$" in sal_completo:
						try:
							sal_mil = sal_completo.replace(" mil", "000")
							div_sal = sal_mil.split('|')
							salario = float(div_sal[0].split()[1])
							bonus = float(div_sal[1].split()[1])
						except:
							print("Erro ao converter string para float. Pulando linha.")
							continue
					else:
						continue

				salaries.append({"Cargo": cargo, "Amostragem": amostragem, "Salário": salario, "Bônus": bonus})
		
		except NoSuchElementException:
			pages_failed.append(page)
			print(f"Failed to extract data from page {page}. Skipping to the next page.")

	if pages_failed:
		print(f"Failed to extract data from the following pages: {', '.join(map(str, pages_failed))}")
	else:
		print("Todos os dados foram extraídos com sucesso!")

	return pd.DataFrame(salaries)

if __name__ == "__main__":
	with open("emissoras.txt", "r") as file:
		lines = file.readlines()

	for line in lines:
		companyName, url, pages = line.strip().split(",")
		pages = int(pages)

		driver = init_driver()
		time.sleep(3)

		print("Logging into Glassdoor account ...")
		login(driver, username, password, loginURL)
		time.sleep(5)

		print(f"Starting data scraping for {url} ...")
		df = get_data(driver, url[:-4], 1, pages, [], True)
		time.sleep(2)

		print(f"Exporting table for {url} to salarios_{companyName}.csv")
		df.to_csv(f"salarios_{companyName}.csv", index=False)
		print(f"Terminating execution for {companyName} in 5 seconds ...")
		time.sleep(5)

		driver.quit()
#endif