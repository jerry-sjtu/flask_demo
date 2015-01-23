# -*- coding: utf-8 -*-
import sys, codecs

def init_cluster(path):
    cluster_df = dict()
    fh = codecs.open(path, 'r', 'utf-8')
    for line in fh:
        if len(line.split('\t')) != 8:
            continue
        review_id, shop_id, noun, adj, noun_cat1, noun_cat2, adj_cat, sentiment = line.strip().split()
        cluster_df[review_id] = (noun, adj, noun_cat1, noun_cat2, adj_cat, sentiment)
    fh.close()
    return cluster_df