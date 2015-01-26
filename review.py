# -*- coding: utf-8 -*-
from flask import Flask
from bs4 import BeautifulSoup
import urllib2
import StringIO
import gzip
import cookielib
from flask import render_template
import cluster

app = Flask(__name__)
BASE_URL = 'http://www.dianping.com/shop/%s/review_all'
CLUSTER_PATH = 'data/review_summary_sh.csv'
print 'start to load cluster information'
cluster_dict = cluster.init_cluster(CLUSTER_PATH)
print 'end to load cluster information'

@app.route("/")
def default():
    shopid = '14170562'
    r_dict1 = pare_review_info(shopid, 20)
    r_dict2 = pare_review_info(shopid, 21)
    r_dict1['review'] += r_dict2['review'] 
    return render_template('review.html', val=r_dict1)

@app.route('/<shopid>')
def view_by_shop(shopid):
    r_dict1 = pare_review_info(shopid, 20)
    r_dict2 = pare_review_info(shopid, 21)
    r_dict1['review'] += r_dict2['review'] 
    return render_template('review.html', val=r_dict1)


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
                    review_content = review_content.replace('<div class="J_brief-cont">','').replace('<br/>', '').replace('</div>', '')
                time = li.find('span', class_='time').string
                #cluster information:noun, adj, noun_cat1, noun_cat2, adj_cat, sentiment
                if review_id in cluster_dict:
                    noun, adj, noun_cat1, noun_cat2, adj_cat, sentiment = cluster_dict[review_id]
                    review_list.append((review_id, time, review_content, noun, adj, noun_cat1, noun_cat2, adj_cat, sentiment))
                else:
                    review_list.append((review_id, time, review_content, 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL'))
    return r_dict

if __name__ == "__main__":
    app.run(debug=True)
