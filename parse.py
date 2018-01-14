import requests
import json
import re
import os

from bs4 import BeautifulSoup
from random import randint
from time import sleep, strftime, localtime
from os.path import dirname, abspath

############################

TEST_TIMES = 50000
FILE_NAME_TO_BE_PARSED = 'review-1112.json'

############################

def parse_html(line):
    result_dict = dict()
    review = json.loads(line.strip(), encoding = 'utf-8')
    
    reviewer_id = review[0]
    review_id = review[1]
    review_date = review[2]
    review_download_time = review[3]
    html = review[4]   
    soup = BeautifulSoup(html, "html5lib")
    
    
    review_text = soup.find('div',{'class':'reviewText'}).text
    result_dict['review_text'] = review_text
    
    reviewer_section = soup.find_all('div',{'class':'crAuthorInfo'})[0]
    
    a_of_reviewer_section = reviewer_section.find('a', href=re.compile('https://www.aaa.com/review/top-reviewers'))
    reviewer_rank = a_of_reviewer_section.text
    result_dict['reviewer_rank'] = reviewer_rank
    #print 'reviewer_rank:', reviewer_rank
    
    div_in_reviewer_section = reviewer_section.find_all('div')
    reviewer_location = div_in_reviewer_section[1].text
    #print 'location =', location
    result_dict['reviewer_location'] = reviewer_location
    
    
    badges = reviewer_section.find('div').find_all('a')
    badge_list = list()
    #pattern = re.compile('alt\="(.+?)"')
    #product_star_rating = re.findall(pattern, str(span_star[0]))
    for i in range(1, len(badges)):
        a_badge = badges[i].img['alt'].strip('()')
        badge_list.append(a_badge)
    #print 'badge_list:', badge_list
    result_dict['badge_list'] = badge_list
    
    #print 'reviewer_id:', reviewer_id
    result_dict['reviewer_id'] = reviewer_id
    print 'review_id:', review_id
    result_dict['review_id'] = review_id
    #print 'review_date:', review_date
    result_dict['review_date'] = review_date
    #print 'review_download_time:', review_download_time
    result_dict['review_download_time'] = review_download_time
    
    left_col = soup.body.table.tbody.tr.td.div
    left_col_text = left_col.text
    
    #
    # item details
    #

    try:
        item_details = soup.find_all('div',{'class':'crDescription'})[0]
        a = item_details.find_all('a', text = re.compile('used & new'))
        if len(a) == 1:
            num_reviews_by_reviewer = a[0].text.split()[0]
            #print 'num_reviews_by_reviewer =', num_reviews_by_reviewer
            result_dict['num_reviews_by_reviewer'] = num_reviews_by_reviewer
            #available_price = a[0].next_sibling.next_sibling.text
            #print 'available_price', available_price
        elif len(a) == 0:
            #print 'num_reviews_by_reviewer = NA'
            result_dict['num_reviews_by_reviewer'] = 'NA'
            
        else:
            print 'num_reviews_by_reviewer != 1, a=', a
            
        div_item = item_details.find_all('div')
        product_name = div_item[0].text.strip()
        #print 'product_name:', product_name
        result_dict['product_name'] = product_name

        histo_rating = dict()
        histo_row = item_details.find_all(class_=re.compile("histoRow"))
        pattern = re.compile('star([0-9]+?)%')
        for item in histo_row:
            #print item.text.strip().split()
            star_number = item.text.strip().split()[0]
            percent = item.text.strip().split()[-1]
            histo_rating[star_number] = percent
        #print 'histo_rating:', histo_rating
        result_dict['histo_rating'] = histo_rating
        
        #####################################
        ##
        ## price list
        ##
        ## if there are three price, the original(first) price's tag is listprice
        ## if there are no discount price, all price tag are 'price'
        ##
    
        item_details = soup.find_all('div',{'class':'crDescription'})[0]
        list_price_node = item_details.find('span', {'class':'listprice'})
        price = [None, None, None]
        prices = item_details.find_all('span', {'class':'price'})

        # if listprice exist
        if list_price_node != None:  # there must be a discount_price
            list_price = list_price_node.text
            #print 'list_price:', list_price
            #result_dict['list_price'] = list_price
            price[0] = list_price
            for item in prices:
                #price.append(item.text.split())
                price_tag = item.text.split()
                if len(price_tag) == 1:
                    price[1] = price_tag[0]
                elif len(price_tag) == 2:
                    price[1] = price_tag[0]
                    price[2] = price_tag[1]
                else:
                    print 'price tag has more than 2 prices'


        else:   # at most 2 price

            for item in prices:
                price_tag = item.text.split()
                if len(price_tag) == 1:
                    price[1] = price_tag[0]
                elif len(price_tag) == 2:
                    price[1] = price_tag[0]
                    price[2] = price_tag[1]
                else:
                    print 'price tag has more than 2 prices'

        result_dict['price'] = price
        #print 'price:', price

        ##########################
        
        span_star = soup.find_all('span',{'class':'crAvgStars'})
        if len(span_star) == 1:
            pattern = re.compile('alt\="(.+?) out of 5 stars"')
            product_star_rating = re.findall(pattern, str(span_star[0]))
            #print 'product_star_rating=', product_star_rating
            result_dict['product_star_rating'] = product_star_rating

            item_reviewed_times = span_star[0].text.strip().strip('()').split()[0]
            #print 'item_reviewed_times:', item_reviewed_times
            result_dict['item_reviewed_times'] = item_reviewed_times
        else:
            print '***star rating number != 1 might have error'
    except:
        print '***Item no longer available on Amazon'
    
    
    #
    # perminent_link, asin
    #
    
    Permalink = soup.find_all('span', {'class':'tiny'}, text = 'Permalink')
    if len(Permalink) == 1:
        perminent_link = Permalink[0].a['href']
        #print 'perminent_link:', perminent_link
        result_dict['perminent_link'] = perminent_link
    else:
        print 'perminent link more than one element ERROR'
    
    pattern = re.compile('ASIN\=(.+?)$')
    asin = re.findall(pattern, perminent_link)
    #print 'asin:', asin
    result_dict['asin'] = asin

    #
    # vine_review
    #
    
    if 'Vine Customer Review' in left_col_text:
        vine_review = True
        #print 'vine_review:', vine_review
        result_dict['vine_review'] = vine_review
    else:
        print '***not a vine_review'
        
    #
    # verified_purchase
    #
    if 'Verified Purchase' in left_col_text:
        verified_purchase = True
        #print 'verified_purchase:', verified_purchase
        result_dict['verified_purchase'] = verified_purchase
    else:
        print '***not a verified_purchase'
    
    #
    # stars, review_title, review_is_from, helpful
    #
    
    pattern = re.compile('alt\="(.+?) out of 5 stars"')
    stars = re.findall(pattern, str(left_col))
    #print 'stars:', stars
    result_dict['stars'] = stars
    
    left_col = soup.body.table.tbody.tr.td.div
    
    helpful_or_title = left_col.find_all('div')
    for i in range(1):
        #print 'review_title:', helpful_or_title[i].text.strip()
        review_title = helpful_or_title[0].text.strip()

        if 'people found the following review helpful' in helpful_or_title[i].text.strip():
            helpful_count = helpful_or_title[i].text.strip().split()
            helpful_votes = helpful_count[0]
            total_votes = helpful_count[2]
            review_title = helpful_or_title[i+1].b.text.strip()
            #print 'review_title:', review_title
            result_dict['review_title'] = review_title
            
            #print 'helpful_count:', helpful_count
            #print 'helpful_votes:', helpful_votes
            result_dict['helpful_votes'] = helpful_votes
            #print 'total_votes:', total_votes
            result_dict['total_votes'] = total_votes
        else:
            #print 'review_title:', review_title
            result_dict['review_title'] = review_title
            print '***helpful_votes: Cannot be parsed yet. Prabably no votes yet.'
            print '***total_votes: Cannot be parsed yet. Prabably no votes yet.'
                
    tiny_class = left_col.find_all('div', {'class':'tiny'})
    try:
        if len(tiny_class) == 1:
            review_is_from = tiny_class[0].text.strip()
            #print 'review_is_from:', review_is_from
            result_dict['review_is_from'] = review_is_from
        else:
            #print 'review is from more than one "tiny" div'
            review_is_from = tiny_class[1].text.strip()
            #print 'review_is_from:', review_is_from
            result_dict['review_is_from'] = review_is_from
    except:
        print '***review_is_from might not exist Error'
    
    
    #print result_dict
    
    #print 'dic len =', len(result_dict)
    with open('result.json','a+') as wfp:
        json.dump(result_dict, wfp)
        wfp.write('\n')
    
    
cwd = dirname(abspath('__file__'))
project_dir = os.path.dirname(cwd)
#reviews_file = os.path.join(project_dir, 'reviews_download', FILE_NAME_TO_BE_PARSED)
reviews_file = os.path.join(project_dir, 'reviews_download', 'backup', FILE_NAME_TO_BE_PARSED)
#print reviews_file

with open('parsed.txt','a+') as fp:
    parsed_list = fp.read().splitlines()

with open(reviews_file) as fp, open('parsed.txt', 'a+', 1) as parsed_fp, \
    open('failed_parsing.txt', 'a+', 1) as failed_parsing_fp:
    test_lines = 0
    for line in fp:
        review = json.loads(line.strip(), encoding = 'utf-8')
        review_id = review[1]
        if review_id not in parsed_list:
        
            #print '================================='
            try:
                parse_html(line)
                parsed_fp.write(review_id + '\n')  # write succeed file to parsed.txt
            except:
                failed_parsing_fp.write(line)
                
        else:
            print 'skipping', review_id
       
        test_lines += 1
        if test_lines >= TEST_TIMES:
            break
        