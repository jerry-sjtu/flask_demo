# -*- coding: utf-8 -*-
from flask import Flask
import urllib2
from flask import render_template
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
BASE_URL = 'http://www.dianping.com/shop/%s/review_all'
BIZER_HOST = "192.168.220.235"
BIZER_ABSTRACT_URL = "http://%s:4153/search/shopreview?query=term(shopid,%s)&sort=desc(abstract)&stat=count(reviewtagsentiment)&limit=0,0"
BIZER_REVIEW_URL = "http://%s:4153/search/shopreview?query=term(shopid,%s)&sort=desc(addtime)&fl=*&limit=%s,%s"
BIZER_TAGRANK_URL = "http://%s:4153/search/shopreview?query=term(shopid,%s),term(reviewtagsentiment,%s)&sort=desc(tagrank)&fl=*&limit=%s,%s"

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
        shopname=page_dict['shopname'], shopid=page_dict['shopid'], tag='')


@app.route('/<shopid>/tag/<tag>')
def view_by_shop_tag(shopid, tag):
    return view_by_shop_tag_page(shopid, tag, 1)

@app.route('/<shopid>/<pageno>/tag/<tag>')
def view_by_shop_tag_page(shopid, tag, pageno):
    abstract = request_abstract(shopid)
    page_dict = review_search_page(shopid, tag, pageno)
    return render_template('review.html', val=page_dict, abstract=abstract, 
        shopname=page_dict['shopname'], shopid=page_dict['shopid'], tag=tag)

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
    r_dict['pno_list'] = pageno_list(int(pageno), total_hit)
    return r_dict

def review_search_page(shopid, tag, pageno):
    start = (int(pageno) - 1) * PAGE_SIZE
    review_json = request_tgrank(shopid, tag, start, PAGE_SIZE)
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
        match_list = list()
        match_list.append(r['highlight'])
        tag_list = r['reviewtagsentiment'].split()
        review_body = r['reviewbody']
        review_body = highlight(review_body, match_list)
        r_dict['review'].append((review_id, time, review_body, tag_list))
    total_hit = int(review_json['totalhits'])
    #r_dict['pno_list'] = range(1, total_hit / PAGE_SIZE + 2)
    r_dict['pno_list'] = pageno_list(int(pageno), total_hit)
    return r_dict

def pageno_list(curr_page, total_hit):
    max_page = total_hit / PAGE_SIZE + 1
    no_list = list()
    no_list.append('1')
    if curr_page > 2:
        no_list.append('...')
    for i in range(curr_page, curr_page + 20):
        if i < max_page and i > 1:
            no_list.append(str(i))
    if curr_page + 20 < max_page:
        no_list.append('...')
    no_list.append(str(max_page))
    return no_list

def highlight(review_content, match_list):
    for m in match_list:
        review_content = review_content.replace(m, '<font color="red">%s</font>' % (m))
    return review_content

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
    #app.run(host='0.0.0.0', port=80, debug=False)
    #demo host: 
    #bizer host: search-arts-shopreview01.nh