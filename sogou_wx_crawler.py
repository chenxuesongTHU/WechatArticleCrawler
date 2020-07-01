#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@File        :   StatSentiment
@Time        :   2020/7/1 12:03 上午
@Author      :   Xuesong Chen
@Description :
"""

import argparse
import os
import random

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import time
from PIL import ImageGrab
import keyboard
import requests
import base64


class VerificationCode:

    def get_code(self, img_path):
        with open(img_path, 'rb') as f:
            img = f.read()

        # ret = requests.post('http://192.168.1.105:8820',
        #                     data={"img": base64.b64encode(img)})
                            
        ret = requests.post('http://172.20.10.3:8820',
                            data={"img": base64.b64encode(img)})
        return ret.text[5:11]


# chromedriver = 'chromedriver.exe' # win
chromedriver = '/Users/cxs/libraries/selenium/chromedriver' # mac

os.environ["webdriver.chrome.driver"] = chromedriver

def parse_args():
    """添加命令行参数信息"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default='', type=str, help="query keyword")
    parser.add_argument("--start_page", default=0, type=int, help="start page")
    return parser.parse_args()


# 声明一个列表存储字典
data_list = []
args = parse_args()
KeyWord = args.query

vrf_code = VerificationCode()


# beautifulSoup
def handle_article(html, data_dict):
    soup = BeautifulSoup(html, "html.parser")
    publish_time = soup.find('em', id='publish_time').text
    contents = soup.find('div', class_='rich_media_content').contents
    article = ''
    for paragraph in contents:
        try:
            article += paragraph.text + '<br>'
        except:
            continue
    article = article.replace('\n', '<br>')

    # 标题 发布公众号 摘要 链接 时间 内容
    with open("output/all/%s.tsv"%KeyWord, 'a+', encoding='utf-8') as file:
        print(
            data_dict['title'], data_dict['author'], data_dict['abstract'], data_dict['href'],
            publish_time, article, sep='\x01', file=file,
        )


def randomSleep(type='short'):
    # return
    if type == 'short':
        sleeptime = random.randint(1, 3)
    else:
        sleeptime = random.randint(10, 30)
    time.sleep(sleeptime)


def start_spiders(KeyWord, start_page=0):

    driver = webdriver.Chrome(chromedriver)
    # url网址
    url = 'https://weixin.sogou.com/'
    # 请求该网址
    driver.get(url)

    # 找到输入框id
    crawlered_pages_n = start_page
    query = driver.find_element_by_id('query')
    query.send_keys(KeyWord)
    # 找到搜索按钮
    time.sleep(1)
    swz = driver.find_element_by_class_name('swz')
    swz.click()
    # 找到登陆按钮并点击
    time.sleep(1)  # 如果要输入验证码，要给出充分的时间（15s）输入验证码
    top_login = driver.find_element_by_id('top_login')
    top_login.click()
    # 显示等待是否登陆成功
    WebDriverWait(driver, 1000).until(
        EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 'yh')
        )
    )
    print('登录成功')
    # 跳转到指定页面开始


    if start_page != 0:
        current_url = driver.current_url
        current_url += '&page=%d'%start_page
        driver.get(current_url)
    while True:
        # 找到所有的li标签
        lis = driver.find_elements_by_xpath('//ul[@class="news-list"]/li')
        # 找到下一页的按钮
        # 遍历列表
        for li in lis:
            # 题目
            title = li.find_element_by_xpath('.//h3').text
            # 作者
            author = li.find_element_by_class_name('account').text
            # 时间
            datetime = li.find_element_by_class_name('s2').text
            # 文章摘要，这个项目没要求
            abstract = li.find_element_by_class_name('txt-info').text
            # 文章链接
            href = li.find_element_by_xpath('.//h3/a').get_attribute('href')

            # 声明一个字典存储数据
            data_dict = {}
            data_dict['title'] = title
            data_dict['author'] = author
            data_dict['datetime'] = datetime
            data_dict['abstract'] = abstract
            data_dict['href'] = href


            click_element = li.find_element_by_link_text(title)
            actions = ActionChains(driver)
            actions.click(click_element).perform()


            # 切换到新标签页的window
            driver.switch_to.window(driver.window_handles[-1])
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located(
                        (By.ID, 'publish_time')
                    )
                )
                driver.find_element_by_id('publish_time').click()
                html = driver.page_source
                handle_article(html, data_dict)
            except:
                pass
            randomSleep('short')
            driver.close()
            driver.switch_to.window(driver.window_handles[0])


        try:
            sogou_next = driver.find_element_by_id('sogou_next')
            # 如果下一页按钮存在就继续
            time.sleep(3)
            sogou_next.click()
            print('crawl down %d pages...'%(crawlered_pages_n+1))
            crawlered_pages_n += 1


        except Exception as e:

            while driver.find_element_by_id('seccodeImage'):
                # 出现验证码，进行填充
                img_element = driver.find_element_by_id('seccodeImage')
                action = ActionChains(driver).move_to_element(img_element)# 移动到该元素
                action.context_click(img_element) # 右键点击该元素
                action.perform()
                for i in range(8):
                    keyboard.press_and_release('down')
                keyboard.press_and_release('enter')
                time.sleep(2)
                image = ImageGrab.grabclipboard()  # 获取剪贴板文件

                image.save('%s.png'%KeyWord)

                while True:
                    code = vrf_code.get_code('%s.png'%KeyWord)
                    # time.sleep(5)
                    if code != 'AUTO  ':
                        break

                query = driver.find_element_by_id('seccodeInput')
                query.send_keys(code)


                time.sleep(1)
                submit = driver.find_element_by_id('submit')
                submit.click()
                time.sleep(2)
                if driver.find_element_by_class_name('swz'):
                    break
                else: # 刷新验证码
                    img_element = driver.find_element_by_id('seccodeImage')
                    action = ActionChains(driver).move_to_element(img_element)  # 移动到该元素
                    action.click(img_element)  # 左键刷新验证码
                    action.perform()

            try:
                sogou_next = driver.find_element_by_id('sogou_next')
                time.sleep(3)
                sogou_next.click()
            except:
                pass
            continue


def main():
    start_spiders(KeyWord=args.query, start_page=args.start_page)


if __name__ == '__main__':

    main()

