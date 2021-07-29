inotifywait -m . -e create  |
    while read path action file; do
        # echo "The file '$file' appeared in directory '$path' via '$action'"
        # do something with the file
	if [[ $file =~ \.bin$ ]]; then
		echo "New BIN-file spotted, start conversion to dat"
		basename=${file%.bin}
		day=1220
		session="${basename##*_}"
		echo "Session='$session'"

		# it is faster to do this on a recording computer
		# cd /home/igor/code/ews/lfp_online/sdl_example/Debug
		# (./lfp_online ../Res/spike_dump_128.conf day=${day} session=${session} ; ./lfp_online ../Res/spike_display_jc157.conf day=${day} session=${session} ) &
		# cd -

		splitandconv.sh $basename
		echo "Processing of '$file' is done."
		zenity --info --text="Processing '$basename' is done, start regaa quarters 1-by-1"
		regaamc8 ${basename}.dat 128 42 ../regaa_jc157_gen_q1.conf
		regaamc8 ${basename}.dat 128 42 ../regaa_jc157_gen_q2.conf
		regaamc8 ${basename}.dat 128 42 ../regaa_jc157_gen_q3.conf
		regaamc8 ${basename}.dat 128 42 ../regaa_jc157_gen_q4.conf
	fi
	
    done
