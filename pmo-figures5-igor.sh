#final tally

#pmo-allphil2


szth=1000
peath=2
cvth=3
# CHANGE FROM FAM1 TO FAM2
awk '{a=$8;b=$14;print (a-b)/(a+b)}' allcor5 >bb
awk '{a=$8;b=$14;print (a-b)}' allcor5 >bb1
# allfir5: 1/2 - pyr/int rate FAM1, 9/10 - pyr/int rate FAML, 13/14 - pyr/int rate FAM2
awk '{a=$2;b=$10;bb=$14;print (a-b)/(a+b),(a-bb)/(a+bb)}' allfir5 >aaint # rate change score of interneurons: from FAM1 to FAML and FAM2
awk '{a=$2;b=$10;bb=$6;print (a-b)/(a+b),(a-bb)/(a+bb)}' allfir5 >bbint  # rate chage score of interneurons: from FAM1 to FAML and NOV
awk '{a=$2;b=$10;bb=$12;print (a-b)/(a+b),(a-bb)/(a+bb)}' allfir5 >ccint #sleep before fam2

awk '{a=$1;b=$9;bb=$13;print (a-b)/(a+b),(a-bb)/(a+bb)}' allfir5 >aapyr
awk '{a=$1;b=$9;bb=$5;print (a-b)/(a+b),(a-bb)/(a+bb)}' allfir5 >bbpyr
awk '{a=$1;b=$9;bb=$11;print (a-b)/(a+b),(a-bb)/(a+bb)}' allfir5 >ccpyr 

awk '{a=$2;b=$10;bb=$6;bbb=$14;print (a-b)/(a+b),(a-bb)/(a+bb),(a-bbb)/(a+bbb)}' allfir5 >ccint

awk '{a=$1;b=$13;print $1,$13}' allszcor5 >cc
awk '{print $1,$2,$13,$14}' allzzcor5 >dd


awk '{a=$1;b=$5;print $1,$5}' allszcor5 >cco
awk '{print $1,$2,$5,$6}' allzzcor5 >ddo

awk '{a=$2;b=$10;aa=$1;bb=$9;print (a-b)/(a+b),(aa-bb)/(aa+bb)}' allpmszcor5 >ee
awk '{a=$2;b=$10;aa=$1;bb=$9;print (a-b),(aa-bb)}' allpmszcor5 >ee2
awk '{a=$2;b=$10;aa=$1;bb=$9;print (a-b)/(a+b),(aa-bb)/(aa+bb),(aa+a-bb-b)/(aa+a+bb+b)}' allpmszcor5 >ee3
# UPD: for different intervals
for vint in 2 5 10 20 50 100 200
do
	awk '{a=$2;b=$10;aa=$1;bb=$9; print (a+b<2)?0:(a-b)/(a+b),(aa+bb<2)?0:(aa-bb)/(aa+bb),(aa+a-bb-b)/(aa+a+bb+b)}' allpmszcor5.$vint >ee3.$vint
done
awk '{a=$1;aa=$9;b=$2;bb=$10;print a*b-aa*bb}' allfir5 >aapcoi
awk '{a=$1;aa=$9;b=$2;bb=$10;print (a*b-aa*bb)/(a*b+aa*bb)}' allfir5 >aapcoi1

# RELATIVE CHANGES: FAM1-FAML, FAM1-NOV
awk '{a=$8;b=$12;aa=$8;bb=$10;print (a-b)/(a+b),(aa-bb)/(aa+bb)}' allcor5 >ff

awk '{a=$8;b=$12;aa=$8;bb=$10;print (a-b),(aa-bb)}' allcor5 >ff1
awk '{a=$2;b=$10;aa=$1;bb=$9;print (a-b)/(a+b),(aa-bb)/(aa+bb)}' allszcor5 >ee1
awk '{a=$2;b=$10;bb=$14;print (a-b),(a-bb)}' allfir5 >aaint1
awk '{a=$2;b=$10;bb=$6;print (a-b),(a-bb)}' allfir5 >bbint1
# STPs in FAM2 FAM1 FAML NOV
awk '{print $14,$8,$12,$10}' allcor5 >gg

awk '{d=$10;if (d<0) d=-d;a=$14;if (a<0) a=-a; b=$8;if (b<0) b=-b;c=$12;if (c<0) c=-c;print log(a),log(b),log(c),log(d)}' allcor5 >ggl


paste  cc dd bb aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9}' >aa;stparcor aa

#szth=3000
#paste  cc dd bb aaint bbint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9,$11}' | regress -p



paste  cc dd bb ee | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8}' | regress

paste  cc dd bb ee | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9}' | regress

paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9}' >aa;stparcor aa

paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $7}' | desc
paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8<0) print $7}' | desc



paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9}' >aa;stparcor aa

paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$10}' >aa;stparcor aa

paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9,$10}' | regress -p

#here it starts <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# stpearcor: r,p,se,a,b,indno
# stpearcorse : mean + se
# aa: FAM2-FAM1-FAML
paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9}' >aa; 

colex 1 3 <aa > aaa; stpearcorse aaa | awk '{print 2,$1,$3}' >jjres # FAM2-FAML, 2C-2
# 2D-1, 2D-2
stparcor aa

stparcorse aa | awk '{print 4,$1,$2}' >>jjres

stparcorse aa | awk '{print 3,$3,$4}' >jjres1 # was 5/jjres
stparcorse aa | awk '{print 4,$5,$6}' >>jjres1 # was 6/jjres

paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$10}' >aa; 
colex 1 2 <aa > aaa; stpearcorse aaa | awk '{print 1,$1,$3}' >>jjres # FAM2-FAM1, 2C-1 (same as above!) # WAS jjres1 / 1
colex 1 3 <aa > aaa; stpearcorse aaa | awk '{print 3,$1,$3}' >>jjres # FAM2-NOV, 2C-3 					# AWS jjres1 / 2
# 2D-3, 2D-4
stparcor aa
#stparcorse aa | awk '{print 4,$1,$2}' >jjres1 # before
stparcorse aa | awk '{print 5,$3,$4}' >>jjres1
stparcorse aa | awk '{print 6,$5,$6}' >>jjres1


# 2C: ANOVA (INSTEAD OF LOO)
paste  cc dd  gg bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9,$10,$11}' >tpa;
R
library(nlme)
a<-scan("tpa",list(f2=0,f1=0,fl=0,n=0,an=""))
#nmlz <- function(x) {(1+x)^0.5} # 0.25 is invalid; (1+x)^0.25 or (1+x)^0.25 doesn't normalize
a$an <- factor(a$an)
#a$f2<-nmlz(a$f2)
#a$f1<-nmlz(a$f1)
#a$fl<-nmlz(a$fl)
#a$n<-nmlz(a$n)
#shapiro.test(a$f2) # normal like this
attach(a)
fit1f<-lm(f2 ~ f1)
fitlf<-lm(f2 ~ fl)
fitnf<-lm(f2 ~ n)
fit1<-lme(f2 ~ f1, random=~1|an, method="REML")
fitl<-lme(f2 ~ fl, random=~1|an, method="REML")
fitn<-lme(f2 ~ n, random=~1|an, method="REML")
anova(fit1)
anova(fitl)
anova(fitn)
print("=====================[ ANIMAL ]=================")
anova(fit1, fit1f)
anova(fitl, fitlf)
anova(fitn, fitnf)
q()
n

# LEAVE-ONE-OUT
echo "LEAVE-ONE-OUT ANALYSIS:"
for nm in mjc71 mjc142  mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
# FAM2, FAM1, FAML ?
paste  cc dd  gg bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($11!="'$nm'") print $7,$8,$9}' >aalo;
# aa: FAM2, FAM1, NOV
paste  cc dd  gg bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($11!="'$nm'") print $7,$8,$10}' >aalon;
colex 1 2 <aalo > aaa; stpearcor aaa # FAM2-FAM1, 2C-1
colex 1 3 <aalo > aaa; stpearcor aaa # FAM2-FAML, 2C-2
colex 1 3 <aalon > aaa; stpearcor aaa # FAM2-NOV, 2C-3
# 2D all
stparcor aalo
stparcor aalon
done


# 2D: Try ANOVA model comparisons instead of partial correlations: to see effect of the animal as well!
paste  cc dd  gg bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9,$10,$11}' >anov2d; # had if != nm!!! before
R
a<-scan("anov2d",list(f2=0,f1=0,fl=0,n=0,an=""))
normalize <- function(x) {x^0.25}
a$an <- factor(a$an)
#a$f2<-a$f2^0.25 	# for normality
#a$f2<-normalize(a$f2) 	# for normality
#a$f1<-normalize(a$f1) 	# for normality
#a$fl<-normalize(a$fl) 	# for normality
#a$n<-normalize(a$n) 	# for normality
#shapiro.test(a$f2)
attach(a)
library(nlme)
fit<-lme(f2 ~ f1 + fl, random=~1|an, method="REML")
fit_ml<-lme(f2 ~ f1 + fl, random=~1|an, method="ML")
fitf<-lm(f2 ~ f1 + fl)
# FAM1 | FAML and FAML | FAM1
fitl<-lme(f2 ~ fl, random=~1|an, method="REML")
fit1<-lme(f2 ~ f1, random=~1|an, method="REML")
fitl_ml<-lme(f2 ~ fl, random=~1|an, method="ML")
fit1_ml<-lme(f2 ~ f1, random=~1|an, method="ML")
fitlf<-lm(f2 ~ fl)
fit1f<-lm(f2 ~ f1)
#summary(fit)
print('===================PARTIALS===============')
#anova(fit)
anova(fitl_ml,fit_ml)
anova(fit1_ml,fit_ml)
print('==================ANIMAL===============')
#anova(fit, fitf)
anova(fit1, fit1f)
anova(fitl, fitlf)
# FAM1 | NOV and NOV | FAM1
fit<-lme(f2 ~ f1 + n, random=~1|an, method="REML")
fitn<-lme(f2 ~ n, random=~1|an, method="REML")
fit_ml<-lme(f2 ~ f1 + n, random=~1|an, method="ML")
fitn_ml<-lme(f2 ~ n, random=~1|an, method="ML")
fitf<-lm(f2 ~ f1 + n)
fitnf<-lm(f2 ~ n)
#summary(fit)
print('===================PARTIALS===============')
anova(fit)
anova(fitn_ml,fit_ml)
anova(fit1_ml,fit_ml)
print('===================[ ANIMAL ]===============')
anova(fitn,fitnf)
q()
n



#R calclulations
paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9,$10}' >aa
#or in R
R
a<-scan("aa",list(y=0,x1=0,x2=0,x3=0))
attach(a)
fit<-lm(y ~ x1 + x2 + x3)
summary(fit)
q()
n


