#!/usr/bin/env bash

szth=1000
peath=2
cvth=3

rm an_mod_p an_mod_r parcor an_an_p pearcor an_pp3_p an_pp2_p an_anc_p an_pyr_p an_pra_p
for vint in 10 20 50 100 # was +2,200 before
do
        echo $vint      

        paste  cc dd bb ee3.$vint aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$11}' >aap1; stparcor aap1 >> parcor
        paste  cc dd bb ee3.$vint aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$11}' >aap2; stparcor aap2 >> parcor
        paste  cc dd bb ee3.$vint aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10,$11}' >aap3; stparcor aap3 >> parcor
#       Rscript anova_model_test.R

        paste  cc dd bb ee3.$vint aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$11}' >aapy1; stparcor aapy1 >> parcor
        paste  cc dd bb ee3.$vint aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$11}' >aapy2; stparcor aapy2 >> parcor
        paste  cc dd bb ee3.$vint aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10,$11}' >aapy3; stparcor aapy3 >> parcor

        # with animal
        paste  cc dd bb ee3.$vint aaint aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$11,$13,$15}' >aa1
        paste  cc dd bb ee3.$vint aaint aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$11,$13,$15}' >aa2
        paste  cc dd bb ee3.$vint aaint aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10,$11,$13,$15}' >aa3
        # writes an_an_p, an_pp2_p, an_pp3_p, an_mod_p
        Rscript --verbose anova_model_test_animal.R

        # for python, no animal
        paste  cc dd bb ee3.$vint aaint aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$11,$13}' >aapt1
        paste  cc dd bb ee3.$vint aaint aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$11,$13}' >aapt2
        paste  cc dd bb ee3.$vint aaint aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10,$11,$13}' >aapt3

        paste  cc dd bb ee3.$vint aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8}' >aa1s; stpearcor aa1s >> pearcor
        paste  cc dd bb ee3.$vint aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9}' >aa2s; stpearcor aa2s >> pearcor
        paste  cc dd bb ee3.$vint aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10}' >aas3; stpearcor aa3s >> pearcor

        if [ $vint -eq 50 ]
        then
            awk '{print $1, $2}' aa1 > tmp1; stpearcorse tmp1 | awk '{print 1, $1, $3}' > jji2
            # 3,4: A|B; 5,6: B|A
            stparcorse aapy1 | awk '{print 2, $3, $4}' >> jji2
            stparcorse aap1 | awk '{print 3, $3, $4}' >> jji2
            partial_correlation.py aapt1 | awk '{print 4, $1, $2}' >> jji2

            awk '{print $1, $2}' aa2 > tmp1; stpearcorse tmp1 | awk '{print 6, $1, $3}' >> jji2
            stparcorse aapy2 | awk '{print 7, $3, $4}' >> jji2
            stparcorse aap2 | awk '{print 8, $3, $4}' >> jji2
            partial_correlation.py aapt2 | awk '{print 9, $1, $2}' >> jji2

            awk '{print $1, $2}' aa3 > tmp1; stpearcorse tmp1 | awk '{print 11, $1, $3}' >> jji2
            stparcorse aapy3 | awk '{print 12, $3, $4}' >> jji2
            stparcorse aap3 | awk '{print 13, $3, $4}' >> jji2
            partial_correlation.py aapt3 | awk '{print 14, $1, $2}' >> jji2
        fi

        # with int rate change, with pyr rate change and both partial by pairing
        if [ $vint -eq 50 ]
        then
            # by pyr rate change
            awk '{print $1, $4}' aa1 > tmp1; stpearcorse tmp1 | awk '{print 1, $1, $3}' > jji3
            # pyr partial by pairing - 3 groups
            stparcorse aapy1 | awk '{print 2, $5, $6}' >> jji3
            stparcorse aapy2 | awk '{print 3, $5, $6}' >> jji3
            stparcorse aapy3 | awk '{print 4, $5, $6}' >> jji3


            # by int rate change
            awk '{print $1, $3}' aa1 > tmp1; stpearcorse tmp1 | awk '{print 6, $1, $3}' >> jji3
            # ubt partial by pairing - 3 groups
            stparcorse aap1 | awk '{print 7, $5, $6}' >> jji3
            stparcorse aap2 | awk '{print 8, $5, $6}' >> jji3
            stparcorse aap3 | awk '{print 9, $5, $6}' >> jji3

            break
        fi

done


grep -o "p=0.* B" parcor | grep -o "\-\?0\.[0-9]\{5\}" > parcor_p
grep -o "B: r=-\?0.* B" parcor | grep -o  "r=-\?0.* p" | grep -o "\-\?0\.[0-9]\{5\}" > parcor_r
awk '{print $1}' pearcor > acorints_r
awk '{print $2}' pearcor > acorints_p

