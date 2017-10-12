import os
import shutil
import sys
import getopt
import json
import heapq

import time

fp = open("format.json",'rb')
format_json = json.loads(fp.read())

x = 0
y = 0
output_name = "default.output"

def merge_2_lines(al,bl):
	#0.in, 1.out, 2.is_dst, 3.star, 4.delay, 5.freq, 6.ttl, 7.monitor, 8.firstseen, 9.lastseen
	if bl[2] == "N":
		al[2] = "N"
	if int(bl[3]) < int(al[3]):
		al[3] = bl[3]
	if float(bl[4]) < float(al[4]):
		al[4] = bl[4]
	al[5] = str(int(al[5]) + int(bl[5]))
	if int(bl[6]) < int(al[6]):
		al[6] = bl[6]
		al[7] = bl[7]
	elif bl[6] == al[6]:
		al[7] = bl[7] if bl[7] < al[7] else al[7]
	if int(bl[8]) < int(al[8]):
		al[8] = bl[8]
	if int(bl[9]) > int(al[9]):
		al[9] = bl[9]
	return al

def write_line(pl,fo):
	line_str = ""
	for i in pl:
		line_str += i + format_json["sp"]
	fo.write(line_str.strip(format_json["sp"])+"\n")
		
def merge_x_files(ifn_list,temp_fn):
	fo = open(temp_fn,'wb')
	ifp_list = map( lambda x:open(x,'rb'), ifn_list )

	#grab x*y lines from disk
	line_list = [ [] for i in range(len(ifn_list)) ]
	for i in range(len(ifp_list)):
		fp=ifp_list[i]
		for j in range(y):
			line = fp.readline()
			if not line:
				break
			line_list[i].append(line)

	cursor_list = [ 0 for i in range(len(line_list)) ]
	
	#init enqueue
	pq = [] #priority queue
	pl = [] #previous line
	for i in range(len(line_list)):
		if cursor_list[i] < len(line_list[i]):
			heapq.heappush( pq, (line_list[i][cursor_list[i]],i) )
			cursor_list[i] += 1

	while True:
		if len(pq) == 0:
			if len(pl) != 0:
				write_line(pl,fo)
			break

		a = heapq.heappop(pq)
		al = a[0].strip('\n').split(format_json["sp"])
		if al[0:2] == pl[0:2]:
			al = merge_2_lines(al,pl)
		elif len(pl) != 0:
			write_line(pl,fo)
		pl = al

		i = a[1]
		if cursor_list[i] == len(line_list[i]):
			line_list[i] = []
			fp = ifp_list[i]
			for j in range(y):
				line = fp.readline()
				if not line:
					break
				line_list[i].append(line)
			cursor_list[i] = 0
		
		if len(line_list[i]) != 0:
			heapq.heappush( pq, (line_list[i][cursor_list[i]],i) )
			cursor_list[i] += 1

	map( lambda x:x.close(), ifp_list )
	fo.close()

def merge(ifn_list,del_org=False):
	temp_ifn_list = []
	for i in range(0,len(ifn_list),x):
		temp_fn = str(len(ifn_list))+"."+str(i)+"."+str(i+x)
		merge_x_files(ifn_list[i:i+x],temp_fn)
		temp_ifn_list.append(temp_fn)
	if del_org:
		for fn in ifn_list:
			os.remove(fn)
	if len(temp_ifn_list) == 1:
		#os.rename(temp_ifn_list[0], output_name)
		shutil.move(temp_ifn_list[0], output_name)
		return
	merge(temp_ifn_list,del_org=True)

def usage():
	print "mergelinks [-i <$input_name>]+ -"

def main(argv):
	global x
	global y
	global output_name
	ifn_list = []
	tmp_dir = ""

	try:
		opts, args = getopt.getopt(argv[1:], "d:i:o:x:y:")
	except getopt.GetoptError as err:
		print str(err)
		usage()
		exit(2)

	for o,a in opts:
		if o == "-i":
			ifn_list.append(a)
		if o == "-o":
			output_name = a
		if o == "-d":
			tmp_dir = a
		if o == "-x":
			x = int(a)
		if o == "-y":
			y = int(a)
	
	if len(ifn_list) == 0:
		while True:
			try:
				line=raw_input()
			except EOFError:
				break
			ifn_list.append(line.strip('\n'))

	if x == 0:
		x = len(ifn_list)
	if y == 0:
		y = 1000
	if tmp_dir == "":
		tmp_dir = "tmp"
	if not os.path.exists(tmp_dir):
		os.makedirs(tmp_dir)

	merge(ifn_list)

if __name__ == "__main__":
	main(sys.argv)
