from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
import json
import re
import time

def login(driver):
    # global driver
    try:
        driver.get("http://sell.alias.org")
        wait = WebDriverWait(driver, 5)
        element = wait.until(EC.visibility_of_element_located((By.ID,"onetrust-accept-btn-handler")))
        driver.find_element(By.ID,"onetrust-accept-btn-handler").click()
        driver.find_element(By.ID,"login").send_keys("账号")
        driver.find_element(By.ID,"password").send_keys("密码")
        driver.find_element(By.NAME,"alias-login-submit-btn").click()
        # #root > div.sc-fxFQKN.ejoSBg > main > div > form > div.sc-kizEQm.irzWzB
        # <div data-qa="login_error_text" class="sc-kizEQm irzWzB">Login attempt failed. Please check your credentials and try again.</div>
        # try:
        try:
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@data-qa='login_error_text']")))
            print ("[err]可能是由于IP原因导致无法登录：%s" % (element.text))
            return False
        except TimeoutException as e:
            # print ("[ok]登陆成功")
            return driver
    except:
        driver.refresh()
        login(driver)


def getSlugBySku(driver,sku):
    url = "https://2fwotdvm2o-3.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.10.3)%3B%20Browser%20(lite)%3B%20JS%20Helper%20(3.5.5)%3B%20react%20(17.0.2)%3B%20react-instantsearch%20(6.12.1)&x-algolia-api-key=241797425e84b6e9156307386e92d8af&x-algolia-application-id=2FWOTDVM2O"
    jsons = {"requests":[{"indexName":"product_variants_v2_trending_purchase","params":f"highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&attributes=%5B%22id%22%2C%22box_condition%22%2C%22direct_shipping%22%2C%22grid_glow_picture_url%22%2C%22grid_picture_url%22%2C%22instant_ship_lowest_price_cents%22%2C%22is_fashion_product%22%2C%22lowest_price_cents%22%2C%22name%22%2C%22product_category%22%2C%22product_template_id%22%2C%22product_type%22%2C%22release_date%22%2C%22resellable%22%2C%22shoe_condition%22%2C%22size%22%2C%22sku%22%2C%22slug%22%2C%22special_type%22%5D&facetFilters=%5B%5B%22product_category%3Ashoes%22%5D%5D&hitsPerPage=30&page=0&distinct=true&query={sku}&facets=%5B%5D&tagFilters="}]}
    # print(jsons)
    web = requests.post(url=url,json=jsons)
    rep_jsons = web.json()
    hits_list = rep_jsons['results'][0]['hits']
    slug_list = []
    for hit in hits_list:
        slug_list.append(hit['slug'])
    return slug_list

def getPriceBySlug(driver,slug,size):
    # global driver
    try:
        url = "https://sell.alias.org/api/v1/listings/%s/availability?id=%s&size=%s&consigned=false&packaging_condition=1&product_condition=1&region_id=223" % (slug,slug,size)
        driver.get(url=url)
        html_code = driver.page_source
        pattern = r'\{[^{}]+\}'
        match = re.search(pattern, html_code)

        if match:
            json_data = match.group()
            return json.loads(json_data)
        else:
            return "No JSON data found."
    except:
        getPriceBySlug(slug=slug,size=size)


def createOrder(driver,Slug,size,price):
    # 1. "https://sell.alias.org/list/campus-00s-black-white-gum-hq8708"
    # 取出网页的内容Set-Cookie：csrf
    # 2. "网页上新"
    #
    url = "https://sell.alias.org/list/%s" % (Slug)
    driver.get(url=url)
    csrf_cookie =  driver.get_cookie("csrf")['value']
    # 获取 Cookies
    cookies = driver.get_cookies()

    cookies_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
    js = """fetch("https://sell.alias.org/api/v1/listings/create-batch-listings", {
        "headers": {"accept": "application/json, text/plain, */*","accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/json;charset=UTF-8",
        "sec-ch-ua": "'Not A(Brand';v='99', 'Microsoft Edge';v='121',
        'Chromium';v='121'","sec-ch-ua-arch": "'x86'","sec-ch-ua-bitness": "'64'","sec-ch-ua-full-version": "'121.0.2277.83'",
        "sec-ch-ua-full-version-list": "'Not A(Brand';v='99.0.0.0', 'Microsoft Edge';v='121.0.2277.83', 'Chromium';v='121.0.6167.85'","sec-ch-ua-mobile": "?0","sec-ch-ua-model": "''","sec-ch-ua-platform": "'Windows'","sec-ch-ua-platform-version": "'15.0.0'","sec-fetch-dest": "empty","sec-fetch-mode": "cors","sec-fetch-site": "same-origin","x-csrf-token": "x-csrf-token-value","cookie": "cookies_str"},"referrerPolicy": "no-referrer",
        "body": '{\"listings\":[{\"priceCents\":8100_price,\"boxCondition\":\"good_condition\",\"shoeCondition\":\"new\",\"sizeUnit\":\"us\",\"sizeOption\":{\"value\":7_size},\"productId\":\"campus-00s-black-white-gum-hq8708\"}]}',"method": "POST"});""".replace("x-csrf-token-value",csrf_cookie).replace("cookies_str",cookies_str).replace("7_size",size).replace("8100_price",price).replace("campus-00s-black-white-gum-hq8708",Slug).replace("\n","")

    with open("2.js","w") as f:
        f.write(js)
        f.close()
    driver.execute_script(script=js)
    title = driver.execute_script('return document.title;')


if __name__=="__main__":
    grid_url = 'http://127.0.0.1:4444/wd/hub'
    # 定义要连接的节点的 ID
    node_id = 'f59d50ce-c280-4398-89bf-6be128aa3895'
    # 创建一个 ChromeOptions 对象
    chrome_options = webdriver.ChromeOptions()
    # 设置节点 ID
    chrome_options.add_argument(f"--node-id={node_id}")
    chrome_options.add_argument('--ignore-certificate-errors') #忽略CERT证书错误
    chrome_options.add_argument('--ignore-ssl-errors') #忽略SSL错误
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--proxy-server=http://192.168.100.138:10809')
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    chrome_options.add_argument('--ignore-urlfetcher-cert-requests')
    chrome_options.add_argument("--enable-chrome-browser-cloud-management")
    # 创建浏览器驱动程序
    driver = webdriver.Remote(command_executor=grid_url, options=chrome_options)
    login(driver)