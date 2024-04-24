from selenium import webdriver
from API.API_selenium import login,getPriceBySlug,getSlugBySku
from API.API_Server import API_Server
from API.API_Mysql import API_Mysql
from tqdm import tqdm
import multiprocessing
# from tqdm.contrib import multiprocessing
import logging
import time
import threading
logging.basicConfig(
            level=logging.ERROR,
            format='${asctime}.$msecs - ${levelname} - ${name} - ${message}',
            datefmt="%a, %d %b %Y %H:%M:%S",
            style="$",
            filename="./log.txt",
            encoding="utf-8"
        )
lock = threading.Lock()

def worker_login():
    # 定义要连接的 Selenium Grid 节点的 URL
    global pbar
    global driver_list
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
    chrome_options.add_argument('--proxy-server=http://192.168.100.231:10809')
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    chrome_options.add_argument('--ignore-urlfetcher-cert-requests')
    chrome_options.add_argument("--enable-chrome-browser-cloud-management")
    # 创建浏览器驱动程序
    driver = webdriver.Remote(command_executor=grid_url, options=chrome_options)
    login(driver)
    pbar.update(1)
    lock.acquire()
    try:
        driver_list.append(driver)
    finally:
        lock.release()
def worker(driver):
    global pbar
    global num
    global stop_num
    global fuhe
    # global apis
    apis = API_Mysql()
    while True:
        try:
            goods_data = apis.getDeWuGoods_API() # 获取一个未被检测的
            id = goods_data['id']
            size = goods_data['size']
            sku = goods_data['sku']
            price = goods_data['price']
            apis.setDeWuGoods_API_status(id=id,status=1)
            size = float(size)
            if (price==None):
                logging.info("本地数据库未有报价，忽略")
                apis.setDeWuGoods_API_status(id=id,status=2)
                raise BaseException
        except BaseException as e:
            logging.error("1 - %s" % (e))
            with lock:
                num += 1
                if (num>=stop_num):
                    return
                pbar.update(1)
            continue
            
        
        try:
            slug_list = getSlugBySku(driver=driver,sku=sku)
            if (slug_list==[]):
                logging.info("SKU: 本地型号：%s alias未查到相应的型号" % (sku))
                apis.setDeWuGoods_API_status(id=id,status=2)
                raise BaseException
            if ("wmns" in slug_list[0]):
                # logging.info(slug_list)
                g_size = apis.coverSize(sex=0,size_type="EU",size=size)
            else:
                g_size = apis.coverSize(sex=1,size_type="EU",size=size)
            logging.info(slug_list)
            if (g_size==None):
                raise BaseException
        except BaseException as e:
            logging.error("2 - %s" % (e))
            with lock:
                num += 1
                if (num>=stop_num):
                    return
                pbar.update(1)
            continue
        

        try:
            price_Json = getPriceBySlug(driver=driver,slug=slug_list[0],size=g_size)
            lowestPriceCents = price_Json["lowestPriceCents"]
            if (lowestPriceCents == None):
                logging.info("SKU: %s 不符合条件，价格获取为空" % (sku))
                apis.setDeWuGoods_API_status(id=id,status=2)
                continue
            chajia = ((lowestPriceCents / 100 * 7.19 )-float(price))
            if ( chajia> 20):
                logging.info("符合条件 鞋号%s 价位：%sUSD => %sRMB - 得物价位：%sRMB  SIZE: %s=>%s" % (sku,(lowestPriceCents/100),(lowestPriceCents / 100 * 7.19),price,size,g_size))
                apis.setDeWuGoods_API_status(id=id,status=3)
                fuhe += 1
            else:
                logging.info("价钱不符合条件 %s 差价：%s" % (lowestPriceCents,chajia))
                apis.setDeWuGoods_API_status(id=id,status=2)
                continue
            driver.refresh()
        except BaseException as e:
            logging.error("3 - %s" % (e))
            with lock:
                num += 1
                if (num>=stop_num):
                    return
                pbar.update(1)
            continue

def multiprocess_func(webdriver):
    pass


        

if __name__=="__main__":

    num = 0
    fuhe = 0
    stop_num = 500
    driver_list = []
    max_node = 8 # 最大的node位置
    with tqdm(total=max_node) as pbar:
        pbar.set_description("登录进度")
        threading_list = []
        for i in range(max_node):
            a = threading.Thread(target=worker_login)
            a.start()
            threading_list.append(a)
        for i in threading_list:
            i.join()

    try:
        start_time = time.time()
        with tqdm(total=stop_num) as pbar:
            pbar.set_description("进度条")
            threading_list = []
            for i in driver_list:
                time.sleep(1)
                a = threading.Thread(target=worker,args=(i,))
                a.start()
                threading_list.append(a)
            for i in threading_list:
                i.join()
        print (time.time()-start_time)
        print ("程序执行完毕 共扫描：%s 商品 %s个符合条件的商品 用时：%s s" %(stop_num,fuhe,time.time()-start_time) )
    except BaseException as e:
        print("错误 %s" % (e))
    finally:
        for i in driver_list:
            i.quit()


    