# Igor : 2F - is correlation significant? ; THIS IS NOT RELATIVE CHANGE !!
paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7-$8,$9-$8}' >aicor
stpearcor aicor
# OR LOO
for nm in mjc71 mjc142 mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
paste  cc dd  gg bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($11!="'$nm'") print $7-$8,$9-$8}' >aicorloo
stpearcor aicorloo
done





# ??? WHERE DOES THIS COME FROM - VALIDATE ! - 2nd plot in jj1, not used
echo  "0.018109   0.005081   3.564 0.000731
    0.349580   0.100528   3.477 0.000957
   0.584969   0.146198   4.001 0.000178 
   -0.212386   0.135341  -1.569 0.121936    " | awk '{print NR,$0}' >jjres2

# 2F - compare FAM2 VS. FAM1 FOR THOSE WHICH GAINED / LOST TRANMISSION IN FAML COMPARED TO FAM1
paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($8-$9)>0) print $7,$8}' | rankrel
paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($8-$9)<0) print $7,$8}' | rankrel
# LOO
for nm in mjc71 mjc142 mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($8-$9)>0 && ($11!="'$nm'")) print $7,$8}' | rankrel
paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($8-$9)<0 && ($11!="'$nm'")) print $7,$8}' | rankrel
done

# PROPER (2F) ANOVA : FAM1L IS SIGNIFICANT, ANIMAL IS NOT
paste  cc dd bb ff bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$10}' >aator
R
library(nlme)
dtp3<-scan('aator',list(fam12=0,fam1l=0,an=""))
#nmlz <- function(x) {x^0.25}
dtp3$an<-factor(dtp3$an)
#dtp3$fam12<-nmlz(dtp3$fam12)
#dtp3$fam1l<-nmlz(dtp3$fam1l)
#shapiro.test(dtp3$fam12)
attach(dtp3)
#fit<-lm(fam12~fam1l+an)
fit<-lme(fam12~fam1l, random=~1|an)
fit_noan<-lm(fam12~fam1l)
anova(fit)
anova(fit, fit_noan)
q()
n

# [DON'T USE THIS - USE ONE BELOW]-- ANOVA ANALYSIS - DIFFERENCE IN TPS WITH SESSION(FAM1/FAM2) AND ANIMAL AS FACTORS
paste  cc dd  gg bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($8-$9)>0) {print $7,1,$11; print $8,2,$11}}' > anv2fp
paste  cc dd  gg bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($8-$9)<0) {print $7,1,$11; print $8,2,$11}}' > anv2fn
R
library(nlme)
a<-scan("anv2fp",list(tp=0,ses="",an=""))
a$ses<-factor(a$ses)
a$an<-factor(a$an)
attach(a)
#fit<-lm(tp ~ ses + an)
fit<-lme(tp ~ ses, random=~1|an)
fit_noan<-lm(tp ~ ses)
summary(fit)
anova(fit)
anova(fit, fit_noan)
q()
n
# -- ANOVA ANALYSIS - PREDICTING FAM2 USING FAM1 AND ANIMAL
paste  cc dd  gg bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($8-$9)>0) print $8,$7,$11}' > anv2fcorp
paste  cc dd  gg bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($8-$9)<0) print $8,$7,$11}' > anv2fcorn
R
a<-scan("anv2fcorp",list(fam2=0,fam1=0,an=""))
a$an<-factor(a$an)
attach(a)
fit<-lm(fam2 ~ fam1 + an)
summary(fit)
anova(fit)
q()
n


# USED IN 2E - 2F
paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($8-$9)>0) print $8,$7}' >aa1
paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($8-$9)<0) print $8,$7}' >aa2

# plotted in jj1 end: (FAML-FAM1, FAM2-FAM1)
paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print -$8,-$7}' >aa3


# 2B - 3 bars;  	ABSOLUTE VALUE ?!
paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $7;else print -$7}' | stats mean se  | awk '{print 1,$1,$2}' >jjfn
paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($9>0) print $9;else print -$9}' | stats mean se  | awk '{print 2,$1,$2}' >>jjfn
paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $8;else print -$8}' | stats mean se   | awk '{print 3,$1,$2}' >>jjfn
# 2B - see significance (prob - t / prob / F) - may be see original data for which test was used
paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $7;else print -$7}' | desc
paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($9>0) print $9;else print -$9}' | desc
paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $8;else print -$8}' | desc
# ANOVA (ALT TO LEAVE ONE OUT)
paste  cc dd bb ff bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $7, $10; else print -$7, $10}' > rel_fam2
paste  cc dd bb ff bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $8, $10; else print -$8, $10}' > rel_faml
paste  cc dd bb ff bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($9>0) print $9, $10; else print -$9, $10}' > rel_nov
R
library(nlme)
a<-scan("rel_fam2",list(score=0,an="")) 					# ANIMAL SIG HERE WITH ANOVA !
#a<-scan("rel_faml",list(score=0,an=""))
#a<-scan("rel_nov",list(score=0,an=""))
a$an<-factor(a$an)
attach(a)
#fit<-lme(score ~ 1, random=~1|an, method="REML")
fit<-lm(score ~ an)
fit_noan<-gls(score ~ 1, method="REML")
#fit_noan<-lm(score ~ 1)
#summary(fit)
anova(fit)
#anova(fit, fit_noan)
q()
n


# LOO on these (2B) << TO BE USED IN THE PAPER, NOT THE ANOVA !!! (because no regression was used here)
for nm in mjc71 mjc142  mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
paste  cc dd bb ff bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0 && $10!="'$nm'") print $7;else if ($7<0 && $10!="'$nm'") print -$7}' | desc | tail -2
paste  cc dd bb ff bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($9>0 && $10!="'$nm'") print $9;else if ($9<0 && $10!="'$nm'") print -$9}' | desc | tail -2
paste  cc dd bb ff bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0 && $10!="'$nm'") print $8;else if ($8<0 && $10!="'$nm'")print -$8}' | desc | tail -2
done

# NEW : 2B-1st // copied from pmo-figures-igor.sh
paste  cc dd bb | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $7;else print -$7}' > fam1tofam2
#awk '{a=$1;b=$2;c1=(a-b)/(a+b);if (c1<0) c1=-c1;print c1}' allfscor2 >fam1h1toh2
# same - prevent 0 division + filter; use 1 of the two - halves or odd/even
paste cc dd allfscor5  | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){a=$7;b=$8;if (a+b!=0) c1=(a-b)/(a+b); else c1=0;if (c1<0) c1=-c1;print c1}' >fam1h1toh2
# FROM BELOW FOR CMP:								      	       	       awk '{a=$1;b=$2;aa=$2;bb=$14;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;if(aa+bb!=0)c2=(aa-bb)/(aa+bb);else c2=0;if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs
paste cc dd allfs1cor5 | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){a=$7;b=$8;if (a+b!=0) c1=(a-b)/(a+b); else c1=0;if (c1<0) c1=-c1;print c1}' >fam1otoe
# what to these tests mean? significance of difference > 0 ?
paste fam1tofam2 fam1h1toh2 | pair
paste fam1tofam2 fam1otoe | pair
paste fam1tofam2 fam1otoe | rankrel
# better compre using t-test or wilcoxon
# TRANSFORM TO APPLY T-TEST - none of sqrt, log, exp make it normal!
R
famh<-scan('fam1h1toh2')
famoe<-scan('fam1otoe')
fam12<-scan('fam1tofam2')
wilcox.test(famh,fam12)
wilcox.test(famoe,fam12)
t.test(famh,fam12)
t.test(famoe,fam12)
shapiro.test(fam12)
shapiro.test(famh)
shapiro.test(famoe)
q()
n

# LOO 2B-control ODD-EVEN
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> THIS SEEMED TO HAVE WORKED ON OLD DATABASE (PHILIPP ONLY), BUT NOW IS FAILING WITH LOO-JC218 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
for nm in mjc71 mjc142  mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
paste  cc dd bb bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($7>0)&&($8!="'$nm'")) print $7;else if ($8!="'$nm'") print -$7}' > fam1tofam2
paste cc dd bbname allfs1cor5| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){a=$8;b=$9;if (a+b!=0) c1=(a-b)/(a+b); else c1=0;if (c1<0) c1=-c1;if($7!="'$nm'")print c1}' >fam1otoe
# IS DIFFERENCE >0 ? - doesn't work
# paste fam1tofam2 fam1otoe | pairi
# WILCOXON TEST
Rscript wilcoxon_oddeven_vs_fam12.R
done

# ANOVA test for comparing ODD-TO-EVEN vs. FAM1-TO-FAM2
paste  cc dd bb bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $7,$8,1;else print -$7,$8,1}' > dstpcon
#paste cc dd bbname allfscor5  | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){a=$8;b=$9;if (a+b!=0) c1=(a-b)/(a+b); else c1=0;if (c1<0) c1=-c1;print c1,$7,2}' >>dstpcon
paste cc dd bbname allfs1cor5| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){a=$8;b=$9;if (a+b!=0) c1=(a-b)/(a+b); else c1=0;if (c1<0) c1=-c1;print c1,$7,2}' >> dstpcon
# try without jc218
#paste  cc dd bb bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0&&$8!="jc218") print $7,$8,1;else if ($8!="jc218") print -$7,$8,1}' > dstpcon
#paste cc dd bbname allfs1cor5| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){a=$8;b=$9;if (a+b!=0) c1=(a-b)/(a+b); else c1=0;if (c1<0) c1=-c1;if ($7!="jc218")print c1,$7,2}' >> dstpcon
R
dstp<-scan('dstpcon', list(d=0, an="", tp=0))
shapiro.test(dstp$d) # sqrt better; sqrt sqrt works!
dstp$d<-dstp$d^0.25
#dstp$d<-asin(dstp$d)^0.25 # this gives best normality after outlier is removed
shapiro.test(dstp$d) # sqrt better; sqrt sqrt works!
dstp$an<-factor(dstp$an)
dstp$tp<-factor(dstp$tp)
attach(dstp)
fit<-lm(d~an*tp)
anova(fit)
#summary(fit)
q()
n





gnuplot
set term post color 12
set outp "jj1.ps"
unset key
set tics nomirror
unset xtics
set multiplot layout 3,2
set boxw .5
set ytics 0,0.2,0.4
set xzeroax
plot [0:5][0:0.5] 'jjfn' w boxerr lc 0
set ytics -0.2,0.2,0.6
plot [0:5][-0.4:0.8] 'jjres2' u 1:2:3 w boxerr lc 0
set ytics -0.4,0.4,0.8
plot [0:7][-0.4:1] 'jjres' w boxerr lc 0
plot [0:7] [-0.4:1]'jjres1' w boxerr lc 0
set logs
set xtics
set ytics auto
set tics nomirror
plot [0.001:1][0.001:1] 'aa1' w po pt 5 lc 6 ps .5,'aa2' w po pt 9 lc 7,x w li lc 0
set zeroaxis
unset logs
set ytics -1.0,0.2,0.75
set yrange [-1.0:0.75] # -0.5:0.75 OK
#plot [-.9:0.8]'aa3' w po pt 5 lc 0,0.4516*x+0.0613244 w li lc 0 # OLD LINE ?
plot [-.9:0.8]'aa3' w po pt 5 lc 0, 0.5989*x+0.0846806 w li lc 0
#plot [-1.0:1.0]'aa3' w po pt 5 lc 0, 0.5989*x+0.0846806 w li lc 0 # WHOLE RANGE FOR TEST
quit
gv jj1.ps


