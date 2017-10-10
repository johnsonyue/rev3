data_dir=/home/yzx/probing/
kapar_path=kapar-0.5/kapar/kapar
year_month=201706
out_file_name=$year_month.router

#generates alias files
arr=($(ls $data_dir/ | grep "^$year_month.*"))

tgt=$data_dir/iffinder.pairs
[ -f $tgt ] && echo "rm $tgt" && rm $tgt #rewrite the pairs

for d in ${arr[*]}; do
	iffinder_file=$(ls $data_dir/$d/* | grep "iffinder")
	[ ! -z "$iffinder_file" ] && tar zxvf $iffinder_file -O | grep -v "^#.*" | grep -v "^$" | awk -F ' *' '$(NF-2)=="D" { print $1" "$2; }' >> $tgt
done

#uncompress the .tar.gz which is not ideal
for d in ${arr[*]}; do
	cwd=$(pwd)
	cd $data_dir/$d
	tar zxvf $(ls | grep ".*warts\.tar\.gz")
	cd cwd
done

cmd=$(
echo "$kapar_path -il -py -r31 -sir -c0.5 -nv -adms -d1 -mn -lb -1a -oals -O $out_file_name -z 24 "
echo "-A $tgt "
for d in ${arr[*]}; do
	echo "-P $(ls $data_dir/$d/* | grep ".*warts$") "
done
)

echo $cmd
eval $cmd

#uncompress the .tar.gz which is not ideal
printf "cleaning up ... "
for d in ${arr[*]}; do
	cwd=$(pwd)
	cd $data_dir/$d
	rm $(ls | grep ".*warts$")
	cd cwd
done
echo "done."
