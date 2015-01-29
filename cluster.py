# -*- coding: utf-8 -*-
import sys, codecs

def init_cluster(path):
    #review id of 2014-06-01
    min_id = 56913632
    cluster_df = dict()
    fh = codecs.open(path, 'r', 'utf-8')
    for line in fh:
        if len(line.split('\t')) != 8:
            continue
        review_id, shop_id, noun, adj, noun_cat1, noun_cat2, adj_cat, sentiment = line.strip().split()
        if noun_cat1 == 'NULL':
            continue
        if int(review_id) <= min_id:
            continue
        if review_id not in cluster_df:
            cluster_df[review_id] = list()
        cluster_df[review_id].append((noun, adj, noun_cat1, noun_cat2, adj_cat, sentiment))
    fh.close()
    return cluster_df

def init_scene(path):
    cluster_df = dict()
    fh = codecs.open(path, 'r', 'utf-8')
    for line in fh:
        if len(line.split('\t')) != 2:
            continue
        word, scene = line.strip().split()
        cluster_df[word] = scene
    fh.close()
    return cluster_df