# gg: FAM2 FAM1 FAML NOV: (FAM2-FAM1)/(FAM2+FAM1) for FAM1-FAML > 0, <0
paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($8-$9)>0) print ($7-$8)/($7+$8)}' >aao1
paste  cc dd  gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($8-$9)<0) print ($7-$8)/($7+$8)}' >aao2
echo 1 `colex 1 <aao1 | stats mean` >aaom
echo 2 `colex 1 <aao2 | stats mean` >>aaom
echo 1 `stnpercentile aao1 .5` >aaome1
echo 2 `stpercentile aao2 .5` >aaome2
awk '{print 1,$1}' aao1 >aaom1
awk '{print 2,$1}' aao2 >aaom2


# FIG 2F INSERT
gnuplot
set term post color 12
set outp "jj1a.ps"
set multiplot layout 3,4
unset key
set tics nomirror
set xzeroaxis
unset xtics
plot [0:3] 'aaom1' w poi lc 6 ps .6 pt 6,'aaom2' w poi lc 7 ps .6 pt 6,'aaome1' w poi lc 6 ps 3 pt 1,'aaome2' w poi lc 7 ps 3 pt 1
quit
gv jj1a.ps

# 3A
paste  cc dd bb aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9}' >aa;stparcor aa
# For Figure 3 / jj2.ps
colex 1 2 <aa > aaa; stpearcorse aaa | awk '{print 1,$1,$3}' >jjres
colex 1 3 <aa > aaa; stpearcorse aaa | awk '{print 2,$1,$3}' >>jjres
colex 1 2 <aa > aaa; stpearcor aaa
colex 1 3 <aa > aaa; stpearcor aaa
# LOO on these
for nm in mjc71 mjc142  mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
paste  cc dd bb aaint bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($10!="'$nm'") print $7,$8,$9}' >aalo;stparcor aalo
colex 1 2 <aalo > aaa; stpearcor aaa
colex 1 3 <aalo > aaa; stpearcor aaa
done
# ANOVA (alt to LOO)
paste  cc dd bb aaint bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9,$10}' > tpscore_rates_an
R
library(nlme)
a<-scan("tpscore_rates_an",list(dtp=0,rcl=0,rcf2=0,an=""))
a$an<-factor(a$an)
#nmlz <- function(x) {sign(x)*abs(x)^0.25}
#rnmlz <- function(x) {sign(x)*log(1+x)^0.5}
#a$dtp<-nmlz(a$dtp)
#a$rcl<-rnmlz(a$rcl)
#a$rcf2<-a$rcf2^0.125
#a$rcf2<-nmlz(a$rcf2)
#shapiro.test(a$dtp)
attach(a)
fitl<-lme(dtp ~ rcl, random=~1|an)
fitl_ml<-lme(dtp ~ rcl, random=~1|an, method="ML")
fitl_f<-lm(dtp ~ rcl)
anova(fitl)
fitf2<-lme(dtp ~ rcf2, random=~1|an)
fitf2_ml<-lme(dtp ~ rcf2, random=~1|an, method="ML")
fitf2_f<-lm(dtp ~ rcf2)
anova(fitf2)
fitlf2<-lme(dtp ~ rcl + rcf2, random=~1|an)
fitlf2_ml<-lme(dtp ~ rcl + rcf2, random=~1|an, method="ML")
fitlf2_f<-lm(dtp ~ rcl + rcf2)
# ANOVA max model:
anova(fitlf2)
# 3A-3, 3A-4 : instead of partial correlations - compare models
print("====================================================================[ PARTIALS ]=====================================================================")
anova(fitf2_ml, fitlf2_ml)
anova(fitl_ml,  fitlf2_ml)
print("====================================================================[ ANIMAL ]=====================================================================")
anova(fitlf2, fitlf2_f)
anova(fitf2, fitf2_f)
anova(fitl, fitl_f)
# compare models without animal variable (3A-3)
#fitf2<-lm(dtp ~ rcf2)
#fitlf2<-lm(dtp ~ rcl + rcf2)
#anova(fitf2, fitlf2)
q()
n


# for Figure 3 / jj2.ps
stparcorse aa | awk '{print 4,$1,$2}' >>jjres
stparcorse aa | awk '{print 5,$3,$4}' >>jjres
stparcorse aa | awk '{print 6,$5,$6}' >>jjres

# 3B-3 and 3B-4
paste  cc dd bb aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9}' >aa;stparcor aa
colex 1 2 <aa > aaa; stpearcorse aaa | awk '{print 1,$1,$3}' >jjres1 		
colex 1 3 <aa > aaa; stpearcorse aaa | awk '{print 2,$1,$3}' >>jjres1
colex 1 2 <aa > aaa; stpearcor aaa 	# 3B-1
colex 1 3 <aa > aaa; stpearcor aaa 	# 3B-2
# LOO on these
for nm in mjc71 mjc142  mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
paste  cc dd bb aapyr bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($10!="'$nm'") print $7,$8,$9}' >aalo;stparcor aalo
colex 1 2 <aalo > aaa; stpearcor aaa
colex 1 3 <aalo > aaa; stpearcor aaa
done
# ANOVA 
paste  cc dd bb aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$10}' >anv3b
R
a<-scan("anv3b",list(dtp=0,drfam2=0,an=""))
a$an<-factor(a$an)
attach(a)
fit<-lm(dtp ~ drfam2 + an)
summary(fit)
anova(fit)
q()
n
# ANOVA for 3B : model comparison + animal variable
paste  cc dd bb aapyr bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9,$10}' > tpscore_pyr_an
R
library(nlme)
a<-scan("tpscore_pyr_an",list(dtp=0,drl=0,drf2=0,an=""))
a$an<-factor(a$an)
#nmlz <- function(x) {sign(x)*abs(x)^0.25}
#shapiro.test(a$dtp)
#a$dtp<-nmlz(a$dtp)
#a$dtp<-sign(a$dtp)*abs(a$dtp)^0.8 # this gives best normalization result
#shapiro.test(a$dtp)
attach(a)
fit2<-lme(dtp ~ drf2, random=~1|an)
fitl<-lme(dtp ~ drl, random=~1|an)
fitboth<-lme(dtp ~ drf2 + drl, random=~1|an)
fit2_f<-lm(dtp ~ drf2)
fitl_f<-lm(dtp ~ drl)
fitboth_f<-lm(dtp ~ drf2 + drl)
fit2_ml<-lme(dtp ~ drf2, random=~1|an, method="ML")
fitl_ml<-lme(dtp ~ drl, random=~1|an, method="ML")
fitboth_ml<-lme(dtp ~ drf2 + drl, random=~1|an, method="ML")
#fit2<-lm(dtp ~ drf2 + an)
#fitl<-lm(dtp ~ drl + an)
#fitboth<-lm(dtp ~ drf2 + drl + an)
anova(fit2)
anova(fitl)
print("=========================[ ANIMAL ]=========================")
anova(fit2, fit2_f)
anova(fitl, fitl_f)
print("=========================[ PARTIALS ]=========================")
anova(fit2_ml, fitboth_ml)
anova(fit2, fitboth)
anova(fitl_ml, fitboth_ml)
q()
n


# For Figure 3 / jj2.ps
stparcorse aa | awk '{print 4,$1,$2}' >>jjres1
stparcorse aa | awk '{print 5,$3,$4}' >>jjres1
stparcorse aa | awk '{print 6,$5,$6}' >>jjres1


paste  cc dd bb aaint aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9,$10,$11}' | regress -p

paste  cc dd bb aaint aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9,$10,$11}' >aa

#or in R
R
a<-scan("aa",list(y=0,x1=0,x2=0,x3=0,x4=0))
attach(a)
fit<-lm(y ~ x1 + x2 + x3 + x4)
summary(fit)
q()
n

paste  cc dd bb aaint aapyr bbint bbpyr| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9,$10,$11,$13,$15}' >aaa

#sleep before fam2 exploration
#paste  cc dd bb aaint aapyr ccint ccpyr| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9,$10,$11,$13,$15}' >aaa
#or in R
R
a<-scan("aaa",list(y=0,x1=0,x2=0,x3=0,x4=0,x5=0,x6=0))
attach(a)
fit<-lm(y ~ x1 + x2 + x3 + x4 + x5 +x6)
summary(fit)
q()
n


echo  "-0.01867    0.02746  -0.680   0.4993    
     0.28229    0.12135   2.326   0.0235 
     0.89039    0.17408   5.115  3.7e-06 
       0.23613    0.10557   2.237   0.0292  
      -0.01419    0.10042  -0.141   0.8881  " | awk '{print NR,$0}' >jjres2

# 3C
paste  cc dd  gg aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($11>0) print $7,$8}' | rankrel
paste  cc dd  gg aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($11<0) print $7,$8}'  | rankrel
# LOO 3C
echo "LEAVE-ONE-OU ANALYSIS:"
for nm in mjc71 mjc142  mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
echo "POSITIVE"
paste  cc dd  gg aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($11>0)&&($13!="'$nm'")) print $7,$8}' | rankrel
echo "NEGATIVE"
paste  cc dd  gg aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($11<0)&&($13!="'$nm'")) print $7,$8}'  | rankrel
done



# LOO 3D
echo "LEAVE-ONE-OU ANALYSIS:"
for nm in mjc71 mjc142  mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
echo "POSITIVE"
paste  cc dd  gg aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($11>0)&&($13!="'$nm'")) print $7,$8}' | rankrel
echo "NEGATIVE"
paste  cc dd  gg aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if (($11<0)&&($13!="'$nm'")) print $7,$8}'  | rankrel
done



paste  cc dd  gg aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($11>0) print $7,$8}' >aa1
paste  cc dd  gg aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($11<0) print $7,$8}' >aa2

# INT RATE CHANGE VS. FAM2-FAM1
paste  cc dd bb aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print -$8,-$7}' >aa3

# PYR RATE CHANGE VS. FAM2-FAM1
paste  cc dd bb aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print -$8,-$7}' >bb3


paste  cc dd bb aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print -$8,-$9}' >bb4

paste  cc dd bb aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print -$8,-$9}' >aa4


paste  cc dd bb aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print -$8,-$9}' >bb4

