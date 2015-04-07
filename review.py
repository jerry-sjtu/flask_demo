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
BIZER_REVIEW_URL = "http://%s:4153/search/shopreview?query=term(reviewid,%s)&sort=desc(addtime)&fl=reviewid,reviewmatch,reviewtagsentiment"


@app.route("/")
def default():
    shopid = '14170562'
    abstract = request_abstract(shopid)
    page_dict = pare_review_info(shopid, 1)
    return render_template('review.html', val=page_dict, abstract=abstract, shopname=page_dict['shopname'])

@app.route('/<shopid>')
def view_by_shop(shopid):
    abstract = request_abstract(shopid)
    page_dict = pare_review_info(shopid, 1)
    return render_template('review.html', val=page_dict, abstract=abstract, shopname=page_dict['shopname'])

@app.route('/<shopid>/<pageno>')
def view_by_shop_page(shopid, pageno):
    abstract = request_abstract(shopid)
    page_dict = pare_review_info(shopid, pageno)
    return render_template('review.html', val=page_dict, abstract=abstract, shopname=page_dict['shopname'])


def request_abstract(shopid):
    url = BIZER_ABSTRACT_URL % (BIZER_HOST, shopid)
    i_headers = dict()
    request = urllib2.Request(url, headers=i_headers)
    response = urllib2.urlopen(request)
    decodejson = json.loads(response.read())
    return decodejson

def request_review(reviewid):
    reviewid = 101161774
    url = BIZER_REVIEW_URL % (BIZER_HOST, reviewid)
    i_headers = dict()
    request = urllib2.Request(url, headers=i_headers)
    response = urllib2.urlopen(request)
    decodejson = json.loads(response.read())
    return decodejson


def pare_review_info(shopid, pageno):
    url = BASE_URL % shopid
    if pageno > 1:
        url += '?pageno=%s' % (pageno)
    i_headers = dict()
    i_headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
    i_headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    i_headers['Accept-Encoding'] = 'gzip,deflate,sdch'
    i_headers['Accept-Language'] = 'zh-CN,zh;q=0.8'
    i_headers['Cache-Control'] = 'max-age=0'
    i_headers['Connection'] = 'keep-alive'
    i_headers['Host'] = 'www.dianping.com'
    request = urllib2.Request(url, headers=i_headers)
    response = urllib2.urlopen(request)
    r_dict = dict()
    review_list = list()
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO.StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        soup = BeautifulSoup(f.read())
        r_dict['review'] = review_list
        r_dict['pno_list'] = list()
        r_dict['shopid'] = shopid
        r_dict['curr_page'] = pageno
        for a in soup.find_all('div', class_='revitew-title') :
            r_dict['shopname'] = soup.h1.a.string
        for comment_list_div in soup.find_all('div', class_='comment-list'):
            ul = comment_list_div.ul
            for li in ul.find_all('li'):
                if 'data-id' not in li.attrs:
                    continue
                review_id = li.attrs["data-id"]
                biref_div = li.find('div', class_='J_brief-cont')
                review_content = biref_div.string
                if review_content == None:
                    review_content = u'%s' % (biref_div)
                    review_content = remove_html(review_content)
                time = li.find('span', class_='time').string
                review_abs = request_review(review_id)
                if len(review_abs['records']) > 0:
                    match_list = review_abs['records'][0]['reviewmatch'].split()
                    tag_list = review_abs['records'][0]['reviewtagsentiment'].split()
                    review_content = highlight(review_content, match_list)
                    review_list.append((review_id, time, review_content, tag_list))
        for a in soup.find_all('a', class_="PageLink"):
            r_dict['pno_list'].append(a.attrs['data-pg'])
    return r_dict


def remove_html(original_text):
    return original_text.replace('<div class="J_brief-cont">','').replace('<br/>', '').replace('</div>', '')

def highlight(review_content, match_list):
    for m in match_list:
        review_content = review_content.replace(m, '<font color="red">%s</font>' % (m))
    return review_content

if __name__ == "__main__":
    app.run(debug=True)
