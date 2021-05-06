#coding=utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import csv
import time
import requests

## set browser
options = Options()
options.add_argument("--disable-notifications")
chrome = webdriver.Chrome('../chromedriver', chrome_options=options)