gnuplot
set term post color 12
set outp "jj2.ps"
set multiplot layout 3,2
set zeroaxis
unset key
set tics nomirror
set ytics -0.6,0.2,0.8
set xtics -0.8,0.2,0.8
plot [-.7:.4][-.3:0.4] 'aa4'  w po pt 5 lc 0
set ytics -0.4,0.4,0.8
set xtics -0.8,0.4,0.8
plot [-0.9:0.9][-0.7:0.9]'bb4'  w po pt 5 lc 0 ,0.7539*x+0.0433818 w li lc 0
set boxw .5
unset xtics
set ytics 0,0.4,0.8
plot [0:7][0:0.8] 'jjres' w boxerr lc 0
plot [0:7] [0:0.8]'jjres1' w boxerr lc 0
#plot [0:7] [-.2:1.1]'jjres2' u 1:2:3  w boxerr lc 0
set xtics
set ytics -0.4,0.2,0.6
#set yrange [-0.4:0.8]
set yrange [-1.0:1.0]
set xtics -.6,.2,0.4
#set xrange [-.7:0.4]
set xrange [-1.0:1.0]
plot 'aa3' w po pt 5 lc 0,0.6941*x+0.106423 w li lc 0
#plot [0:7] [-.2:1.1]'jjres2' u 1:2:3  w boxerr lc 0
set ytics -0.4,0.4,0.8
#set yrange [-0.5:0.8]
set yrange [-1.0:1.0]
set xtics -.8,.4,0.8
#set xrange [-.9:0.9]
set xrange [-1.0:1.0]
plot 'bb3' w po pt 5 lc 0,0.3192*x+-0.00762829 w li lc 0
quit

gv jj2.ps


# INSERTS - Figure 3
#paste  cc dd bb aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ if($8>0) print -$7}' >aa3_1
#paste  cc dd bb aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ if($8<0) print -$7}' >aa3_2
paste  cc dd bb aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ if($8>0) print -$7}' >aa3_1
paste  cc dd bb aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ if($8<0) print -$7}' >aa3_2
echo 1 `stpercentile aa3_1 .5` >aa3me_1
echo 2 `stpercentile aa3_2 .5` >aa3me_2
awk '{print 1,$1}' aa3_1 >aa3m_1
awk '{print 2,$1}' aa3_2 >aa3m_2

gnuplot
set term post color 12
set outp "jj2_i1.ps"
set multiplot layout 3,4
unset key
set tics nomirror
set xzeroaxis
unset xtics
plot [0:3] 'aa3m_1' w poi lc 6 ps .6 pt 6,'aa3m_2' w poi lc 7 ps .6 pt 6,'aa3me_1' w poi lc 6 ps 3 pt 1,'aa3me_2' w poi lc 7 ps 3 pt 1
quit
gv jj2_i1.ps



#alternative


awk '{a=$2;b=$10;bb=$14;c=$6;print a,b,bb,c}' allfir5 >aainto
paste  cc dd aainto | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>$8) print $7,$9}' >aa1o
paste  cc dd aainto | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7<$8) print $7,$9}' >aa2o
awk '{a=$1;b=$9;bb=$13;c=$5;print a,b,bb,c}' allfir5 >aapyro
paste  cc dd aapyro | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>$8) print $7,$9}' >bb1o
paste  cc dd aapyro | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7<$8) print $7,$9}' >bb2o

gnuplot
set term post color 12
set outp "jj2.ps"
set multiplot layout 3,2
set zeroaxis
unset key
set tics nomirror
set ytics 0,20,40
set xtics 0,20,40
plot [0:50][0:50] 'aa1o' w po pt 5 lc 6 ps .5,'aa2o' w po pt 9 lc 7,x w li lc 0
set ytics 0,2,4
set xtics 0,2,4
plot [0:5][0:5] 'bb1o' w po pt 5 lc 6 ps .5,'bb2o' w po pt 9 lc 7,x w li lc 0
set boxw .5
unset xtics
set ytics 0,0.4,0.8
plot [0:7][0:0.8] 'jjres' w boxerr lc 0
plot [0:7] [0:0.8]'jjres1' w boxerr lc 0
#plot [0:7] [-.2:1.1]'jjres2' u 1:2:3  w boxerr lc 0
set xtics
set ytics -0.4,0.2,0.6
set yrange [-0.4:0.8]
set xtics -.6,.2,0.4
set xrange [-.7:0.4]
plot 'aa3' w po pt 5 lc 0,0.3574*x+0.0453044 w li lc 0
#plot [0:7] [-.2:1.1]'jjres2' u 1:2:3  w boxerr lc 0
set ytics -0.4,0.4,0.8
set yrange [-0.5:0.8]
set xtics -.8,.4,0.8
set xrange [-.9:0.9]
plot 'bb3' w po pt 5 lc 0,0.22*x+0.01 w li lc 0
quit

gv jj2.ps



# Figure 1C, 1D
# cc dd bb : 7 cols
awk '{a=$1;b=$9;bb=$13;c=$5;print a,b,bb,c}' allfir5 >aapyro # pyr rates in: FAM1, FAML, FAM2, ?
paste  cc dd bb aapyro | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){  print $8,$11}' >bb3o
paste  cc dd bb aapyro | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $8,$10}' >bb2o
paste  cc dd bb aapyro | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){  print $8,$9}' >bb1o # FAM1/FAML
awk '{a=$2;b=$10;bb=$14;c=$6;print a,b,bb,c}' allfir5 >aainto
paste  cc dd bb aainto | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){  print $8,$11}' >aa3o
paste  cc dd bb aainto | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){  print $8,$10}' >aa2o
paste  cc dd bb aainto | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $8,$9}' >aa1o # FAM1/FAML

paste  cc dd gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){  print $8,$9}' >aa4o
paste  cc dd gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){  print $8,$7}' >aa5o
paste  cc dd gg | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){  print $8,$10}' >aa6o

gnuplot
set term post color 12
set outp "jj2a.ps"
set multiplot layout 3,3
set size ratio 1
set zeroaxis
unset key
set tics nomirror
set ytics 0,20,40
set xtics 0,20,40
plot [0:50][0:50] 'aa1o' w po pt 5 lc 0 ps .5,x w li lc 0
set ytics 0,2,4
set xtics 0,2,4
plot [0:5][0:5] 'bb1o' w po pt 5 lc 0 ps .5,x w li lc 0
set logs
set xtics auto
set ytics auto
set tics nomirror
plot [0.001:1][0.001:1] 'aa4o' w po pt 5 lc 0 ps .5,x w li lc 0
unset log
set tics nomirror
set ytics 0,20,40
set xtics 0,20,40
plot [0:50][0:50] 'aa2o' w po pt 5 lc 0 ps .5,x w li lc 0
set ytics 0,2,4
set xtics 0,2,4
plot [0:5][0:5] 'bb2o' w po pt 5 lc 0 ps .5,x w li lc 0
set logs
set xtics auto
set ytics auto
set tics nomirror
plot [0.001:1][0.001:1] 'aa5o' w po pt 5 lc 0 ps .5,x w li lc 0
unset log
set tics nomirror
set ytics 0,20,40
set xtics 0,20,40
plot [0:50][0:50] 'aa3o' w po pt 5 lc 0 ps .5,x w li lc 0
set ytics 0,2,4
set xtics 0,2,4
plot [0:5][0:5] 'bb3o' w po pt 5 lc 0 ps .5,x w li lc 0
set logs
set xtics auto
set ytics auto
set tics nomirror
plot [0.001:1][0.001:1] 'aa6o' w po pt 5 lc 0 ps .5,x w li lc 0
unset log
quit

gv jj2a.ps


# last review round
R
library(nlme)
a<-scan("bb1ou",list(r1=0,rl=0))
#a$inte<-factor(a$inte)
attach(a)
fit<-lm( ~ dri, random=~1|an)
q()
n



# (was absent in original) RE-RUN to be sure not overritten in-between
paste  cc dd bb aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print -$8,-$7}' >aa3

paste  cc dd bb aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print -$8,-$7}' >bb3

paste aa3 bb3 | awk '($1<0&&$3<0){print $2}' | desc


paste aa3 bb3 | awk '($1<0&&$3>0){print $2}' | desc

paste aa3 bb3 | awk '($1<0&&$3<0){print $2,0}' | rankrel
paste aa3 bb3 | awk '($1<0&&$3>0){print $2,0}' | rankrel

paste aa3 bb3 | awk '($1>0&&$3<0){print $2}' | desc


paste aa3 bb3 | awk '($1>0&&$3>0){print $2}' | desc

paste aa3 bb3 | awk '($1>0&&$3<0){print $2,0}' | rankrel
paste aa3 bb3 | awk '($1>0&&$3>0){print $2,0}' | rankrel


paste aa3 bb3 | awk '($1<0&&$3>0){print $1*$3,$2}'  >jjaa
paste aa3 bb3 | awk '($1<0&&$3<0){print $1*$3,$2}'  >jjbb
paste aa3 bb3 | awk '($1>0&&$3<0){print $1*$3,$2}'  >jjcc
paste aa3 bb3 | awk '($1>0&&$3>0){print $1*$3,$2}'  >jjdd

paste aa3 bb3 | awk '($1<0&&$3>0){print $2}' | desc -h -m -.4 -M 0.8 -i .1 | tail -n +2 | colex 1 2 >jja
paste aa3 bb3 | awk '($1<0&&$3<0){print $2}' | desc -h -m -.4 -M 0.8 -i .1 | tail -n +2 | colex 1 2 >jjb
paste aa3 bb3 | awk '($1>0&&$3<0){print $2}' | desc -h -m -.4 -M 0.8 -i .1 | tail -n +2 | colex 1 2 >jjc
paste aa3 bb3 | awk '($1>0&&$3>0){print $2}' | desc -h -m -.4 -M 0.8 -i .1 | tail -n +2 | colex 1 2 >jjd


paste aa3 bb3 | awk '($1<0&&$3<0){print $2,"in","pn"}' >aa
paste aa3 bb3 | awk '($1<0&&$3>0){print $2,"in","pp"}' >>aa
paste aa3 bb3 | awk '($1>0&&$3<0){print $2,"ip","pn"}' >>aa
paste aa3 bb3 | awk '($1>0&&$3>0){print $2,"ip","pp"}' >>aa

R
a<-scan("aa",list(x=0,inte="",py=""))
a$inte<-factor(a$inte)
a$py<-factor(a$py)
attach(a)
model<-aov(x~inte*py)
summary(model)
TukeyHSD(model)
q()



paste  cc dd bb ee | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8}' >aa
colex 1 2 <aa > aaa3; stpearcorse aaa3 | awk '{print 1,$1,$3}' >jjres1


paste  cc dd bb ee | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9}' >aa
colex 1 2 <aa > aaa4; stpearcorse aaa4 | awk '{print 2,$1,$3}' >>jjres1


