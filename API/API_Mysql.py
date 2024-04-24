import pymysql
import logging
# from threading import Lock

class API_Mysql():
    MAN = {
        35.5: 3.5,
        36: 4,
        36.5: 4.5,
        37.5: 5,
        38: 5.5,
        38.5: 6,
        39: 6.5,
        40: 7,
        40.5: 7.5,
        41: 8,
        42: 8.5,
        42.5: 9,
        43: 9.5,
        44: 10,
        44.5: 10.5,
        45: 11,
        45.5: 11.5,
        46: 12,
        47.5: 13,
        48.5: 14
        }
    WOMAN = {
        35.5: 5,
        36: 5.5,
        36.5: 6,
        37.5: 6.5,
        38: 7,
        38.5: 7.5,
        39: 8,
        40: 8.5,
        40.5: 9,
        41: 9.5,
        42: 10,
        42.5: 10.5,
        43: 11,
        44: 11.5,
        45: 12,
        45.5: 12.5,
        46: 13
    }

    def __init__(self):
        """
        连接本地数据库
        """
        logging.basicConfig(
            level=logging.NOTSET,
            format='${asctime}.$msecs - ${levelname} - ${name} - ${message}',
            datefmt="%a, %d %b %Y %H:%M:%S",
            style="$",
            filename="./log.txt",
            encoding="utf-8"
        )
        
        self.username = "root"
        self.password = "password"
        self.database = "nike1"
        self.connection = pymysql.connect(
            host='127.0.0.1',
            user=self.username,
            password=self.password,
            database=self.database
        )
        # self.lock = Lock()
        

    def getDeWuGoods_API(self):
        """
        获取goods中符合条件status=0的条目一个
        {'id': 1, 'size': '42', 'sku': 'DM1290-401', 'price': '589'}
        """
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM goods WHERE status = 0 and price IS NOT NULL and type='鞋子' LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            data = {
                "id":result[0],
                "size":result[5],
                "sku":result[4],
                "price":result[7]
            }
            return data
        except BaseException as e:
            logging.error("getDeWuGoods_API -  %s" % (e))

    def setDeWuGoods_API_status(self, id, status):
        """
        传入id，更新goods中status中的值为设置的status
    
        0 - 未扫描
        1 - 已经被获取，未判决
        2 - 不符合条件
        3 - 符合条件，未上架
        4 - 符合条件，已上架
        """
        try:
            cursor = self.connection.cursor()
            query = f"UPDATE goods SET status = {status} WHERE id = {id}"
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
        except BaseException as e:
            logging.error("setDeWuGoods_API_status - %s" % (e))

    def coverSize(self,sex,size_type,size):
        """
        转换鞋子的码
        返回None或者转换后的代码
        """
        try:
            if (sex==0):
                return self.MAN[size]
            elif (sex==1):
                return self.WOMAN[size]
        except BaseException as e:
            logging.error("coverSize %s %s %s" % (sex,size,e))
            return None


if __name__=="__main__":
    print (API_Mysql().getDeWuGoods_API())