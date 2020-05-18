import re
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


home_page = r""
driver =  webdriver.PhantomJS()
tagname_a_array = driver.find_element_by_tag_name('a')

page_indices = []
pattern = re.compile("http://www.mangabz.com/m\d")

for line in tagname_a_array:
    href_text = line.get_attribute("href")
    print(href_text)
    page_index_range = pattern.search(href_text)
    if page_index_range is not None:
        page_indices.append(int(href_text[page_index_range.start()+24:-1]))

np.savetxt("D:\\indices.txt", np.asarray(page_indices))