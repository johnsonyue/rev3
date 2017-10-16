import getopt
import json
import sys

fp = open("format.json",'rb')
format_json = json.loads(fp.read())

edge_dict = {}
def insert(arg_list):
	for arg in arg_list:
		if not edge_dict.has_key((arg[0],arg[1])):
			edge_dict[(arg[0],arg[1])] = [arg[2],arg[3],arg[4],1,arg[5],arg[6],arg[7],arg[7]]
			continue
		edge = edge_dict[(arg[0],arg[1])]
		if arg[2] == "N":
			edge[0] = "N"
		if arg[3] < edge[1]:
			edge[1] = arg[3]
		if arg[4] < edge[2]:
			edge[2] = arg[4]
		edge[3] += 1
		if arg[5] < edge[4] or (arg[5] == edge[4] and arg[6] < edge[5]):
			edge[4:6] = [arg[5],arg[6]]
		if arg[7] < edge[6]:
			edge[6] = arg[7]
		if arg[7] > edge[7]:
			edge[7] = arg[7]

def process():
	while True:
		try:
			line = raw_input()
		except EOFError:
			return
	
		if line[0] == "#":
			continue
		
		fields = line.strip('\n').split(format_json["fd"])
		monitor = fields[0]
		dstip = fields[1]
		timestamp = int(fields[2])
		if fields[3] == "":
			continue
		path = fields[3].split(format_json["hd"])
		
		links = []
		nodes = {}
		is_loop = False
		prev_ip = ""
		prev_rtt = 0
		prev_ttl = 0
		star = 0
		for i in range(len(path)):
			hop = path[i].split(format_json["td"])[0]
			if hop == format_json["bh"]:
				star += 1
				continue
			else:
				items = hop.split(format_json["itd"])
				ip = items[0]
				rtt = float(items[1])
				ttl = int(items[2])

				if prev_ip != "" and ip != prev_ip:
					if nodes.has_key(ip):
						is_loop = True
						break
					else:
						nodes[ip]=""
					delay = float(rtt - prev_rtt) / 2
					if delay < 0:
						delay = 0
					if i == len(path)-1 and hop.split(format_json["itd"])[0] == dstip:
						is_dest = "Y"
					else:
						is_dest = "N"
					links.append([prev_ip,ip,is_dest,star,delay,prev_ttl,monitor,timestamp])
				
				prev_ip = ip
				prev_rtt = rtt
				prev_ttl = ttl
				star = 0

		if not is_loop:
			insert(links)

def usage():
	print "trace2link [-o <$output_name>] -"

def main(argv):
	output_name = ""
	try:
		opts, args = getopt.getopt(argv[1:], "o:")
	except getopt.GetoptError as err:
		print str(err)
		usage()
		exit(2)

	for o,a in opts:
		if o == "-o":
			output_name = a
	
	process()
	
	#out
	#0.in, 1.out, 2.is_dst, 3.star, 4.delay, 5.freq, 6.ttl, 7.monitor, 8.firstseen, 9.lastseen
	edge_key_list = sorted( edge_dict.iterkeys(), key=lambda k:(k[0],k[1]) )
	if output_name == "":
		for key in edge_key_list:
			ingress = key[0]
			out = key[1]
			edge = edge_dict[key]
			edge_str = str(ingress) + format_json["sp"] + str(out)
			for i in range(len(edge)):
				e = edge[i]
				if i == 2:
					e = "%.3f" % float(e)
				edge_str += format_json["sp"] + str(e)
			print edge_str
	else:
		with open(output_name,'wb') as fp:
			for key in edge_key_list:
				ingress = key[0]
				out = key[1]
				edge = edge_dict[key]
				edge_str = str(ingress) + format_json["sp"] + str(out)
				for e in edge:
					edge_str += format_json["sp"] + str(e)
			fp.write(edge_str+"\n")
		fp.close()

if __name__ == "__main__":
	main(sys.argv)
