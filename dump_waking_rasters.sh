for TRIAL in `seq 11 20`;
do
raster_waking.py %{animal}_%{day}_9l. `sed "${TRIAL}q;d" $1whl.trials` 0 -awin 3600 -sel 1.2 -resp ../7reg%{FULL}/pulses.timestamps.responses -skip 0 -minpfr 0.0 -maxpfr 4 -mincoh 0 -maxsp 1.0 -rinh -0.1 -rdinh 1.0 -targ $2
done

