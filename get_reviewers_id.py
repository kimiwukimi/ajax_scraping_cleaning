# -*- coding: utf-8 -*-
import requests
import re
from random import randint
from time import sleep, strftime, localtime

def get_id(url):
    r = s.get(url)
    #r = s.get('https://www.xxx.com/review/top-reviewers/ref=cm_cr_tr_link_2?ie=UTF8&page=1')
    #r = s.get('https://www.xxx.com/gp/cdp/member-reviews/ALYZJ7W14YS26/ref=cm_cr_tr_tbl_1_sar?ie=UTF8&sort_by=MostRecentReview')
    html = r.text.encode('utf-8')
    pattern = re.compile(r'href="/gp/pdp/profile/(.+?)/')
    all_id = re.findall(pattern, html)
    for id in list(set(all_id)):
        fp.write( id + '\n')
        id_list.append(id)
    random_time = randint(1,3)
    print 'Add', len(list(set(all_id))), 'id. Sleep', random_time, 'seconds.'
    sleep(random_time)

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"})
id_list = list()
current_time = strftime("%Y%m%d_%H%M", localtime())

with open('id_list_' + current_time + '.txt','a+', 0)as fp:
    for page in range(1,101):
        print 'page=', page
        url = 'https://www.xxx.com/review/top-reviewers/ref=cm_cr_tr_link_2?ie=UTF8&page=' + str(page)
        get_id(url)
        