import sys
import getopt
from sets import Set
import subprocess

edge_dict = {}

def merge(a,b):
	#0.in, 1.out, 2.is_dst, 3.star, 4.delay, 5.freq, 6.ttl, 7.monitor, 8.firstseen, 9.lastseen
	if b[0] == "N":
		a[0] = "N"
	if int(b[1]) < int(a[1]):
		a[1] = b[1]
	if float(b[2]) < float(a[2]):
		a[2] = b[2]
	a[3] = str(int(a[3]) + int(b[3]))
	if int(b[4]) < int(a[4]):
		a[4] = b[4]
		a[5] = b[5]
	elif b[4] == a[4]:
		a[5] = b[5] if b[5] < a[5] else a[5]
	if int(b[6]) < int(a[6]):
		a[6] = b[6]
	if int(b[7]) > int(a[7]):
		a[7] = b[7]
	return a

def insert(a,b,attr):
	aid = (ip2router[a] if ip2router.has_key(a) else len(router_list))
	if ( aid == len(router_list) ):
		router_list.append(Set([a]))
		router_type.append('h')
		ip2router[a] = aid
	bid = (ip2router[b] if ip2router.has_key(b) else len(router_list))
	if ( bid == len(router_list) ):
		router_list.append(Set([b]))
		router_type.append('h')
		ip2router[b] = aid
	
	if not edge_dict.has_key((aid,bid)):
		edge_dict[(aid,bid)] = attr
	else:
		edge_dict[(aid,bid)] = merge(edge_dict[(aid,bid)],attr)

router_ip = {}
router_list = []
router_type = []
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
	global router_type
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
	router_type = [ 'r' for i in range(len(router_list)) ]
	for k,v in router_ip.items():
		if v != 1:
			ip2router[k] = len(router_list)
			router_list.append([k])
			router_type.append('r')
	
	with open(edge,'rb') as ef:
		for line in ef.readlines():
			line=line.strip('\n')
			insert(line.split(' ')[0],line.split(' ')[1],line.split(' ')[2:])
	ef.close()
	
	#write
	with open(prefix+".node",'wb') as of:
		for i in range(len(router_list)):
			of.write( "Node" + str(i) + "," + str(router_type[i]) + ",")
			r = router_list[i]
			if_str = ""
			for f in r:
				if_str += f+" "
			of.write( if_str.strip(" ") + "\n")
	of.close()

	with open(prefix+".edge",'wb') as of:
		for k,v in edge_dict.items():
			of.write("Node" + str(k[0]) + ",Node" + str(k[1]))
			for f in v:
				of.write("," + str(f))
			of.write("\n")
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
