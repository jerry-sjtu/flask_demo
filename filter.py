# -*- coding: utf-8 -*-
import sys, codecs

fh1 = codecs.open(sys.argv[1], 'r', 'utf-8')
fh2 = codecs.open(sys.argv[2], 'w', 'utf-8')
for line in fh1:
        review_id, shop_id, noun, adj, noun_cat1, noun_cat2, adj_cat, sentiment = line.strip().split()
        if int(review_id) > 56913632:
                fh2.write(line)
fh1.close()
fh2.close()