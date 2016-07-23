from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Create a new instance of the Firefox driver
#driver = webdriver.PhantomJS(executable_path='/Users/Antonio/node_modules/phantomjs/lib/phantom/bin/phantomjs')
driver = webdriver.Firefox()
# go to the google home page
driver.get("http://www.reclameaqui.com.br/busca/?q=samsung")

try:
    # we have to wait for the page to refresh, the last thing that seems to be updated is the title
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.business-name .ng-binding')))

    # You should see "cheese! - Google Search"
   # print(driver.page_source)
    soupBusca = BeautifulSoup(driver.page_source, "lxml")
    empresaUrl = soupBusca.select('.business-name .ng-binding')[0]['href']
    empresaUrlComp = 'http://www.reclameaqui.com.br'+empresaUrl

    driver.get(empresaUrlComp)

    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#n3-pie-arcs')))
        soupEmpresa = BeautifulSoup(driver.page_source, "lxml")
        reclamacoes = soupEmpresa.select('.all-complaints p')[0].get_text()
        print('reclamações:', reclamacoes)

    finally:
        driver.quit()

finally:
    driver.quit()
