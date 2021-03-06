#!/usr/bin/python3

import requests
import json
import hashlib
import logging
import os

# 子项配置优先于全局配置
conf = json.loads('''{
    "items": [
        {
            "urls": {
                "测试": "http://httpbin.org/get"

            },
            "webhook": "webhook",
            "content": {
                "msgtype": "text",
                "text": {
                    "content": "%s 更新啦\\n%s"
                }
            }
        }

    ],
    "webhook": "全局地址",
    "headers": {
        "User-Agent": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"
    }
}
''')

# 文字消息字段飞书是msg_type，钉钉/企业微信是msgtype, 其他类型的消息格式详见文档
# 飞书 https://www.feishu.cn/hc/zh-CN/articles/360024984973
# 钉钉 https://developers.dingtalk.com/document/app/custom-robot-access
# 企业微信 https://work.weixin.qq.com/api/doc/90000/90136/91770

# 缓存文件路径
cacheFile = ".url-alert"



logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %I:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)

if os.path.exists(cacheFile):
    with open(cacheFile) as f:
        cache = json.load(f)
else:
    cache = {}


def main(item):
    for name, value in item["urls"].items():
        time.sleep(0.5)
        try:
            if t:=item.get("headers"):
                headers = t
            else:
                headers = conf.get("headers")

            if t:=item.get("urlf"):
                url = t % value
            else:
                url = value

            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                logger.error(f"error fetch {url}\nstatus_code: {r.status_code}\n{r.text}")
            else:
                key = hashlib.md5(url.encode()).hexdigest()
                md5 = hashlib.md5(r.content).hexdigest()

                if cache.get(key) and cache[key] != md5:
                    message(item, name, value)

                cache[key] = md5

        except Exception as e:
            logger.error(f"error fetch {url}\n{e}")

def message(item, *data):
    if t:=item.get("webhook"):
        webhook = t
    else:
        webhook = conf.get("webhook")

    if t:=item.get("content"):
        content = t
    else:
        content = conf.get("content")

    if data:
        content = json.loads(json.dumps(content) % data)

    r = requests.post(webhook, json=content)
    if (r.json().get("code") and r.json().get("code") != 0) or (r.json().get("errcode") and r.json().get("errcode") != 0):
        logger.error(f"发送消息错误:\n{r.text}")


if __name__ == '__main__':
    for i in conf["items"]:
        main(i)
    with open(cacheFile, "w") as f:
        json.dump(cache, f)

