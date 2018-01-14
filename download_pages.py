#-*- encode = utf-8 -*-

import json
import sys
import time
import re
import random
import os
import math

from selenium import webdriver
from time import sleep, localtime, strftime, mktime, strptime
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from os.path import dirname, abspath
from random import randint
from time import sleep, strftime, localtime, time
from bs4 import BeautifulSoup

TRY_TIMES = 2
WAIT_MULTIPLIER = 10

def to_epoch(time_string):
    pattern = "%b %d, %Y"
    epoch = int(mktime(strptime(time_string, pattern)))
    return epoch

def have_content(page):
    try:
        soup = BeautifulSoup(page, "lxml")
        div = soup.find_all('div',  {'cel_widget_id' : "GlimpseTimeline"})[0]
        div = div.find_all('div')
        for item in div:
            if 'data-story-id' in str(item):
                pattern = re.compile('\w+\s\d{1,2},\s\d{4}')
                dates = re.findall(pattern, str(item))          
                if dates:
                    return True
    except:
        pass
    
def reach_20160801_or_before(page):
    
    soup = BeautifulSoup(page, "lxml")
    div = soup.find_all('div',  {'cel_widget_id' : "GlimpseTimeline"})[0]
    div = div.find_all('div')
    date_list = []
    
    for item in div:
        if 'data-story-id' in str(item):
            #pattern = re.compile('https://www.xxx.com/gp/review/(.+?)\?')
            #review_ids = re.findall(pattern, str(item))
                
            pattern = re.compile('\w+\s\d{1,2},\s\d{4}')
            dates = re.findall(pattern, str(item))
            
            if len(dates) == 0:
                dates = [strftime("%b %d, %Y", localtime())]
            #print dates
            for i in range(len(dates)):
                try:
                    dates[i] = to_epoch(dates[i])   # convert to epoch time
                    date_list.append(dates[i])
                except:
                    pass
                #print dates[i]
            
            if max(dates) < to_epoch('Aug 1, 2016'):
                print 'earliest post: {}'.format(strftime("%b %d, %Y", localtime(min(date_list))))
                return True
    print 'earliest post: {}'.format(strftime("%b %d, %Y", localtime(min(date_list))))

def no_reviews(page):
    
    soup = BeautifulSoup(page, "lxml")
    div = soup.find_all('div', "activity-section")
    
    if len(div) == 0:
        print 'completely no content'
        return True
        
    #print 'div0 text=', div[0].text
    
    if 'This customer has chosen to hide reviews from their profile' in div[0].text:
        print 'choose to hide reviews.'
        with open('empty_review.txt', 'a+', 0) as empty_fp:
            empty_fp.write('{}\n'.format(id))
        return True

                    
def download_one_reviewers(id):
    
    #id = 'A1H4BDHFRBPRV9'   ### for testing
    
    print 'Downloading {} Start time:{}'.format(id, strftime("%Y%m%d_%H%M", localtime()))
    #sleep(5)
    url = 'https://www.xxx.com/gp/profile/' + id

    driver.get(url)
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
    last_div_numbers = 0
    tries_after_no_additional_div = 0

    for i in range(100):
        for j in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(1)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        sleep(2)
        
        page = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(page, "lxml")
        div = soup.find_all('div')
        current_div_len = len(div)
        
        if no_reviews(page):
            with open('empty_review.txt', 'a+', 0) as empty_fp:
                empty_fp.write('{}\n'.format(id))
            break
        #
        #   if there are content, wait a few seconds to let javascript load.
        #
        if have_content(page):
            #print 'there are content. sleep 5 seconds.'
            sleep(randint(1,3))

        #
        #   reach 20160801
        #
        try:
            if reach_20160801_or_before(page):
                print 'Reached date before 2016.08.01'
                #
                #   10/31 10:46 add this snippet
                #
                with open('data.json', 'a+', 0)as fp:
                    json.dump([id, strftime("%Y%m%d_%H%M", localtime()), driver.page_source.encode('utf-8')], fp)
                    fp.write('\n')
                
                with open('downloaded_page.txt', 'a+', 0) as downloaded_fp:
                    downloaded_fp.write('{}\n'.format(id))
                #
                #
                #
            
                print "downloaded successfully.***"
                sleep(10)
                
                return
        except:
            pass
        
        if last_div_numbers == current_div_len:   
            #print 'No more content for this reviewer.'
            tries_after_no_additional_div += 1
            sleep(WAIT_MULTIPLIER*tries_after_no_additional_div)
            #print 'tried times:', tries_after_no_additional_div
        else:
            tries_after_no_additional_div = 0
        
        # set error margin
        if tries_after_no_additional_div >= TRY_TIMES:
            print 'div not changed too many times. Break. Write to start_after_0801_data'
            with open('start_after_0801_data.json', 'a+', 0)as fp:
                json.dump([id, strftime("%Y%m%d_%H%M", localtime()), driver.page_source.encode('utf-8')], fp)
                fp.write('\n')          
            break
        
        if current_div_len > 40000:
            print 'div > 20000. Break'
            break
        
        last_div_numbers = len(div)
        #print 'len of divs=', last_div_numbers
        sleep(2)

    print id, 'did not downloaded because no content or tried to many times. Writing no_content.txt...'
    
    with open('no_content.txt', 'a+', 0) as no_content_wfp:
        no_content_wfp.write('{}\n'.format(id))
    sleep(10)
    
    
##########

cwd = dirname(abspath(__file__))
project_dir = os.path.dirname(cwd)
id_list = os.path.join(project_dir, 'fetch_id', 'id_list.txt')
ids = list()
with open(id_list) as fp:
    ids = fp.read().splitlines() 

with open('downloaded_page.txt','a+') as downloaded_fp:
    downloaded_page = downloaded_fp.read().splitlines() 

with open('no_content.txt','a+') as no_content_fp:
    no_content_page = no_content_fp.read().splitlines()

with open('empty_review.txt', 'a+') as efp:
    empty_page = efp.read().splitlines()
    
##########
    
#driver = webdriver.PhantomJS()
driver = webdriver.Chrome()
driver.set_window_position(0, 0)
driver.set_window_size(500, 650)

rank = 0
for id in ids:
    rank += 1
    if id not in downloaded_page:       

        try:
            print 'Rank:', rank, '========================'
            download_one_reviewers(id)
        except:
            print id, "Unexpected error:", sys.exc_info()[0]
            print 'sleep 60 sec'
            sleep(60)
    else:
        print 'Skipping rank:', rank, 'because already downloaded.'
            
driver.quit()