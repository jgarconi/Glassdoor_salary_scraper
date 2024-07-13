import time
import json
import Salary
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

username = # your email here
password = # your password here

# Manual options for the company, num pages to scrape, and URL
pages = 1
companyName = "globo"
companyURL = "https://www.glassdoor.com.br/Salário/Globo-Salários-E321393.htm"

def obj_dict(obj):
    return obj.__dict__

def json_export(data):
	jsonFile = open(companyName + ".json", "w")
	jsonFile.write(json.dumps(data, indent=4, separators=(',', ': '), default=obj_dict))
	jsonFile.close()

def init_driver():
    service = Service(executable_path = "/usr/lib/chromium-browser/chromedriver")
    driver = webdriver.Chrome(service=service)
    driver.wait = WebDriverWait(driver, 10)
    return driver

def login(driver, username, password):
    driver.get("http://www.glassdoor.com/profile/login_input.htm")
    try:
        element = driver.wait.until(EC.presence_of_element_located(
            (By.ID, "inlineUserEmail")))
        time.sleep(2)
            
        user_input = driver.find_element(By.ID, "inlineUserEmail")    
        user_input.send_keys(username)
        time.sleep(2)
        
        continue_button = driver.find_element(By.CLASS_NAME, "emailButton")
        continue_button.click()
        time.sleep(2)
        
        pw_input = driver.find_element(By.ID, "inlineUserPassword")
        pw_input.send_keys(password)
        time.sleep(2)

        login_button = driver.find_element(By.CLASS_NAME, "emailButton")
        login_button.click()
        time.sleep(2)
        
        user_input = driver.find_element(By.ID, "inlineUserEmail")    
        user_input.send_keys(username)
        time.sleep(2)
        
        continue_button = driver.find_element(By.CLASS_NAME, "emailButton")
        continue_button.click()
        time.sleep(2)
        
        pw_input = driver.find_element(By.ID, "inlineUserPassword")
        pw_input.send_keys(password)
        time.sleep(2)
        
        login_button = driver.find_element(By.CLASS_NAME, "emailButton")
        login_button.click()
        time.sleep(2)
        
    except TimeoutException:
        print("TimeoutException! Username/password field or login button not found on glassdoor.com")
        
def get_period():
    try:
        dp_button = driver.find_element(By.CLASS_NAME, "filter-chip_FilterChip__kAbKx filter-chip_FilterChipSelected__uNi3m")
        dp_button.click()
        time.sleep(1)
        
        period_button = driver.find_element(By.ID, "data-selected-value-Pagamento mensal")
        period_button.click()
        time.sleep(1)
    except NoSuchElementException:
        print("Cannot choose payment period.")

def parse_reviews_HTML(reviews, data):
	for review in reviews:
		length = "-"
		gotOffer = "-"
		experience = "-"
		difficulty = "-"
		date = review.find("time", { "class" : "date" }).getText().strip()
		role = review.find("span", { "class" : "reviewer"}).getText().strip()
		outcomes = review.find_all("div", { "class" : ["tightLt", "col"] })
		if (len(outcomes) > 0):
			gotOffer = outcomes[0].find("span", { "class" : "middle"}).getText().strip()
		#endif
		if (len(outcomes) > 1):
			experience = outcomes[1].find("span", { "class" : "middle"}).getText().strip()
		#endif
		if (len(outcomes) > 2):
			difficulty = outcomes[2].find("span", { "class" : "middle"}).getText().strip()
		#endif
		appDetails = review.find("p", { "class" : "applicationDetails"})
		if (appDetails):
			appDetails = appDetails.getText().strip()
			tookFormat = appDetails.find("took ")
			if (tookFormat >= 0):
				start = appDetails.find("took ") + 5
				length = appDetails[start :].split('.', 1)[0]
			#endif
		else:
			appDetails = "-"
		#endif
		details = review.find("p", { "class" : "interviewDetails"})
		if (details):
			s = details.find("span", { "class" : ["link", "moreLink"] })
			if (s):
				s.extract() # Remove the "Show More" text and link if it exists
			#endif
			details = details.getText().strip()
		#endif
		questions = []
		qs = review.find_all("span", { "class" : "interviewQuestion"})
		if (qs):
			for q in qs:
				s = q.find("span", { "class" : ["link", "moreLink"] })
				if (s):
					s.extract() # Remove the "Show More" text and link if it exists
				#endif
				questions.append(q.getText().encode('utf-8').strip())
			#endfor
		#endif
		r = Review.Review(date, role, gotOffer, experience, difficulty, length, details, questions)
		data.append(r)
	#endfor
	return data
#enddef

def get_data(driver, URL, startPage, endPage, data, refresh):
	if (startPage > endPage):
		return data
	#endif
	print("\nPage " + str(startPage) + " of " + str(endPage))
	currentURL = URL + "_IP" + str(startPage) + ".htm"
	time.sleep(2)
	#endif
	if (refresh):
		driver.get(currentURL)
		print("Getting " + currentURL)
	#endif
	time.sleep(2)
	HTML = driver.page_source
	soup = BeautifulSoup(HTML, "html.parser")
	reviews = soup.find_all("li", { "class" : ["empReview", "padVert"] })
	if (reviews):
		data = parse_reviews_HTML(reviews, data)
		print("Page " + str(startPage) + " scraped.")
		if (startPage % 10 == 0):
			print("\nTaking a breather for a few seconds ...")
			time.sleep(10)
		#endif
		get_data(driver, URL, startPage + 1, endPage, data, True)
	else:
		print("Waiting ... page still loading or CAPTCHA input required")
		time.sleep(3)
		get_data(driver, URL, startPage, endPage, data, False)
	#endif
	return data
#enddef

if __name__ == "__main__":
	driver = init_driver()
	time.sleep(3)
	print("Logging into Glassdoor account ...")
	login(driver, username, password)
	time.sleep(5)
	print("Choosing payment period ...")
	get_period()
	time.sleep(3)
	print("\nStarting data scraping ...")
	data = get_data(driver, companyURL[:-4], 1, pages, [], True)
	print("\nExporting data to " + companyName + ".json")
	json_export(data)
	driver.quit()
#endif
