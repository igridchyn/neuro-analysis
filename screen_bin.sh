# run BIN->DAT + regaa + lfpo dump + lfpo display (to speed up screening process)

animal=jc184
day=$1
session=$2

# start dumping and subsequent display
cd /home/igor/code/ews/lfp_online/sdl_example/Debug
./lfp_online ../Res/spike_dump.conf day=${day} session=${session} && ./lfp_online ../Res/spike_display_screening.conf day=${day} session=${session} &

# start Axona2dat and then regaa for all quarters
cd -
Axona2dat3_15_128 ${animal}_${day}_${session}.bin
regaamc8 ${animal}_${day}_${session}.dat 128 42 ../regaa_${animal}_q1.conf
regaamc8 ${animal}_${day}_${session}.dat 128 42 ../regaa_${animal}_q2.conf
regaamc8 ${animal}_${day}_${session}.dat 128 42 ../regaa_${animal}_q3.conf
regaamc8 ${animal}_${day}_${session}.dat 128 42 ../regaa_${animal}_q4.conf
