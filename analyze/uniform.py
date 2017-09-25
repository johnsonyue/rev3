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

		print str(dstip) + format_json["fd"] + str(timestamp) + format_json["fd"] + str(path_str)
			
		'''
		rpl_ttl = fields[9]
		halt_reason = fields[10]
		halt_data = fields[11]
		extra = str(halt_reason) + format_json["ed"] + str(halt_data) + format_json["ed"] + rpl_ttl
		'''
		
		#print str(dstip) + format_json["fd"] + str(timestamp) + format_json["fd"] + str(path_str) + format_json["fd"] + str(extra)

def transform_iplane():
	path = []
	dstip = ""
	timestamp = ""
	while True:
		try:
			line = raw_input()
		except EOFError:
			exit()
	
		if (line[0] == "#"):
			timestamp = line.split(' ')[1]
			continue
		
		fields = line.strip('\n').split(' ')
		if fields[0] == "read":
			continue
		elif fields[0] == "destination:":
			if len(path) != 0:
				path_str=""
				for hop in path:
					path_str += hop[0] + format_json["itd"] + hop[1] + format_json["itd"] + str(1) + format_json["hd"]
				path_str.strip(format_json["hd"])
				print str(dstip) + format_json["fd"] + str(timestamp) + format_json["fd"] + str(path_str)

			dstip = fields[1]
			path = []
		else:
			path.append(fields[1:3])
	
	path_str=""
	for hop in path:
		path_str += hop[0] + format_json["itd"] + hop[1] + format_json["itd"] + str(1) + format_json["hd"]
	path_str.strip(format_json["hd"])
	print str(dstip) + format_json["fd"] + str(timestamp) + format_json["fd"] + str(path_str)

def transform_ripeatlas():
	return

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
		traceform_ripeatlas()

if __name__ == "__main__":
	main(sys.argv)
