hive -e"
select review_id, shop_id, noun, adj ,noun_cat0, noun_cat1, adj_cat0,sentiment
from search.dpstg_wcw_review_summary_sh 
where review_id >=82775056 and noun_cat0 is not null 
">review.csv

hive -e"use search; desc dpstg_wcw_shop_review_summary"


hive -e"
use search;
select shop_id, tag
from dpstg_wcw_shop_review_summary 
">summary.csv