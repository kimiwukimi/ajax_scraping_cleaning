# -*- coding: utf-8 -*-

import requests
import json
import re
import sys
import random
import os
import math

from os.path import dirname, abspath
from random import randint
from time import sleep, strftime, localtime, time
from bs4 import BeautifulSoup

############

SLEEP_TIME_RANDOM_START = 1
SLEEP_TIME_RANDOM_END = 2

############

def LoadUserAgents(uafile):
    """
    uafile : string
        path to text file of user agents, one per line
    """
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1])
                #print ua.strip()[1:-1]
    random.shuffle(uas)
    #print len(uas)
    return uas

def download_review_of_one_id(reviewer_id, review_id, review_date):
    last_page_for_this_id = None


    while True:
        
        uas = LoadUserAgents("user_agents.txt")
        ua = random.choice(uas)  # select a random user agent
        headers = {
            "Connection" : "close",  # another way to cover tracks
            "User-Agent" : ua}

        print 'Downloading {} {} {} {}'.format(reviewer_id, review_id, review_date, strftime("%Y%m%d_%H%M%S", localtime()))
        try:
            url = 'https://www.aaa.com/gp/review/' + review_id
            r = requests.get(url, headers=headers, allow_redirects=False)
            html = r.content
        except ConnectionError:
            print 'ConnectionError. Sleep a 10-20 sec.'
            sleep(randint(10,20))
            continue
            
        #
        #   Error handling below.
        #
        if r.status_code == 404:
            print '404 =', reviewer_id, review_id
            sleep(randint(2,3))
            #   write downloaded page to downloaded_page.txt
            with open('404_page.txt', 'a+') as downloaded_fp:
                downloaded_fp.write('{}\n'.format(review_id))           
            break
        
        if r.status_code != 200:
            random_time = randint(10,20)
            print 'Status code:', r.status_code, '. Sleep {} seconds.'.format(random_time)
            sleep(random_time)
            continue
        
        if "Sorry, we just need to make sure you're not a robot." in html:
            random_time = randint(10,20)
            print 'Encounter robot test. Sleep {} seconds to retry.'.format(random_time)
            sleep(random_time)
            continue
        #
        #   End of Error handling
        #
        with open('review.json', 'a+', 0) as fp:
            json.dump([reviewer_id, review_id, review_date, int(time()), html.decode("utf-8", "ignore")], fp)
            fp.write('\n')

        #   write downloaded page to downloaded_page.txt
        with open('downloaded_page.txt', 'a+') as downloaded_fp:
            downloaded_fp.write('{}\n'.format(review_id))
            
        #
        #   sleep a random time to slow down
        #
        random_time = randint(SLEEP_TIME_RANDOM_START, SLEEP_TIME_RANDOM_END)
        print 'Downloaded: {} {} . Sleep {} seconds.'.format(reviewer_id, review_id, random_time)
        sleep(random_time)
        break   # break while true loop

    #print reviewer_id, review_id, 'downloaded.'


cwd = dirname(abspath(__file__))
project_dir = os.path.dirname(cwd)
reviews_id = os.path.join(project_dir, 'download_reviews_pages', 'reviews_id.txt')

with open('downloaded_page.txt','a+') as downloaded_fp:
    downloaded_page = downloaded_fp.read().splitlines() 
    
with open('404_page.txt','a+') as page404_fp:
    page_404 = page404_fp.read().splitlines() 
    
#
#  [reviewer_id, review_id, review_date ]
#
with open(reviews_id) as fp:        
    for line in fp:
        data = json.loads(line.strip(), encoding = 'utf-8')
        reviewer_id = data[0]
        review_id = data[1]
        review_date = data[2]

        if (review_id not in downloaded_page) and (review_id not in page_404):
            
            try:
                download_review_of_one_id(reviewer_id, review_id, review_date)
            except:
                print reviewer_id, review_id, "Unexpected error:", sys.exc_info()[0]
                # winsound.Beep(800,500)   #winsound.Beep(Freq,Dur)
            
        #else:
            #print 'Skipping {} {} because it is downloaded.'.format(reviewer_id, review_id)
            #pass
        