paste  cc dd bb aapyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9}' >aa;stparcor aa
colex 1 2 <aa > aaa1; stpearcorse aaa1 | awk '{print 4,$1,$3}' >>jjres1
paste  cc dd bb aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$9}' >aa;stparcor aa
colex 1 2 <aa > aaa2; stpearcorse aaa2 | awk '{print 5,$1,$3}' >>jjres1

gnuplot
set term post color 12
set outp "jj3.ps"
set multiplot # layout 4,1
set size 0.5,0.25
unset key
set ytics  0,4,8
set xtics -0.2,.2,.7
set xrange [-.4:0.8]
set yrange [0:10]
unset border
set tics nomirror
set boxw 0.09
set zeroa
set style fill solid .5

set ori 0.5,0
plot 'jja' w boxes lc 0
set ori 0.5,.25
plot 'jjb' w boxes lc 0
set ori 0.5,.5
plot 'jjc' w boxes lc 0
set ori 0.5,.75
plot 'jjd' w boxes lc 0
set ori 0.,0
#set zeroaxis
set border
set size 0.5,0.33
set ytics -0.4,0.2,0.6
set yrange [-0.4:0.8]
set xtics -.6,.2,0.4
set xrange [-.7:0.4]
plot 'aa3' w po pt 5 lc 0,0.3574*x+0.0453044 w li lc 0
set ori 0.,.33
#plot [0:7] [-.2:1.1]'jjres2' u 1:2:3  w boxerr lc 0
set ytics -0.4,0.4,0.8
set yrange [-0.5:0.8]
set xtics -.8,.4,0.8
set xrange [-.9:0.9]
plot 'bb3' w po pt 5 lc 0,0.22*x+0.01 w li lc 0
set ori 0.,.66
set boxw .5
unset xtics
set ytics 0,0.4,0.8
plot [0:7][0:0.8] 'jjres1' w boxerr lc 0
quit
gv jj3.ps

paste  cc dd bb ee | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8}' | regress

paste  cc dd bb ee | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9}' | regress





# difference of familialr-novel correaltions.

paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $7;else print -$7}' | stats mean se  

paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $8;else print -$8}' | stats mean se   

paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($9>0) print $9;else print -$9}' | stats mean se  

#paste  cco ddo bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($9>0) print $9;else print -$9}' | stats mean se  



paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $7;else print -$7}' >aa
echo -1 >>aa

paste  cco ddo bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($9>0) print $9;else print -$9}' >>aa


rankind <aa
oneway<aa
echo -1 >>aa
paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $8;else print -$8}' >>aa

paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $7;else print -$7}' >aa
paste  cco ddo bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($9>0) print $9;else print -$9}' >aaa

paste aa aaa | awk '{print $1-$2}' >aaaa

R
a=scan("aa")
b=scan("aaa")
c=scan("aaaa")
wilcox.test(a,b)
wilcox.test(c)


paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $7,"ff";else print -$7,"ff"}' >aa
paste  cco ddo bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($9>0) print $9,"fn";else print -$9,"fn"}' >>aa
paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $8,"fs";else print -$8,"fs"}' >>aa

R
a<-scan("aa",list(x=0,cmp=""))
a$cmp<-factor(a$cmp)
attach(a)
kruskal.test(x~cmp)


model<-aov(x~cmp)
summary(model)
TukeyHSD(model)
pairwise.t.test(x,cmp)


awk '$1>0{print $2}' aa3 | desc -h -m -.6 -M .8 -i .1 | tail -n +2 >aa3.h1
awk '$1<0{print $2}' aa3 | desc -h -m -.6 -M .8 -i .1 | tail -n +2 >aa3.h2
awk '$1>0{print $2}' bb3 | desc -h -m -.6 -M .8 -i .1 | tail -n +2 >bb3.h1
awk '$1<0{print $2}' bb3 | desc -h -m -.6 -M .8 -i .1 | tail -n +2 >bb3.h2

gnuplot
set term post  solid 20
set outp "jj.ps"
set style fill solid .4
unset key
set yzeroaxis
set multiplot layout 2,2
set tics nomirror out
set yrange [0:16]
set xrange [-0.6:0.7]
set ytics 0,4,16
set xtics -.4,.2,.4
set label "p<0.001" at .2,12
plot 'aa3.h1' w boxes lc 0 lw 2
unset label
set label "p<0.005" at .2,12
plot 'aa3.h2' w boxes lc 0 lw 2
unset label
set label "p=0.408" at .2,12
plot 'bb3.h1' w boxes lc 0 lw 2
unset label
set label "p=0.205" at .2,12
plot 'bb3.h2' w boxes lc 0 lw 2
quit

gv jj.ps

#4A-3, 4A-4 does FAM1-NOV spike tranmssion changes predicted by pyramidal and interneuron rate changes
paste  cc dd ff bbint bbpyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $8,$10,$12}' >aa;stparcor aa
# 4A-1, 4A-2
colex 1 2 <aa > aaa; stpearcor aaa
colex 1 3 <aa > aaa; stpearcor aaa
#4B, right 2:same for light application session
paste  cc dd ff bbint bbpyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$11}' >aa;stparcor aa
# left 2
colex 1 2 <aa > aaa; stpearcor aaa
colex 1 3 <aa > aaa; stpearcor aaa
# LOO for 4A/B
# L183? - LEAVE-ONE-OUT, WILCOXON
echo "LEAVE-ONE-OUT ANALYSIS:"
for nm in mjc71 mjc142  mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
paste  cc dd ff bbint bbpyr bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($13 != "'$nm'") print $8,$10,$12}' >aa;stparcor aa
colex 1 2 <aa > aaa; stpearcor aaa
colex 1 3 <aa > aaa; stpearcor aaa
paste  cc dd ff bbint bbpyr bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($13 != "'$nm'")print $7,$9,$11}' >aa;stparcor aa
colex 1 2 <aa > aaa; stpearcor aaa
colex 1 3 <aa > aaa; stpearcor aaa
done

# 4A : ANOVA instead of LOO and partial correlations
paste  cc dd ff bbint bbpyr bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $8,$10,$12,$13}' > tp_iprates_nov
# REMOVING 1 OUTLIER (1.5*) MAKES IT NORMAL ! (but animal is significant after this)
R
library(nlme)
a<-scan("tp_iprates_nov",list(dtp=0,dri=0,drp=0,an=""))
a$inte<-factor(a$inte)
#a$dtp<-(1+a$dtp)^0.5 	# FOR NORMALITY - if outlier not removed
attach(a)
fiti<-lme(dtp ~ dri, random=~1|an)
fitp<-lme(dtp ~ drp, random=~1|an)
fiti_ml<-lme(dtp ~ dri, random=~1|an, method="ML")
fitp_ml<-lme(dtp ~ drp, random=~1|an, method="ML")
fiti_f<-lm(dtp ~ dri)
fitp_f<-lm(dtp ~ drp)
fitip<-lme(dtp ~ drp + dri, random=~1|an)
fitip_ml<-lme(dtp ~ drp + dri, random=~1|an, method="ML")
fitip_f<-lm(dtp ~ drp + dri)
print("=============================================================================[ SIMPLE ]=======================================================================================")
anova(fiti)
anova(fitp)
anova(fitip)
print("=============================================================================[ PARTIALS ]=======================================================================================")
anova(fiti_ml, fitip_ml)
anova(fitp_ml, fitip_ml)
print("=============================================================================[ ANIMAL ]=======================================================================================")
anova(fiti, fiti_f)
anova(fitp, fitp_f)
anova(fitip, fitip_f)
q()
n

# 4B : ANOVA instead of LOO and partial correlations 			!!! MAKE SURE TO USE 
paste  cc dd ff bbint bbpyr bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$11,$13}' > tp_iprates_faml
R
library(nlme)
a<-scan("tp_iprates_faml",list(dtp=0,dri=0,drp=0,an=""))
a$inte<-factor(a$inte)
a$dtp<-(1+a$dtp)^0.5 	# FOR NORMALITY
attach(a)
fiti<-lme(dtp ~ dri, random=~1|an)
fitp<-lme(dtp ~ drp, random=~1|an)
fiti_f<-lm(dtp ~ dri)
fitp_f<-lm(dtp ~ drp)
fiti_ml<-lme(dtp ~ dri, random=~1|an, method="ML")
fitp_ml<-lme(dtp ~ drp, random=~1|an, method="ML")
fitip<-lme(dtp ~ drp + dri, random=~1|an)
fitip_f<-lm(dtp ~ drp + dri + an)
fitip_ml<-lme(dtp ~ drp + dri, random=~1|an, method="ML")
print("============================================================================[ PARTIALS ]===================================================================================")
anova(fiti_ml, fitip_ml)
anova(fitp_ml, fitip_ml)
print("============================================================================[ SIMPLE ]===================================================================================")
anova(fiti)
anova(fitp)
anova(fitip)
print("============================================================================[ ANIMAL ]===================================================================================")
anova(fiti, fiti_f)
anova(fitp, fitp_f)
anova(fitip, fitip_f)
q()
n

# 4A-1, 4A-2
paste  cc dd ff bbint bbpyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $8,$10,$12}' >aa
colex 1 2 <aa > aaa; stpearcorse aaa |  awk '{print 1,$1,$3}' >jjres_4
colex 1 3 <aa > aaa; stpearcorse aaa |  awk '{print 1.5,$1,$3}' >>jjres_4
# Partials
stparcorse aa | awk '{print 2.5,$3,$4}' >>jjres_4 # was 5/jjres
stparcorse aa | awk '{print 3,$5,$6}' >>jjres_4
# 4B-1, 4B-2
paste  cc dd ff bbint bbpyr | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$11}' >aa
colex 1 2 <aa > aaa; stpearcorse aaa |  awk '{print 1,$1,$3}' >jjres1_4
colex 1 3 <aa > aaa; stpearcorse aaa |  awk '{print 1.5,$1,$3}' >>jjres1_4
# Partials
stparcorse aa | awk '{print 2.5,$3,$4}' >>jjres1_4 # was 5/jjres
stparcorse aa | awk '{print 3,$5,$6}' >>jjres1_4

# Figure 4
gnuplot
set term post color 12
set size ratio 0.4
set outp "jj4.ps"
set multiplot layout 1,2
set zeroaxis
unset key
set tics nomirror
set boxw .5
unset xtics
set ytics 0,0.2,0.4,0.6,0.8
plot [0:4][-0.2:0.8] 'jjres_4' w boxerr lc 0 # 4A
plot [0:4] [-0.2:0.8]'jjres1_4' w boxerr lc 0 # 4B
quit
gv jj4.ps





pmo-dispphilcorall
pmo-dispphilcoronepair


# FIGURE 6, fig 6 results number of pairing vs mono change - 			DO IT FOR MULTIPLE INTERVALS ! for default intervals: LOO was n.s. for 3/5 animals!

