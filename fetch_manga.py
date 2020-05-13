# Python libraries
import time
import os
import re
import numpy as np
import logging

# Thrid party libraries
import cv2
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

class ImgFetcher(object):
    def __init__(self, src, dst, **kwargs):
        self.src = src
        self.dst = dst
        if ('prefix' in kwargs):
            self.prefix = kwargs['prefix']

        if ('rect' in kwargs):
            self.rect = kwargs['rect']
        else:
            self.rect = None
        
        if ('xpath' in kwargs):
            self.xpath = xpath
        else:
            self.xpath = "//div[@class='readForm']//img"
        
        if ('key_word' in kwargs):
            self.key_word = kwargs['key_word']
        else:
            self.key_word =  'manhua_detail'

        fig = plt.figure()
        self.axs = fig.gca()
        self.axs.set_axis_off()
        self.axs.figure.subplots_adjust(top=1,bottom=0,left=0,right=1,hspace=0,wspace=0) 
        self.pdfMaker = PdfPages(dst)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        self.min_pixels = 2e5
        
    def set_param(self, **kwargs):
        """
        Set parameters of the model
        """
        for arg, value in kwargs.items():
            command = "self.{}".format(arg)
            exec(command + "={}".format(value))
    
    def fetch(self):
        i = 0
        j = 0

        try:
            webpage = requests.get(self.src.format(i))
    #        self.remove_mark(img)
            
            while webpage.text != '404':
                soup = BeautifulSoup(webpage.content, 'html.parser')
                for link in soup.find_all('script'):
                    if not (link.string is None):
                        index1 = re.search('mhurl', link.string)
                        if not (index1 is None):
                            index2 = re.search('.jpg|.png', link.string)
                            if not (index2 is None):
                                url = link.string[index1.end()+2: index2.end()]
                                # self.logger.info(url)
                                print(url)
                                break
                            else:
                                self.pdfMaker.close()
                                return

                url = link.string[index1.end()+2: index2.end()]
                r = requests.get(prefix + url)
                img_code = np.asarray(bytearray(r.content), dtype='uint8')
                img = cv2.imdecode(img_code, cv2.IMREAD_GRAYSCALE)
                self.append_page(img)

                i += 1
                # self.logger.info("------- Page{} -------".format(i))
                print("------- Page{} -------".format(i))
                webpage = requests.get(self.src.format(i))

                # if i == 3:
                #     break
        except:
            return False
        else:
            self.pdfMaker.close()
            return True
    
    def scroll_fetch(self, j=None):
        js="document.getElementById('mainView').scrollTop={}"
        # driver = webdriver.Chrome()
        driver = webdriver.PhantomJS()
        try:
            driver.get(self.src)
            imgs = driver.find_elements_by_xpath("//div[@id='mainView']/ul[@id='comicContain']//img")
            if len(imgs) == 0:
                return False
            
            j = 0 if j is None else j
            for i in range(j):
                driver.execute_script(js.format((i)*1080))
                time.sleep(2)

            for i in range(j, len(imgs)):
                print("------- Page{} -------".format(i))
                url = imgs[i].get_attribute("src")
                if not 'manhua_detail' in url:
                    continue
                
                r = requests.get(imgs[i].get_attribute("src"))
                img_code = np.asarray(bytearray(r.content), dtype='uint8')
                img = cv2.imdecode(img_code, cv2.IMREAD_GRAYSCALE)
                # cv2.imwrite("d://{}.jpg".format(i), img)
                if img.shape[0] * img.shape[1] > self.min_pixels:
                    self.remove_mark(img)
                    self.append_page(img)
                driver.execute_script(js.format((i+1)*1080))
                time.sleep(2)
     
                # if i == 2:
                #     break
            
        except Exception as e:
            print(e)
            return i
        else:
            self.pdfMaker.close()
            return "s"
    
    def page_by_page_fetch(self, j=None):
        # driver = webdriver.Chrome()
        driver = webdriver.PhantomJS()
        try:
            j = 1 if j is None else j
            driver.get(self.src.format(j))
            time.sleep(2)
            imgs = driver.find_elements_by_xpath(self.xpath)
            
            break_flag = False
            if type(imgs) == list:
                print(len(imgs))
    
                while (len(imgs)):
                    print("------- Page{} -------".format(j))           
                    r = requests.get(imgs[-1].get_attribute("src"))
                    img_code = np.asarray(bytearray(r.content), dtype='uint8')
                    img = cv2.imdecode(img_code, cv2.IMREAD_GRAYSCALE)
    
                    if not (img is None):
                        if img.shape[0] * img.shape[1] <= self.min_pixels:
                            break
                        
