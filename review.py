# -*- coding: utf-8 -*-
from flask import Flask
from bs4 import BeautifulSoup
import urllib2
import StringIO
import gzip
import cookielib
from flask import render_template
import cluster
import json

app = Flask(__name__)
BASE_URL = 'http://www.dianping.com/shop/%s/review_all'
BIZER_HOST = "192.168.220.235"
BIZER_ABSTRACT_URL = "http://%s:4153/search/shopreview?query=term(shopid,%s)&sort=desc(abstract)&stat=count(reviewtagsentiment)&limit=0,0"
BIZER_REVIEW_URL = "http://%s:4153/search/shopreview?query=term(shopid,%s)&sort=desc(addtime)&fl=*&limit=%s,%s"
BIZER_TAGRANK_URL = "http://%s:4153/search/shopreview?query=term(shopid,%s),term(reviewtagsentiment,%s)&sort=desc(addtime)&fl=*&limit=%s,%s"

PAGE_SIZE = 20

@app.route("/")
def default():
    return view_by_shop('1945402')

@app.route('/<shopid>')
def view_by_shop(shopid):
    return view_by_shop_page(shopid, 1)

@app.route('/<shopid>/<pageno>')
def view_by_shop_page(shopid, pageno):
    abstract = request_abstract(shopid)
    page_dict = review_list_page(shopid, pageno)
    return render_template('review.html', val=page_dict, abstract=abstract, 
        shopname=page_dict['shopname'])


def request_abstract(shopid):
    url = BIZER_ABSTRACT_URL % (BIZER_HOST, shopid)
    i_headers = dict()
    request = urllib2.Request(url, headers=i_headers)
    response = urllib2.urlopen(request)
    decodejson = json.loads(response.read())
    return decodejson

def request_review(shopid, start, pagesize):
    url = BIZER_REVIEW_URL % (BIZER_HOST, shopid, start, pagesize)
    i_headers = dict()
    request = urllib2.Request(url, headers=i_headers)
    response = urllib2.urlopen(request)
    decodejson = json.loads(response.read())
    return decodejson

def request_tgrank(shopid, tag, start, pagesize):
    url = BIZER_TAGRANK_URL % (BIZER_HOST, shopid, tag, start, pagesize)
    i_headers = dict()
    request = urllib2.Request(url, headers=i_headers)
    response = urllib2.urlopen(request)
    decodejson = json.loads(response.read())
    return decodejson


def review_list_page(shopid, pageno):
    start = (int(pageno) - 1) * PAGE_SIZE
    review_json = request_review(shopid, start, PAGE_SIZE)
    r_dict = dict()
    r_dict['review'] = list()
    r_dict['shopid'] = shopid
    r_dict['curr_page'] = pageno
    if len(review_json['records']) == 0:
        return r_dict
    for r in review_json['records']:    
        r_dict['shopname'] = r['shopname']
        time = r['addtime']
        review_id = r['reviewid']
        match_list = r['reviewmatch'].split()
        tag_list = r['reviewtagsentiment'].split()
        review_body = r['reviewbody']
        review_body = highlight(review_body, match_list)
        r_dict['review'].append((review_id, time, review_body, tag_list))
    total_hit = int(review_json['totalhits'])
    r_dict['pno_list'] = range(1, total_hit / PAGE_SIZE + 1)
    return r_dict

def review_search_page(shopid, tag, pageno):
    pass

def highlight(review_content, match_list):
    for m in match_list:
        review_content = review_content.replace(m, '<font color="red">%s</font>' % (m))
    return review_content

if __name__ == "__main__":
    app.run(debug=True)
    #http://10.1.107.103/