# UPD 3: 		replace aaint <--> aapcoi1d (dummy column added)
#   Perhaps for partial we could try whether pairing dependent of int rate changes
#   Ie: F2-F1 ~ Pairing(light) | (norm-int-rate-change(f1-light)
#   Considering that interneuron but not pyramidal rate changes during light predicted f2-f1 change….
rm an_mod_p an_mod_r parcor an_an_p pearcor an_pp3_p an_pp2_p an_anc_p an_pyr_p an_pra_p
for vint in 5 10 20 50 100 # was +2,200 before
do
		echo $vint 		

		paste  cc dd bb ee3.$vint aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$11}' >aap1; stparcor aap1 >> parcor
		paste  cc dd bb ee3.$vint aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$11}' >aap2; stparcor aap2 >> parcor
		paste  cc dd bb ee3.$vint aaint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10,$11}' >aap3; stparcor aap3 >> parcor
#		Rscript anova_model_test.R

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

# SAME LOO - DON'T DO THIS, USE ANIMAL VARIABLE IN ANOVA!
rm an_mod_p an_mod_r parcor an_an_p acorints
for vint in 5 10 20 50 100
do
for nm in mjc71 mjc142  mjc101 mjc51 jc218
do
		paste  cc dd bb ee3.$vint aaint bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($13!="'$nm'") print $7,$8,$11}' >aa1; stparcor aa1 >> parcor
		paste  cc dd bb ee3.$vint aaint bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($13!="'$nm'") print $7,$9,$11}' >aa2; stparcor aa2 >> parcor
		paste  cc dd bb ee3.$vint aaint bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($13!="'$nm'") print $7,$10,$11}' >aa3; stparcor aa3 >> parcor
		# writes to an_mod_r and an_mod_p
		Rscript anova_model_test.R

		# non-partial, normal
		paste  cc dd bb ee3.$vint aaint bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($13!="'$nm'") print $7,$8}' >aa1; stpearcor aa1 >> acorints
		paste  cc dd bb ee3.$vint aaint bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($13!="'$nm'") print $7,$9}' >aa2; stpearcor aa2 >> acorints
		paste  cc dd bb ee3.$vint aaint bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($13!="'$nm'") print $7,$10}' >aa3; stpearcor aa3 >> acorints	
done			
done
grep -o "p=0.* B" parcor | grep -o "\-\?0\.[0-9]\{5\}" > parcor_p
grep -o "B: r=-\?0.* B" parcor | grep -o  "r=-\?0.* p" | grep -o "\-\?0\.[0-9]\{5\}" > parcor_r
awk '{print $1}' acorints > acorints_r
awk '{print $2}' acorints > acorints_p

# FIGURE 6 - normal and partial correlations Pairing / | IN rate change
# also int/pyr rate change partial by pairing
gnuplot
set term post color 12
set outp "jj_i2.ps"
unset key
set tics nomirror
unset xtics
#set multiplot layout 3,2
set boxw .5
set ytics 0,0.2,0.4,0.6,0.8
set xzeroax
#plot [0:15][-0.25:0.8] 'jji2' w boxerr lc 0
plot [0:15][-0.3:0.8] 'jji3' w boxerr lc 0
quit
gv jj_i2.ps

R
a<-scan("aa1",list(f12=0,pr=0,int=0))
#a$inte<-factor(a$inte)
attach(a)
fit_pr<-lm(f12 ~ pr)
fit_int<-lm(f12 ~ int)
fit2<-lm(f12 ~ pr + int)
anova(fit_pr)
anova(fit_int)
anova(fit_pr, fit2)
anova(fit_int, fit2)
q()
n




# FAM1-to-FAM2 vs. (before / after / all : pairing events)
paste  cc dd bb ee3 | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8}' >aa; stpearcor1 aa
paste  cc dd bb ee3 | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9}' >aa; stpearcor1 aa
paste  cc dd bb ee3 | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10}' >aa; stpearcor1 aa
# UPD for different intervals
rm corints corints_ro corints_p corints_r
for vint in 2 5 10 20 50 100 200
do
paste  cc dd bb ee3.$vint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8}' >aa; stpearcor1 aa >> corints
cp aa aa.$vint
paste  cc dd bb ee3.$vint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9}' >aa; stpearcor1 aa >> corints
paste  cc dd bb ee3.$vint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10}' >aa; stpearcor1 aa >> corints
# rank order
paste  cc dd bb ee3.$vint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8}' | rankrel | grep rho >> corints_ro
paste  cc dd bb ee3.$vint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9}' | rankrel | grep rho >> corints_ro
paste  cc dd bb ee3.$vint | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10}' | rankrel| grep rho >> corints_ro
echo "INTERVAL = "$vint" MS:"
done
awk '{print $1}' corints > corints_r
awk '{print $2}' corints > corints_p
grep -o "\-\?0.*" corints_ro > corints_ros


# FAM1-to-FAM2 vs. (before / after / all : pairing events) | BASELINE PAIRING 			<<<<<<< this one had reproducibility issues (1/3) - confirmed
paste  cc dd bb ee3 aapcoi1 | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$11}' >aa; stparcor aa
paste  cc dd bb ee3 aapcoi1 | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$11}' >aa; stparcor aa
paste  cc dd bb ee3 aapcoi1 | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10,$11}' >aa; stparcor aa
# UPD for different intervals: (PARTIAL, ALTOGETHER)
rm parints ares1 ares2 aniall pair_rs pair_ps
for vint in 2 5 10 20 50 100 200
do
echo "INTERVAL = "$vint" MS:"
paste  cc dd bb ee3.$vint aapcoi1 | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$11}' >aa; stparcor aa >>parints
paste  cc dd bb ee3.$vint aapcoi1 | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$11}' >aa; stparcor aa >>parints
paste  cc dd bb ee3.$vint aapcoi1 | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10,$11}' >aa; stparcor aa >> parints
# compile aniall with data across multiple intervals; only use one of these: +,-,+-
paste  cc dd bb ee3.$vint aapcoi1 bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$11,$12,'$vint'}' >>aniall;
#paste  cc dd bb ee3.$vint aapcoi1 bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$11,$12,'$vint'}' >>aniall;
#paste  cc dd bb ee3.$vint aapcoi1 bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10,$11,$12,'$vint'}' >>aniall;
done
grep -o "B: r=-\?0.* B" parints | grep -o  "r=-\?0.* p" | grep -o "\-\?0\.[0-9]\{5\}" > pair_rs
grep -o "p=0.* B" parints | grep -o "\-\?0\.[0-9]\{5\}" > pair_ps

# analyze with R
paste  cc dd bb ee3.$vint aapcoi1 bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$11,$12,'$vint'}' >ani;
Rscript anova_pairings.R
paste  cc dd bb ee3.$vint aapcoi1 bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$9,$11,$12,'$vint'}' >ani;
Rscript anova_pairings.R
paste  cc dd bb ee3.$vint aapcoi1 bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$10,$11,$12,'$vint'}' >ani;
Rscript anova_pairings.R
#done

# ALT to Rscript -> execute by launching R in shell
R
a<-scan("ani",list(f1f2=0, pair=0, bpair=0, anim=""))
a$anim<-factor(a$anim)
fit1 <- lm(f1f2 ~ pair + bpair + anim, data=a)
fit2 <- lm(f1f2 ~ bpair + anim, data=a)
p1=toString(anova(fit1, fit2)$"Pr(>F)"[2])
write(p1, file="ares1.txt", append=TRUE)
fit1 <- lm(f1f2 ~ pair + bpair, data=a)
fit2 <- lm(f1f2 ~ bpair, data=a)
anova(fit1, fit2)
p2=toString(anova(fit1, fit2)$"Pr(>F)"[2])
write(p2, file="ares2.txt", append=TRUE)
q()
n
#done


# Partial correlaion with transform of the dependent variable - to make it normal
paste  cc dd bb ee3 aapcoi1 | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print sqrt($7+1),$8,$11}' >aa; stparcor aa
# >>>>>>> WORKS WITH NEW DATA = PARTIAL CORREALTIONS ARE SIGNIFICANT;  Partial correlation : absolute values + sqrt transform for all
paste  cc dd bb ee3 aapcoi1 | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print sqrt(abs($7)),sqrt(abs($8)),sqrt(abs($11))}' >aa; stparcor aa
paste  cc dd bb ee3 aapcoi1 | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print sqrt(abs($7)),sqrt(abs($9)),sqrt(abs($11))}' >aa; stparcor aa
paste  cc dd bb ee3 aapcoi1 | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print sqrt(abs($7)),sqrt(abs($10)),sqrt(abs($11))}' >aa; stparcor aa

# UPD: partial correlations for different intervals: - ABSOLUTE VALUES
rm parint_abs acorints acorints_r acorints_p
for vint in 2 5 10 20 50 100 200
do
echo "INTERVAL = "$vint" MS:"
paste  cc dd bb ee3.$vint | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print sqrt(abs($7)),sqrt(abs($8)),sqrt(abs($11))}' >aa; stpearcor1 aa >> acorints
paste  cc dd bb ee3.$vint | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print sqrt(abs($7)),sqrt(abs($9)),sqrt(abs($11))}' >aa; stpearcor1 aa >> acorints
paste  cc dd bb ee3.$vint | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print sqrt(abs($7)),sqrt(abs($10)),sqrt(abs($11))}' >aa; stpearcor1 aa >> acorints
paste  cc dd bb ee3.$vint aapcoi1 | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print sqrt(abs($7)),sqrt(abs($8)),sqrt(abs($11))}' >aa;stparcor aa>>parint_abs
paste  cc dd bb ee3.$vint aapcoi1 | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print sqrt(abs($7)),sqrt(abs($9)),sqrt(abs($11))}' >aa;stparcor aa>>parint_abs
paste  cc dd bb ee3.$vint aapcoi1 | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print sqrt(abs($7)),sqrt(abs($10)),sqrt(abs($11))}' >aa;stparcor aa>>parint_abs
done
# extract Rs and p-values
grep -o "B: r=-\?0.* B" parint_abs | grep -o  "r=-\?0.* p" | grep -o "\-\?0\.[0-9]\{5\}" > pair_abs_rs
grep -o "p=0.* B" parint_abs | grep -o "\-\?0\.[0-9]\{5\}" > pair_abs_ps
awk '{print $1}' acorints > acorints_r
awk '{print $2}' acorints > acorints_p


# try it LOO - only default interval
for nm in mjc71 mjc142 mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
paste  cc dd bb ee3 aapcoi1 bbname| awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($12!="'$nm'")print sqrt(abs($7)),sqrt(abs($8)),sqrt(abs($11))}' >aa; stparcor aa
done

