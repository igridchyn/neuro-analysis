let NTET=`wc -l < TEMPLATE.par`-4
for TET in $(seq 0 ${NTET}); do
cd tet${TET}/
cp tet${TET}.clu tet${TET}_PRECLEAN.clu
cp tet${TET}.res tet${TET}_PRECLEAN.res
cp tet${TET}.clean.clu tet${TET}.clu
cp tet${TET}.clean.res tet${TET}.res
cd ..
done
