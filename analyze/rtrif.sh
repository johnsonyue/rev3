#!/bin/bash
mper_port=8746
interface=eth0
gateway=172.17.0.1
iffinder=/home/iffinder-1.38/iffinder

usage(){
	echo 'rtrif -i <$input> -o <$output>'
}

while getopts "i:o:" opt; do
	case "$opt" in
		i)
			input=$OPTARG ;;
		o)
			output=$OPTARG ;;
		*)
			usage
			exit -1;;
	esac
done

test -z "$input" && usage && exit
test -z "$output" && usage && exit

#cat << "STUFF"
#cat $input | python <(
#cat << END
#while True:
#  try:
#    line=raw_input()
#  except:
#    break
#  fields = line.split(' ')
#  print fields[0]
#  print fields[1]
#END
#) | sort | uniq >total
#STUFF
#
#cat $input | python <(
#cat << END
#while True:
#  try:
#    line=raw_input()
#  except:
#    break
#  fields = line.split(' ')
#  print fields[0]
#  print fields[1]
#END
#) | sort | uniq >total
#
#echo "cat $input | cut -d ' ' -f 1 | sort | uniq >deg0"
#cat $input | cut -d ' ' -f 1 | sort | uniq >deg0
#echo "cat $input | grep 'Y' | cut -d ' ' -f 2 | sort | uniq >rpl"
#cat $input | grep 'Y' | cut -d ' ' -f 2 | sort | uniq >rpl
#echo "comm -2 -3 rpl deg0 | sort >host"
#comm -2 -3 rpl deg0 | sort >host
#echo "comm -2 -3 total host >router"
#comm -2 -3 total host >router

cat << "STUFF"
cat $input | python <(
cat << END
out={}
while True:
  try:
    line=raw_input()
  except:
    break
  fields = line.split(' ')
  print fields[0]
  if not out.has_key(fields[1]):
    out[fields[1]] = fields[2]
  elif fields[2] == "Y":
    out[fields[1]] = "Y"
for k,v in out.items():
  if v == "N":
    print k
END
) | sort | uniq >router
STUFF

cat $input | python <(
cat << END
out={}
while True:
  try:
    line=raw_input()
  except:
    break
  fields = line.split(' ')
  print fields[0]
  if not out.has_key(fields[1]):
    out[fields[1]] = fields[2]
  elif fields[2] == "Y":
    out[fields[1]] = "Y"
for k,v in out.items():
  if v == "N":
    print k
END
) | sort | uniq >router

#kill `ps -ef | grep iffinder | awk '{print $2}'` >/dev/null 2>&1 #kill active iffinder.
#echo "$iffinder -d -o $output -c 200 -r 500 rst"
#$iffinder -d -o $output -c 200 -r 500 rst
