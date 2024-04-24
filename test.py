from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# 您的代理设置
proxy_ip = "172.65.64.112"  # 代理服务器IP
proxy_port = "13192"        # 代理服务器端口
proxy_user = "ada240"        # 代理用户名
proxy_pass = "84ac37fd"    # 代理密码

# Selenium Grid服务器地址
grid_url = "http://127.0.0.1:4444/wd/hub"

# 设置Chrome选项
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("enable-automation")
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1366,768")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--dns-prefetch-disable")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(f"--proxy-server=socks5://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}")

# 将Chrome选项转换为字典格式的能力设置
# capabilities = chrome_options.to_capabilities()

# 创建远程WebDriver实例
driver = webdriver.Remote(
    command_executor=grid_url,
    options=chrome_options 
)
driver.get("https://baidu.com")
# print (help(driver))
print (driver.title)

# ...您的测试代码...
# driver.quit()
 # 使用options参数而不是desired_capabilities