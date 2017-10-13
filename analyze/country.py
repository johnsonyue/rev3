import sys
import json
import getopt
import subprocess

from geoip import geoip

fp = open("format.json",'rb')
format_json = json.loads(fp.read())

prefix = ""
GZIP_OUTPUT = True

def write(line, country, handle_dict):
	if not handle_dict.has_key(country):
		filename = str(prefix) + "." + str(country)
		if GZIP_OUTPUT:
			filename += ".gz"

		fpo = open(filename, 'wb')
		if GZIP_OUTPUT:
			h = subprocess.Popen(['gzip', '-c', '-'], stdin=subprocess.PIPE, stdout=fpo)
			handle = h.stdin
		else:
			handle = fpo
		handle_dict[country] = handle
	else:
		handle = handle_dict[country]
	
	handle.write(line + "\n")

def process(country_list,db_list):
	helper = geoip.geoip_helper(db_list)
	handle_dict = {}
	while True:
		try:
			line = raw_input()
		except EOFError:
			exit()
	
		if (line[0] == "#"):
			continue
		
		fields = line.split(format_json["fd"])
		dstip = fields[1]
		geo = helper.query(dstip)
		
		#order in list represents priority
		for db in db_list:
			if geo[db] == "" or not geo[db]["country"] in country_list:
				continue
			if geo[db]["country"] in country_list:
				write(line, geo[db]["country"], handle_dict)

	#clear up
	for handle in handle_dict.itervalues():
		handle.close()

def usage():
	print "country -p prefix -"

def main(argv):
	global prefix
	global GZIP_OUTPUT

	try:
		opts, args = getopt.getopt(argv[1:], "p:")
	except getopt.GetoptError as err:
		print str(err)
		usage()
		exit(2)

	country_list = [
		"CN","US","JP","KR","RU",
		"SY","IR","LY","AF","IQ",
		"PK","TW","HK"
	]
	#db_list = [ "bgp", "czdb", "mmdb", "ip2location" ]
	db_list = [ "mmdb" ]

	for o,a in opts:
		if o == "-p":
			prefix = a
		elif o == "-n":
			GZIP_OUTPUT = False

	if prefix == "":
		exit(2)
	
	process(country_list,db_list)
	
if __name__ == "__main__":
	main(sys.argv)
