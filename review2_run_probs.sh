ANIMAL=$1
DAY=$2

cd /hdr/data/bindata/$ANIMAL/$DAY/
cl 2 `ls -t *.sw | head -1` > swrpeak
tail -n +6 swrpeak > swrpeak
cp swrpeak ../../../processing/$ANIMAL/$DAY/13ssi
cd ../../../processing/$ANIMAL/$DAY/8pres/

