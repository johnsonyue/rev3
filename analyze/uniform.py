import sys
import json

fp = open("format.json",'rb')
format_json = json.loads(fp.read())

def transform_caida():
	while True:
		try:
			line = raw_input()
		except EOFError:
			exit()
	
		#comments and header line
		if (line[0] == "#"):
			continue
		
		#trace lines
		fields = line.strip('\n').split('\t', 13)
		if (len(fields) < 14): #skip cases where there's no hop at all
			continue
		
		srcip = fields[1]
		dstip = fields[2]

		timestamp = fields[5]
		
		path = fields[13]
		path_str = ""
		for hop in path.split('\t'):
			path_str += hop + format_json["hd"]
		path_str = path_str.strip(format_json["hd"])
		replied = fields[6]
		dst_rtt = fields[7]
		path_str += "" if replied == "N" else format_json["hd"] + str(dstip) + format_json["itd"] + str(dst_rtt) + format_json["itd"] + str(1)

		print str(src_ip) + format_json["fd"] + str(dstip) + format_json["fd"] + str(timestamp) + format_json["fd"] + str(path_str)
			
		'''
		rpl_ttl = fields[9]
		halt_reason = fields[10]
		halt_data = fields[11]
		extra = str(halt_reason) + format_json["ed"] + str(halt_data) + format_json["ed"] + rpl_ttl
		'''
		
		#print str(dstip) + format_json["fd"] + str(timestamp) + format_json["fd"] + str(path_str) + format_json["fd"] + str(extra)

def transform_iplane():
	path = []
	srcip = ""
	dstip = ""
	timestamp = ""
	while True:
		try:
			line = raw_input()
		except EOFError:
			exit()
	
		if (line[0] == "#"):
			src = line.split(' ')[0]
			timestamp = line.split(' ')[1]
			continue
		
		fields = line.strip('\n').split(' ')
		if fields[0] == "read":
			continue
		elif fields[0] == "destination:":
			if len(path) != 0:
				path_str=""
				for hop in path:
					path_str += hop + format_json["hd"]
				path_str.strip(format_json["hd"])
				print str(srcip) + format_json["fd"] + str(dstip) + format_json["fd"] + str(timestamp) + format_json["fd"] + str(path_str)

			dstip = fields[1]
			path = []
		else:
			if fields[1] != "0.0.0.0":
				hop_str = fields[1] + format_json["itd"] + fields[2] + format_json["itd"] + str(1)
			else:
				hop_str = format_json["bh"]
			path.append(hop_str)
	
	path_str=""
	for hop in path:
		path_str += hop + format_json["hd"]
	path_str.strip(format_json["hd"])
	print str(srcip) + format_json["fd"] + str(dstip) + format_json["fd"] + str(timestamp) + format_json["fd"] + str(path_str)

def transform_ripeatlas():
	while True:
		try:
			line = raw_input()
		except EOFError:
			exit()
		trace_obj = json.loads(line)
		
		result_list = json.loads(trace_obj["results_json"])
		for result in result_list:
			srcip = result["from"]
			if not result.has_key("dst_addr"):
				continue
			dstip = result["dst_addr"]
			timestamp = result["endtime"]

			path = result["result"]
			path_str = ""
			for hop in path:
				if hop.has_key("error"):
					continue

				tpl_dict = {}
				for i in range(len(hop["result"])):
					tpl = hop["result"][i]
					if tpl.has_key("x"):
						continue
					if not tpl.has_key("rtt"):
						continue
					if not tpl_dict.has_key(tpl["from"]):
						tpl_dict[tpl["from"]] = [float(tpl["rtt"]),i+1]
					elif float(tpl["rtt"]) < tpl_dict[tpl["from"]]:
						tpl_dict[tpl["from"]][0] = float(tpl["rtt"])

				hop_str = ""
				for ip in sorted(tpl_dict.keys(), key=lambda x:tpl_dict[x][1]):
					rtt = tpl_dict[ip][0]
					ntries = tpl_dict[ip][1]
					hop_str += str(ip) + format_json["itd"] + str(rtt) + format_json["itd"] + str(ntries) + format_json["td"]
				hop_str = hop_str.strip(format_json["td"])

				if hop_str == "":
					hop_str = format_json["bh"]
				
				path_str += str(hop_str) + format_json["hd"]
			path_str.strip(format_json["hd"])
		
			print str(srcip) + format_json["fd"] + str(dstip) + format_json["fd"] + str(timestamp) + format_json["fd"] + str(path_str)

def usage():
	print "uniform caida/iplane/ripeatlas"

def main(argv):
	if (len(argv) != 2):
		usage()
		exit()
		
	source = argv[1]
	if source == "caida":
		transform_caida()
	elif source == "iplane":
		transform_iplane()
	elif source == "ripeatlas":
		transform_ripeatlas()

if __name__ == "__main__":
	main(sys.argv)
