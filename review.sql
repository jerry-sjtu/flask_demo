hive -e"
select review_id, shop_id, noun, adj ,noun_cat0, noun_cat1, adj_cat0,sentiment
from search.dpstg_wcw_review_summary_sh_2 
where review_id >=56913632 and noun_cat0 is not null 
">review.csv