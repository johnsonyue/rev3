import getopt
import json
import sys

fp = open("format.json",'rb')
format_json = json.loads(fp.read())

edge_dict = {}
def insert(ingress, out, is_dst, star, delay, ttl, monitor):
	if not edge_dict.has_key((ingress,out)):
		edge_dict[(ingress,out)] = [is_dst,star,delay,1,ttl,monitor]
		return
	edge = edge_dict[(ingress,out)]
	if is_dst == "n":
		edge[0] = "n"
	if star < edge[1]:
		edge[1] = star
	if delay < edge[2]:
		edge[2] = delay
	edge[3] += 1
	if ttl < edge[4] or (ttl == edge[4] and monitor < edge[5]):
		edge[4:6] = [ttl,monitor]

def process():
	while True:
		try:
			line = raw_input()
		except EOFError:
			return
		
		fields = line.strip('\n').split(format_json["fd"])
		monitor = fields[0]
		dstip = fields[1]
		timestamp = int(fields[2])
		path = fields[3].split(format_json["hd"])
		
		prev_ip = ""
		prev_rtt = 0
		star = 0
		for i in range(len(path)):
			hop = path[i]
			if hop == "q":
				star += 1
				continue
			else:
				ip = hop.split(format_json["itd"])[0]
				rtt = float(hop.split(format_json["itd"])[1])

				if prev_ip != "":
					delay = (prev_rtt - rtt) / 2
					if delay < 0:
						delay = 0
					if i == len(path)-1 and hop.split(format_json["itd"])[0] == dstip:
						is_dest = "y"
					else:
						is_dest = "n"
					insert(prev_ip,ip,is_dest,star,delay,i+1,monitor)
				
				prev_ip = ip
				prev_rtt = rtt
				star = 0

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
	
	edge_key_list = sorted( edge_dict.iterkeys(), key=lambda k:(k[0],k[1]) )
	if output_name == "":
		for key in edge_key_list:
			ingress = key[0]
			out = key[1]
			edge = edge_dict[key]
			edge_str = str(ingress) + "," + str(out)
			for e in edge:
				edge_str += "," + str(e)
			print edge_str
	else:
		with open(output_name,'rb') as fp:
			for key in edge_key_list:
				ingress = key[0]
				out = key[1]
				edge = edge_dict[key]
				edge_str = str(ingress) + "," + str(out)
				for e in edge:
					edge_str += "," + str(e)
			fp.write(edge_str+"\n")
		fp.close()

if __name__ == "__main__":
	main(sys.argv)