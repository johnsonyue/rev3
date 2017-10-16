import sys
import os
import json
import getopt
from sets import Set

import subprocess

fp = open("format.json",'rb')
format_json = json.loads(fp.read())

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
	for i in pl[:2]:
		if not "." in i:
			i = min(router_list[int(i)])
		line_str += i + format_json["sp"]
			
	for i in pl[2:]:
		line_str += i + format_json["sp"]
	fo.write(line_str.strip(format_json["sp"])+"\n")

def insert(a,b,attr,h):
	aid = ip2router[a] if ip2router.has_key(a) else a
	bid = ip2router[b] if ip2router.has_key(b) else b
	
	h.stdin.write( str(aid) + format_json["sp"] + str(bid) + format_json["sp"] + attr )

router_ip = {}
router_list = []
deleted = []
ip2router = {}

def aggr(a,b):
	if router_ip.has_key(a):
		router_ip[a]=1
	if router_ip.has_key(b):
		router_ip[b]=1

	aid = -1
	if ip2router.has_key(a):
		aid = ip2router[a]
	bid = -1
	if ip2router.has_key(b):
		bid = ip2router[b]

	if aid < 0 and bid < 0:
		rid = len(router_list)
		router_list.append(Set([a,b]))
		ip2router[a] = rid
		ip2router[b] = rid
		deleted.append(False)
	elif aid >= 0 and bid >= 0:
		if aid != bid:
			router_list[aid]=router_list[aid].union(router_list[bid])
			for i in router_list[bid]:
				ip2router[i] = aid
			deleted[bid] = True
	else:
		if aid >= 0:
			ip2router[b] = aid
			router_list[aid].add(b)
		else:
			ip2router[a] = bid
			router_list[bid].add(a)

def process(router,alias,edge,prefix):
	global router_list
	#read
	with open(router,'rb') as rf:
		for line in rf.readlines():
			router_ip[line.strip('\n')] = ""
	rf.close()

	with open(alias,'rb') as af:
		for line in af.readlines():
			line=line.strip('\n')
			aggr(line.split()[0],line.split()[1])
	af.close()

	router_list = [ router_list[i] for i in range(len(router_list)) if not deleted[i] ]
	for k,v in router_ip.items():
		if v != 1:
			ip2router[k] = len(router_list)
			router_list.append([k])

	with open(edge,'rb') as ef:
		efto = open(edge+".tmp",'wb') 
		h = subprocess.Popen(['sort','--parallel','4'], stdin=subprocess.PIPE, stdout=efto)
		for line in ef.readlines():
			insert(line.split(' ')[0],line.split(' ')[1],line.split(' ',2)[2],h)
	h.stdin.close()
	efto.close()
	ef.close()

	h.wait()
	#write
	with open(prefix+".node",'wb') as of:
		for i in range(len(router_list)):
			r = router_list[i]
			if_str = ""
			for f in sorted(r):
				if_str += f+" "
			of.write( if_str.strip(" ") + "\n")
	of.close()

	with open(prefix+".edge",'wb') as of:
		efti = open(edge+".tmp",'rb')
		pl = []
		al = efti.readline().strip('\n').split(' ')
		while True:
			line = efti.readline()
			if line == "":
				if pl == [] or al[0:2] == pl[0:2]:
					write_line(al,of)
				break
			pl = al
			al = line.strip('\n').split(' ')
			if al[0:2] == pl[0:2]:
				al = merge_2_lines(al,pl)
			else:
				write_line(pl,of)

	efti.close()
	#os.remove(edge+".tmp")
	of.close()

def usage():
	print "rtrtopo -r <$router-file> -e <$edge-file> -a <$alias-file> -p <$prefix>"

def main(argv):
	try:
		opts, args = getopt.getopt(argv[1:], "ha:e:r:p:")
	except getopt.GetoptError as err:
		print str(err)
		usage()
		exit(2)

	alias = ""
	edge = ""
	router = ""
	prefix = "default"
	for o,a in opts:
		if o == "-h":
			usage()
			exit(0)
		elif o == "-r":
			router = a
		elif o == "-a":
			alias = a
		elif o == "-e":
			edge = a
		elif o == "-p":
			prefix = a
		
	if alias == "" or edge == "" or router == "":
		usage()
		exit(2)
	
	process(router,alias,edge,prefix)

if __name__ == "__main__":
	main(sys.argv)
