import requests
import logging
class API_Server():
    url = None
    def __init__(self,url:str,username:str,password:str):
        self.url = url
        url_API = url + "/user/login"
        data = {
            "username": username,
            "password": password
            }
        logging.basicConfig(
            level=logging.NOTSET,
            format='${asctime}.$msecs - ${levelname} - ${name} - ${message}',
            datefmt="%a, %d %b %Y %H:%M:%S",
            style="$",
            filename="./log.txt",
            encoding="utf-8"
        )

        try:
            web = requests.post(url=url_API,data=data,)
            self.token = web.json()["data"]["token"]
        except BaseException as e:
            logging.error("登录报错 %s" % (e))
    def getDeWuGoods_API(self,status:int):
        url_API = self.url + "/goods/list"
        data = {
                "limit": 1,
                "minId": 0,
                "rules": {
                    "type": "鞋子",
                    "status": status
                }
            }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
            }
        try:
            
            web = requests.post(url=url_API,json=data,headers=headers,)
            data = web.json()["data"][0]
            return (data)
        except BaseException as e:
            logging.error("getDeWuGoods_API函数出错 %s" % (e))
    def setDeWuGoods_API_status(self,id:int,status:int):
        """
        0 - 未扫描
        1 - 已经被获取，未判决
        2 - 不符合条件
        3 - 符合条件，未上架
        4 - 符合条件，已上架
        """
        url_API = self.url+"/goods/updateGoods"
        data = {
            "id": id,
            "data": {
                "status": status
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
            }
        try:
            web = requests.post(url=url_API,json=data,headers=headers,)
        except BaseException as e:
            logging.error("setDeWuGoods_API_status函数出错 %s "% (e))
        # print(web.json())   
    def coverSize(self,sex:int,size_type:str,size:str):
        """
        尺码互相转换
        sex 0为女性 1为男性
        size_type 鞋码类型：EU goatUS二选一
        size 鞋子码

        返回转换后的码
        """
        url_API = self.url+"/coverSize"
        data = {
                "sex": sex,
                size_type: size
            }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
            }
        try:
            web = requests.post(url=url_API,json=data,headers=headers,)
            return web.json()["data"]
        except BaseException as e:
            logging.error("转换鞋码错误 %s %s" % (size,e))
            return None
