import json

import requests
from pip._vendor.retrying import retry

from ponits import city_point
from settings import HEADERS


class ELeMe(object):
    res_id_list = []
    res_list = []

    def __init__(self):
        self.headers = HEADERS
        self.start_url = "https://h5.ele.me/restapi/shopping/v3/restaurants?latitude={2}&longitude={1}&keyword=&offset={0}"
        self.city_name = "武汉"


    @retry(stop_max_attempt_number=4)
    def parse(self,url):
        r = requests.get(url, headers=self.headers, timeout=5)
        assert r.status_code == 200
        return json.loads(r.content)

    # 获取动态加载页面的商铺id列表信息
    def get_resinfo(self,content):

            res_id = content["restaurant"]["id"]
            # 提取有用信息并添加进字典
            res = {}
            # 判断是否是重复信息
            if res_id not in self.res_id_list:
                res["res_id"] = res_id
                res["res_name"] = content["restaurant"]["name"]
                res["res_addr"] = content["restaurant"]["address"]
                if not res["res_addr"].startswith("湖北省武汉") and not res["res_addr"].startswith("武汉"):
                    return
                res["res_phono"] = content["restaurant"]["phone"] if "phone" in content[
                    "restaurant"].keys() else None
                res["res_sales"] = content["restaurant"]["recent_order_num"]

                res_url = "https://h5.ele.me/restapi/shopping/v2/menu?restaurant_id=" + str(res["res_id"])
                res["foods"] = self.get_foodsinfo(res_url)
                print(res)
                self.res_id_list.append(res_id)
                self.res_list.append(res)
            return res

    # 获取每个商铺所卖的食品信息
    def get_foodsinfo(self, url):
        food_list = []
        content_list = self.parse(url)
        for content in content_list:
            for food in content["foods"]:
                food_dict = {}
                food_dict["name"] = food["name"]
                food_dict["tips"] = food["tips"]
                food_list.append(food_dict)

        return food_list
    # 写进文件中
    def write_into(self,dict):

        with open("./eleme.txt","a",encoding="GB18030",errors="ignore") as f:
            json.dump(dict, f, ensure_ascii=False, indent=2)
            f.write("\n")



    def run(self):


        # 获取武汉地区内所有商铺id列表
        for i, j, k in city_point(self.city_name):
            num = 0
            # 起始url
            url = self.start_url.format(num, i, j)

            content_dict = self.parse(url)
            while content_dict["items"]:
                for content in content_dict["items"]:
                    print(content["restaurant"]["address"])
                    res =self.get_resinfo(content)
                    if res:
                        print(res)
                    # print(content_dict)
                        self.write_into(res)
                num += 8
                url = self.start_url.format(num, i, j)
                print(url)
                content_dict = self.parse(url)





if __name__ == '__main__':
    eleme = ELeMe()
    eleme.run()
