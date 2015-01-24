#!/usr/bin/python
#coding=utf-8
import math
x_pi = 3.14159265358979324 * 3000.0 / 180.0

def google_to_baidu(glat,glng):
	z = math.sqrt(glat*glat + glng*glng) + 0.00002*math.sin(glat * x_pi)
	theta = math.atan2(glat,glng) + 0.000003*math.cos(glng*x_pi)
	blat = z*math.sin(theta) + 0.006
	blng = z*math.cos(theta) + 0.0065
	return blat,blng



name = 'mt_price'

dp_file = open(name + '.out','r')
dp_outfile = open(name + '.js','w')
outline = ''
for line in dp_file:
	lat,lng,count = line.strip().split('\t')
	lat,lng = google_to_baidu(float(lat),float(lng))
	outline = outline +  '{\"lng\":' + str(lng) + ',' + '\"lat\":' + str(lat) + ',\"count\":' + count + '},\n'
outline = 'var '+ name + '=[ \n' + outline[:len(outline)-2] + '];'
dp_outfile.write(outline)
dp_outfile.close()
dp_file.close()