# UPD2: partial and normal correlations for different intervals and LOO by animals (plot max later for example) + !!! try ANOVA later for different intervals
# 	BOTH TRANSFORMED AND NOT ..
rm parint_abs, acorints
for vint in 2 5 10 20 50 100 200
do
echo "INTERVAL = "$vint" MS:"
for nm in mjc71 mjc142 mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
paste  cc dd bb ee3.$vint bbname | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($11!="'$nm'") print $7,$8}' >aa; stpearcor1 aa >> acorints
paste  cc dd bb ee3.$vint bbname | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($11!="'$nm'") print $7,$9}' >aa; stpearcor1 aa >> acorints
paste  cc dd bb ee3.$vint bbname | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($11!="'$nm'") print $7,$10}' >aa; stpearcor1 aa >> acorints
paste  cc dd bb ee3.$vint aapcoi1 bbname | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($12!="'$nm'") print $7,$8,$11}' >aa;stparcor aa>>parint_abs
paste  cc dd bb ee3.$vint aapcoi1 bbname | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($12!="'$nm'") print $7,$9,$11}' >aa;stparcor aa>>parint_abs
paste  cc dd bb ee3.$vint aapcoi1 bbname | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($12!="'$nm'") print $7,$10,$11}' >aa;stparcor aa>>parint_abs
#paste  cc dd bb ee3.$vint bbname | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($11!="'$nm'") print sqrt(abs($7)),sqrt(abs($8))}' >aa; stpearcor1 aa >> acorints
#paste  cc dd bb ee3.$vint bbname | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($11!="'$nm'") print sqrt(abs($7)),sqrt(abs($9))}' >aa; stpearcor1 aa >> acorints
#paste  cc dd bb ee3.$vint bbname | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($11!="'$nm'") print sqrt(abs($7)),sqrt(abs($10))}' >aa; stpearcor1 aa >> acorints
#paste  cc dd bb ee3.$vint aapcoi1 bbname | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($12!="'$nm'") print sqrt(abs($7)),sqrt(abs($8)),sqrt(abs($11))}' >aa;stparcor aa>>parint_abs
#paste  cc dd bb ee3.$vint aapcoi1 bbname | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($12!="'$nm'") print sqrt(abs($7)),sqrt(abs($9)),sqrt(abs($11))}' >aa;stparcor aa>>parint_abs
#paste  cc dd bb ee3.$vint aapcoi1 bbname | awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if($12!="'$nm'") print sqrt(abs($7)),sqrt(abs($10)),sqrt(abs($11))}' >aa;stparcor aa>>parint_abs
done
done
# extract Rs and p-values
grep -o "B: r=-\?0.* B" parint_abs | grep -o  "r=-\?0.* p" | grep -o "\-\?0\.[0-9]\{5\}" > pair_abs_rs
grep -o "p=0.* B" parint_abs | grep -o "\-\?0\.[0-9]\{5\}" > pair_abs_ps
awk '{print $1}' acorints > acorints_r
awk '{print $2}' acorints > acorints_p



# ANCOVA: FAM1-FAM2 = pairing * baseline_paring * animal
paste  cc dd bb ee3 aapcoi1 bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,$8,$11,$12}' >anc;
# ABSOLUTE VALUES
paste  cc dd bb ee3 aapcoi1 bbname | awk 'function abs(v) {return v < 0 ? -v : v} ($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print abs($7),abs($8),abs($11),$12}' >anc;
# ABSOLUTE VALUES + SQRT
paste  cc dd bb ee3 aapcoi1 bbname | awk 'function abs(v) {return v < 0 ? -v : v} ($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print sqrt(abs($7)),sqrt(abs($8)),sqrt(abs($11)),$12}' >anc;
R
a<-scan("anc",list(f1f2=0, pair=0, bpair=0, anim=""))
a$anim<-factor(a$anim)
# apply transform if neede (try shapiro.test) : sqrt for absolute values for all 3 variables; ^2 for f1f2 if not raw values
#attach(a)
fit1 <- lm(f1f2 ~ pair + bpair + anim, data=a)
fit2 <- lm(f1f2 ~ bpair + anim, data=a)
anova(fit1, fit2)
fit1 <- lm(f1f2 ~ pair + bpair, data=a)
fit2 <- lm(f1f2 ~ bpair, data=a)
anova(fit1, fit2)
q()
n




# 2B-0: comparing 1st and 2nd half  beginnign and across before and after light (1st or 2nd halfs) - THIS IS USED FOR MANUSCRIPT STATS !!!!!!!!

awk '{a=$1;b=$2;aa=$1;bb=$14;c1=(a-b)/(a+b);c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfscor5 >fffs
paste  cc dd fffs | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $7,$8}'  | rankrel
# p=0.03228 ALL - w/o JC-218
# THIS WORKS LOO AND ANOVA
#awk '{a=$1;b=$2;aa=$1;bb=$13;c1=(a-b)/(a+b);c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs
#paste  cc dd fffs | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $7,$8}'  | pair
# p=0.0329 ALL - w/o JC-218 <<<<<<<< USE THIS BECAUSE THIS ONE IS ODD-EVEN AND ODD-EVEN


# 2-WAY FAM1o-FAM1e vs. FAM1-FAM2 (ff/1)
awk '{a=$1;b=$2;aa=$1;bb=$14;if (a+b==0) c1=0; else c1=(a-b)/(a+b);if (aa+bb==0)c2=0; else c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs
##awk '{a=$1;b=$2;aa=$2;bb=$14;if (a+b==0) c1=0; else c1=(a-b)/(a+b);if (aa+bb==0)c2=0; else c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs2
#awk '{a=$1;b=$2;aa=$1;bb=$13;if (a+b==0) c1=0; else c1=(a-b)/(a+b);if (aa+bb==0)c2=0; else c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs3
#awk '{a=$1;b=$2;aa=$2;bb=$13;if (a+b==0) c1=0; else c1=(a-b)/(a+b);if (aa+bb==0)c2=0; else c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs4
#paste fffs fffs2 fffs3 fffs4 | awk '{print ($2+$4+$6+$8)/4}' > fffsa
paste  cc dd fffs bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $7,"w",$9}' > a2way
paste  cc dd bb   bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ if ($7<0) $7=-$7; print $7,"b",$8}' >> a2way
#paste  cc dd ff   bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ if ($8<0) $8=-$8; print $8,"b",$9}' >> a2way
#paste  cc dd ff   bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ if ($7<0) $7=-$7; print $7,"b",$9}' >> a2way
#paste  cc dd fffs bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $8,"b",$9}' >> a2way
#paste  cc dd fffsa bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $7,"b",$8}' >> a2way
R
library(nlme)
a<-scan("a2way",list(df=0,wb="",anim=""))
a$wb<-factor(a$wb)
a$anim<-factor(a$anim)
attach(a)
#model1<-aov(df~anim+wb)
#model1<-aov(df~anim*wb)
model1<-lme(df~wb, random=~1|anim) 	# NORMAL IS ~wb, ~1|anim 
anova(model1)
#model2<-gls(df~wb*anim, data=a, method="REML")
model2<-lm(df~wb, data=a)
print("======[ ANIMAL ]========")
anova(model1, model2)
print("==========[ WITHIN vs BETWEEN ]========")
anova(model1)
anova(model2)
#TukeyHSD(model2,which="wb:anim")
#TukeyHSD(model1,which="anim")
#TukeyHSD(model1)
#TukeyHSD(model1,which="wb*anim")
#TukeyHSD(model2,which="wb")
#model2<-aov(df~anim*wb*ses)
#anova(model2)
q()
n


# p=0.0004 ALL - w/o JC-218
awk '{a=$1;b=$2;aa=$2;bb=$13;c1=(a-b)/(a+b);c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs
paste  cc dd fffs | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $7,$8}'  | pair

# p=0.0000 ALL - w/o JC-218
awk '{a=$1;b=$2;aa=$2;bb=$14;c1=(a-b)/(a+b);c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs
paste  cc dd fffs | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $7,$8}'  | pair


# 2B-0: ANOVA AND LOO
# ANOVA
#awk '{a=$1;b=$2;aa=$1;bb=$13;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs
awk '{a=$1;b=$2;aa=$1;bb=$14;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs
#awk '{a=$1;b=$2;aa=$2;bb=$13;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs # <<<<<<<<<< ONLY ONE NOT WORKING 
#awk '{a=$1;b=$2;aa=$2;bb=$14;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs
paste  cc dd fffs bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $7,1,$9;print $8,2,$9}' > oecmp
# ANOVA with 2 factors: pos/neg and animal
R
a<-scan("oecmp",list(df=0,gr=0,anim=""))
a$gr<-factor(a$gr)
a$anim<-factor(a$anim)
attach(a)
model1<-aov(df~anim+gr) # 1 OK, 2 --, 3 OK, 4 --
anova(model1)
TukeyHSD(model1,which="anim")
TukeyHSD(model1,which="gr")
model2<-aov(df~anim*gr) # 1 OK, 2 --, 3 OK, 4 --
anova(model2)
q()
n
# LOO
for nm in mjc71 mjc142 mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
# >>>>>>>>>>>>> div 0 - either ignore or assign 0
#awk '{a=$1;b=$2;aa=$1;bb=$13;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs
awk '{a=$1;b=$2;aa=$1;bb=$14;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs
#awk '{a=$1;b=$2;aa=$2;bb=$13;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs <<<<<<<<<< ONLY ONE NOT WORKING 
#awk '{a=$1;b=$2;aa=$2;bb=$14;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs
paste  cc dd fffs bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ if(($9!="'$nm'")&&($7>0))print $7,$8}'  | pair
done

# PLOST 2B CONTROL COMPARISOIN
awk '{a=$1;b=$2;aa=$1;bb=$14;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;c2=(aa-bb)/(aa+bb);if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1}' allfs1cor5 | 
paste  cc dd fffs | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $7}' | stats mean se  | awk '{print 1,$1,$2}' >jji1
paste  cc dd fffs | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $8}' | stats mean se  | awk '{print 2,$1,$2}' >>jji1


gnuplot
set term post color 12
set outp "jj_i1.ps"
unset key
set tics nomirror
unset xtics
#set multiplot layout 3,2
set boxw .5
set ytics 0,0.2,0.4
set xzeroax
plot [0:5][0:0.5] 'jji1' w boxerr lc 0
quit
gv jj_i1.ps