#                        cv2.imwrite("d://{}.jpg".format(j), img)
                        self.append_page(img)
                    
                    else:
                        self.logger.warning("Empty page!")
                        return j
    
                    j += 1
    
                    driver.get(self.src.format(j))
                    time.sleep(2) 
                    imgs = driver.find_elements_by_xpath(self.xpath)
                    
                    # if j == 5:
                    # #    break

            else:
                while (True):
                    print("------- Page{} -------".format(j))           
                    r = requests.get(imgs.get_attribute("src"))
                    img_code = np.asarray(bytearray(r.content), dtype='uint8')
                    img = cv2.imdecode(img_code, cv2.IMREAD_GRAYSCALE)
        
                    if not (img is None):
                        if img.shape[0] * img.shape[1] <= self.min_pixels:
                            break
                        
                        # cv2.imwrite("d://{}.jpg".format(j), img)
                        self.append_page(img)
                    
                    else:
                        self.logger.warning("Empty page!")
        
                    j += 1
                    
                    if (j>=3):
                        break
                    
                    driver.get(self.src.format(j))
                    time.sleep(1) 
                    imgs = driver.find_elements_by_xpath(self.xpath)                

        except Exception as e:
            webpage = requests.get(self.src.format(j))
            soup = BeautifulSoup(webpage.content, 'html.parser')
            for link in soup.find_all("img"):
                if "404" in str(link):
                    self.pdfMaker.close()
                    return 's'
                
            print(e)
            return j
        else:
            self.pdfMaker.close()
            return 's'
        
    
    def append_page(self, img):
        if img.shape[1] > 1020:
            self.axs.figure.set_size_inches(1373/100, 1036/100)
        else:
            self.axs.figure.set_size_inches(900/100, 1360/100)
        self.axs.imshow(img, cmap='gray')
        self.pdfMaker.savefig(self.axs.figure)
        
    def remove_mark(self, img):
        if self.rect is None:
            self.logger.error('No rectangle region')
        h = img.shape[0]
        w = img.shape[1]
        ROI = np.where(img[int(self.rect[0]*h):int(self.rect[2]*h), int(self.rect[1]*w):int(self.rect[3]*w)]<127, 10, 253)
        img[int(self.rect[0]*h):int(self.rect[2]*h), int(self.rect[1]*w):int(self.rect[3]*w)] = ROI


if __name__ == '__main__':
    src = "http://www.mangabz.com/m{}" 
    dst = r'D:\Manga\Ghost\gb_{}.pdf'
    rect = [0.948, 0.81, 0.98, 0.977]                       # startx, starty, endx, endy
    xpath = '//div[@class="readForm"]//img'
#    Fetcher = ImgFetcher(src, dst, rect=rect)
#    Fetcher.scroll_fetch()
#     Fetcher.fetch()
    
    indices = np.loadtxt("D:\\indices.txt")
    
    j = 170
    for i in indices[:75]:
        counter = 0
        src_ = src.format(int(i)) + "-p{}"
        print(src_)
        dst_ = dst.format(j)
        Fetcher = ImgFetcher(src_, dst_, xpath=xpath)
        k = Fetcher.page_by_page_fetch()
        if k != "s":
            for m in range(10):
                print("============ Try again ===============")
                time.sleep(10)
                k = Fetcher.page_by_page_fetch(k)
                if (k == "s"):
                    break
                counter += 1
                if counter > 7:
                    break
        if counter <= 7:
            j -= 1
        
        del Fetcher

    