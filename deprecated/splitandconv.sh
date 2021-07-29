if [ $# -ne 1 ]; then 
	echo "Split 128-channel file into two 64-channel files and convert them to dat files. Remove 64-channel bin files after conversion. Arguments: <128-channel_file_name>"
	exit
fi

split_interleaving ${1}.bin

Axona2dat3_15 ${1}.bin.64.1
mv ${1}.bin.64.dat ${1}_2h.dat 
rm ${1}.bin.64.axtrk

Axona2dat3_15 ${1}.bin.64.2
mv ${1}.bin.64.dat ${1}_1h.dat 
rm ${1}.bin.64.axtrk

rm ${1}.bin.64.1 ${1}.bin.64.2 ${1}.bin.64.digbin 

merge_interleaving ${1}_1h.dat ${1}_2h.dat ${1}.dat
rm ${1}_1h.dat ${1}_2h.dat

# axtrk extraction
bin2track ${1}.bin