# ----------- WAS WRONG BEFORE BECAUSE ABS WAS NOT APPLIED TO bb !!!!!!!!!! UPD: compare odd-even to actual value in 2B which is in bb
#paste  cc dd bb | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $7;else print -$7}' > fam1tofam2
# FIX 0 DIVISION
awk '{a=$1;b=$2;aa=$1;bb=$14;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;if(aa+bb!=0)c2=(aa-bb)/(aa+bb);else c2=0;if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfscor5 >fffs
awk '{a=$1;b=$2;aa=$2;bb=$14;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;if(aa+bb!=0)c2=(aa-bb)/(aa+bb);else c2=0;if (c1<0) c1=-c1;if (c2<0) c2=-c2;print c1,c2}' allfs1cor5 >fffs
# NONE WORKS - ABS
paste  cc dd fffs bb| awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $7,abs($9)}'  | pair
paste  cc dd fffs bb| awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $7,abs($9)}'  | rankrel
# TRY NOABS
awk '{a=$1;b=$2;aa=$2;bb=$14;if(a+b!=0)c1=(a-b)/(a+b);else c1=0;if(aa+bb!=0)c2=(aa-bb)/(aa+bb);else c2=0; print c1,c2}' allfs1cor5 >fffsnabs
paste  cc dd fffsnabs bb| awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $7,$9}'  | pair
paste  cc dd fffsnabs bb| awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $7,$9}'  | rankrel
# now do LOO
for nm in mjc71 mjc142 mjc101 mjc51 jc218
do
printf "\n\nEXCLUDING $nm ...\n"
paste  cc dd fffs bb bbname| awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ if($10!="'$nm'")print $7,abs($9)}'  | pair 
paste  cc dd fffs bb bbname| awk 'function abs(v) {return v < 0 ? -v : v}($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ if($10!="'$nm'")print $7,abs($9)}'  | rankrel
done


or

paste  cc dd fffs | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $7}'  >jjaa
paste  cc dd bb ff | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $7;else print -$7}' >jjbb
paste jjaa jjbb | pair
paste jjaa jjbb | rankrel




szth=1000
peath=2
cvth=3
awk '{a=$8;b=$10;print (a-b)/(a+b)}' allcorhu >bb

awk '{print $1,$5}' allszcorhu >cc
awk '{print $1,$2,$5,$6}' allzzcorhu >dd
paste  cc dd bb | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $7;else print -$7}' | stats mean se n


#per animal fig 2F - INSERT

# DEFINED OK ABOVE, THIS IS INCORRECT FOR JC218 <<< USE THIS TO REPORT DIFFERENCE BETWEEN POS AND NEG GROUPS -in 2F INSERT
# awk '{split($1,a,"-");print a[1]}' allcor5 >bbname
paste  cc dd bb ff bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $10,"pos",$7}' >aator
paste  cc dd bb ff bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8<0) print $10,"neg",$7}' >>aator
# ANOVA with 2 factors: pos/neg and animal
R
library(nlme)
a<-scan("aator",list(anim="",pos="",x=0))
a$anim<-factor(a$anim)
a$pos<-factor(a$pos)
attach(a)
#model<-aov(x~anim*pos)
model<-lme(x~pos, random=~1|anim)
modelf<-lm(x~pos)
#summary(model)
anova(model)
anova(model, modelf)
#TukeyHSD(model)
q()
n

# LOO PARTIALS!
paste  cc dd  gg bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $11,$7,$8,$9,$10}' >aator
for nm in mjc71 mjc142  mjc101 mjc51 jc218
do
awk '{if ($1!="'$nm'") print $2,$3,$4}' aator >aa; stparcor aa
done

for nm in mjc71 mjc142  mjc101 mjc51
do
awk '{if ($1!="'$nm'") print $2,$3,$5}' aator >aa; stparcor aa
done



#per animal fig 3c - 3C; USE NEXT ANOVE
paste  cc dd bb aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $10,"pos",$7}' >aator
paste  cc dd bb aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8<0) print $10,"neg",$7}' >>aator
# STANDALONE
paste  cc dd bb aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $7}' | desc
paste  cc dd bb aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8<0) print $7}' | desc
# + same R as above - animal variable not significant, pos variable is significant (Jozsef's implementation)
# ANOVA FOR STP BEFORE VS. AFTER => didn't work! (either for positive or for negative)
paste  cc dd  gg aaint bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($11>0) {print $7,1,$13; print $8,2,$13}}' > an3cpos
paste  cc dd  gg aaint bbname| awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($11<0) {print $7,1,$13; print $8,2,$13}}' > an3cneg
R
library(nlme)
#a<-scan("an3cpos",list(tp=0,ses="",an=""))
a<-scan("an3cneg",list(tp=0,ses="",an=""))
a$ses<-factor(a$ses)
a$an<-factor(a$an)
attach(a)
#fit<-lme(tp ~ ses, random=1|an)
fit<-lme(tp ~ 1, random=~1|an)
fit_noan<-lm(tp ~ 1)
#summary(fit)
anova(fit)
anova(fit, fit_noan)
q()
n


#per animal fig 3D and 3C INSERTS - USE THIS 
# FOR PYRAMIDAL
paste  cc dd bb aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $10,"pos",$7}' >aator
paste  cc dd bb aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8<0) print $10,"neg",$7}' >>aator
# FOR INT
#paste  cc dd bb aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $10,"pos",$7}' >aator
#paste  cc dd bb aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8<0) print $10,"neg",$7}' >>aator
#
R
library(nlme)
a<-scan("aator",list(anim="",pos="",y=0))
a$anim<-factor(a$anim)
a$pos<-factor(a$pos)
attach(a)
model<-lme(y~pos, random=~1|anim)
model_f<-lm(y~pos)
anova(model)
anova(model, model_f)
q()
n


# 3C, 3D ADDITIONALY: test ANOVA of linear model of TP change score ~ rate change score + animal
#paste  cc dd bb aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $10,$8,$7}' >aator
#
paste  cc dd bb aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $10,$8,$7}' >aator
#
R
library(nlme)
a<-scan("aator",list(anim="",drs=0,y=0))
a$anim<-factor(a$anim)
attach(a)
model<-lme(y~drs, random=~1|anim)
model_f<-lm(y~drs)
#model1<-lm(y~drs)
#summary(model1)
anova(model)
anova(model, model_f)
q()
n



# PFS VS. FAM1-FAM2 CHANGE:
#paste cc dd bb allpfs bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth')&&($8>-1.5){print $7,$8,$9}' >aapfs
paste cc dd bb allpfs_int bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth')&&($8>-1.5){print $7,$8,$9}' >aapfs
paste cc dd bb allpfs_int aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth')&&($8>-1.5){print $7,$8,$9,$11}' >aapfs
#paste cc dd ff allpfs bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth')&&($9>-1.5){print $7,$9,$10}' >aapfs
#paste cc dd ff allpfs bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth')&&($9>-1.5){print $8,$9,$10}' >aapfs
#
R
library(nlme)
#a<-scan("aapfs",list(dtp=0,pfs=0,anim=""))
a<-scan("aapfs",list(dtp=0,pfs=0,dr=0,anim=""))
a$anim<-factor(a$anim)
attach(a)
model<-lme(dtp~pfs, random=~1|anim)
model_f<-lm(dtp~pfs)

model_r<-lme(dtp~pfs+dr, random=~1|anim)
model_rp<-lme(dtp~dr, random=~1|anim)

#model1<-lm(y~drs)
#summary(model1)
anova(model)
anova(model, model_f)
anova(model_r, model_rp)
anova(model, model_r)
q()
n




paste  cc dd bb ff bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($7>0) print $10,"a",$7;else print $10,"a",-$7}' >aator
paste  cc dd bb ff bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($8>0) print $10,"b",$8;else print $10,"b",-$8}' >>aator
paste  cc dd bb ff bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if ($9>0) print $10,"c",$9;else print $10,"c",-$9}' >>aator

paste  cc dd bb aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $10,$7,$8}' >aator

#or
paste  cc dd bb aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $10,$7,$9}' >aator

R
a<-scan("aator",list(anim="",y=0,x=0))
a$anim<-factor(a$anim)
attach(a)
model<-aov(y~anim*x)
summary(model)
q()
n


paste  cc dd bb aaint bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){ print $10,$7,$8,$9}' >aator


for nm in mjc71 mjc142  mjc101 mjc51
do
awk '{if ($1=="'$nm'") print $2,$3,$4}' aator >aa; stparcor aa
done




paste  cc dd bb ee3 aapcoi1 bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $12,$7,$8,$11}' >aator; 

for nm in mjc71 mjc142  mjc101 mjc51
do
awk '{if ($1=="'$nm'") print $2,$3,$4}' aator >aa; stparcor aa
done


paste  cc dd ff bbint bbpyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $13,$8,$10,$12}' >aator

for nm in mjc71 mjc142  mjc101 mjc51
do
awk '{if ($1!="'$nm'") print $2,$3,$4}' aator >aa; stparcor aa
done

paste  cc dd ff bbint bbpyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){print $13,$7,$9,$11}' >aator

# 2-WAY ANOVA FOR GROUPS IN FIGURE 5
#      2  4  2   2    2      1
paste  cc dd bb aaint aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if(($8>0)&&($10>0))print $7,"ii","pi",$8,$10,$12}' >aator
paste  cc dd bb aaint aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if(($8>0)&&($10<0))print $7,"ii","pd",$8,$10,$12}' >>aator
paste  cc dd bb aaint aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if(($8<0)&&($10>0))print $7,"id","pi",$8,$10,$12}' >>aator
paste  cc dd bb aaint aapyr bbname | awk '($1>'$szth'||$2>'$szth')&&($3>'$peath'||$5>'$peath')&&($4>'$cvth'||$6>'$cvth'){if(($8<0)&&($10<0))print $7,"id","pd",$8,$10,$12}' >>aator
R
library(nlme)
a<-scan("aator",list(dtp=0,gri="",grp="",dri=0,drp=0,anim=""))
a$anim<-factor(a$anim)
a$gri<-factor(a$gri)
a$grp<-factor(a$grp)
attach(a)
#model<-aov(dtp~drp*dri*gri*grp) 	# use for comparing groups
#model<-aov(dtp~drp*dri*gri*grp*anim) 	# -- this one gives many significant interactions! 	----------
#model<-aov(dtp~drp+dri+gri+grp+anim) 	# use for reporting animal variable insignificance
#model<-aov(dtp~drp*dri*gri*grp+anim) 	#
#model<-aov(dtp~gri*grp)		# only groups
#model<-aov(dtp~anim*(drp+dri+gri+grp)) # pairwise interactions with animal
#model<-aov(dtp~gri*grp * anim)		# only groups + animal 					<<<<<<<<< USE THIS ONE - NO SIGNIFICANT INTERACTIONS, ANIMAL NS, CORRECT SIG INT/PYR; but Tukey doesn't change anything here!
#model<-lme(dtp~gri+grp, random=~1|anim) # THIS WORKS!
model<-lme(dtp~gri*grp, random=~1|anim)
model_f<-lm(dtp~gri*grp)
#model_f<-lm(dtp~gri+grp)
summary(model)
anova(model)
print("===========================[ ANIMAL ]===========================")
anova(model, model_f)
print("CANNOT PERFORM TUKEYS TEST FOR MIXED MODEL")
#TukeyHSD(model,which="gri")
#TukeyHSD(model,which="grp")
q()
n

