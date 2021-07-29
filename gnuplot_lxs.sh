rm plot_lx.plg
echo "plot filename matrix with image" >> plot_lx.plg
echo "pause 1" >> plot_lx.plg

for i in `seq 1 16`;
do
	gnuplot -e "filename='pf_${i}_lx.mat'" plot_lx.plg
done

# plot lx matrices with delays
