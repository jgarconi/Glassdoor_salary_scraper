import time
import json
import Salary
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

username = "" # your email here
password = "" # your password here

# Manual options for the city, num pages to scrape, and URL
pages = 6
cityName = "new-york-city"
cityURL = "https://www.glassdoor.com/Salaries/new-york-city-data-scientist-salary-SRCH_IL.0,13_IM615_KO14,28.htm"

def obj_dict(obj):
    return obj.__dict__
#enddef

def json_export(data):
	jsonFile = open(cityName + ".json", "w")
	jsonFile.write(json.dumps(data, indent=4, separators=(',', ': '), default=obj_dict))
	jsonFile.close()
#enddef

def init_driver():
    driver = webdriver.Chrome(executable_path = "./chromedriver")
    driver.wait = WebDriverWait(driver, 10)
    return driver
#enddef

def login(driver, username, password):
    driver.get("http://www.glassdoor.com/profile/login_input.htm")
    try:
        user_field = driver.wait.until(EC.presence_of_element_located(
            (By.NAME, "username")))
        pw_field = driver.find_element_by_class_name("signin-password")
        login_button = driver.find_element_by_id("signInBtn")
        user_field.send_keys(username)
        user_field.send_keys(Keys.TAB)
        time.sleep(1)
        pw_field.send_keys(password)
        time.sleep(1)
        login_button.click()
    except TimeoutException:
        print("TimeoutException! Username/password field or login button not found on glassdoor.com")
#enddef

def parse_salaries_HTML(salaries, data):
	for salary in salaries:
		jobTitle = "-"
		company = "-"
		meanPay = "-"
		jobTitle = salary.find("a", { "class" : "jobTitle"}).getText().strip()
		company = salary.find("div", { "class" : "i-emp"}).getText().strip()
		try:
			meanPay = salary.find("div", { "class" : "meanPay"}).find("strong").getText().strip()
		except:
			meanPay = 'xxx'
		r = Salary.Salary(jobTitle, company, meanPay)
		data.append(r)
	#endfor
	return data
#enddef

def get_data(driver, URL, startPage, endPage, data, refresh):
	if (startPage > endPage):
		return data
	#endif
	print "\nPage " + str(startPage) + " of " + str(endPage)
	currentURL = URL + "_IP" + str(startPage) + ".htm"
	time.sleep(2)
	#endif
	if (refresh):
		driver.get(currentURL)
		print "Getting " + currentURL
	#endif
	time.sleep(2)
	HTML = driver.page_source
	soup = BeautifulSoup(HTML, "html.parser")
	salaries = soup.find("div", { "class" : ["salaryChartModule"] }).find_all("div", { "class" : ["salaryRow"] })
	if (salaries):
		data = parse_salaries_HTML(salaries, data)
		print "Page " + str(startPage) + " scraped."
		if (startPage % 10 == 0):
			print "\nTaking a breather for a few seconds ..."
			time.sleep(10)
		#endif
		get_data(driver, URL, startPage + 1, endPage, data, True)
	else:
		print "Waiting ... page still loading or CAPTCHA input required"
		time.sleep(3)
		get_data(driver, URL, startPage, endPage, data, False)
	#endif
	return data
#enddef

if __name__ == "__main__":
	driver = init_driver()
	time.sleep(3)
	print "Logging into Glassdoor account ..."
	login(driver, username, password)
	time.sleep(10)
	print "\nStarting data scraping ..."
	data = get_data(driver, cityURL[:-4], 1, pages, [], True)
	print "\nExporting data to " + cityName + ".json"
	json_export(data)
	driver.quit()
#endif
