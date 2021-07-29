
sumsqr <- function(x){
return(sum ((x - mean(x) )^2))
}

pandr <- function(filename){
a<-scan(filename,list(f12=0,pr=0,int=0,pyr=0,an=""))
a$an<-factor(a$an)
attach(a)
fit_pr<-lm(f12 ~ pr + an)

# CONDITIONAL / PARTIAL MODEL COMPARISON
fit_int<-lm(f12 ~ int + an)
fit2<-lm(f12 ~ pr + int + pyr + an)
#fit_int<-lm(f12 ~ int + an)
#fit2<-lm(f12 ~ pr + int + an)
#fit_int<-lm(f12 ~ pyr + an)
#fit2<-lm(f12 ~ pr + pyr + an)

# NEW
fit_pyrpr<-lm(f12 ~ pr + pyr + an)
fit_intpr<-lm(f12 ~ pr + int + an)
fit_all<-lm(f12 ~ pr + pyr + int + an)

#fit_pr_by_pyr_int<-lm(pr ~ pyr + int + an)
fit_pr_by_pyr_int<-lm(pr ~ pyr + int)
#rs_pairing = summary(fit_pr_by_pyr_int)[["r.squared"]]
rs_pairing = summary(fit_pr_by_pyr_int)[["adj.r.squared"]]
cat("R2 FOR PAIRING:", rs_pairing,'\n')

# PYR ONLY
#fit_int<-lm(f12 ~ pyr + an)
#fit2<-lm(f12 ~ pr + pyr + an)

#anova(fit_pr)
anova(fit_int)
#anova(fit_pr, fit2)
anova(fit_int, fit2)
# before using mixed: SIGNIFICANCE OF ADDING PAIRING TO THE MODEL! - PARTIAL CORRELATION ANALOGUE
#p = toString(anova(fit_int, fit2)$"Pr(>F)"[2])
#print(p)

# SIGNIFICANCE OF ADDING RATE TO THE PAIRING
#pra = toString(anova(fit_pr, fit2)$"Pr(>F)"[2])
#pra = toString(anova(fit_pyrpr, fit_all)$"Pr(>F)"[2])
pra = toString(anova(fit_intpr, fit_all)$"Pr(>F)"[2])

#r = summary(fiit2)["r.squared"] // NOT SO EASY - SEE 1-RSS/TSS ...
# PARTIAL R
rss = anova(fit_int, fit2)["RSS"]
ss = sumsqr(a$f12)
anp = toString(anova(fit2)[["Pr(>F)"]][3])


# MIXED MODELS:
fit_int_pyr_m<-lme(f12 ~ int + pyr, random=~1|an)
fit_int_m<-lme(f12 ~ int, random=~1|an)
fit_pyr_m<-lme(f12 ~ pyr, random=~1|an)
fit_pr_m<-lme(f12 ~ pr, random=~1|an)
fit_pr_int_m<-lme(f12 ~ pr + int, random=~1|an)
fit_pr_pyr_m<-lme(f12 ~ pr + pyr, random=~1|an)
fit_pr_int_noan<-lm(f12 ~ pr + int)
fit_pr_pyr_noan<-lm(f12 ~ pr + pyr)
fit_pr_noan<-lm(f12 ~ pr)
fit_pr_int_pyr_m<-lme(f12 ~ pr + int + pyr, random=~1|an)
fit2_noan<-lm(f12 ~ pr + int + pyr)

# ML for comparing with different mixed effects
fit_int_pyr_ml<-lme(f12 ~ int + pyr, random=~1|an, method='ML')
fit_int_ml<-lme(f12 ~ int, random=~1|an, method='ML')
fit_pyr_ml<-lme(f12 ~ pyr, random=~1|an, method='ML')
fit_pr_ml<-lme(f12 ~ pr, random=~1|an, method='ML')
fit_pr_int_ml<-lme(f12 ~ pr + int, random=~1|an, method='ML')
fit_pr_pyr_ml<-lme(f12 ~ pr + pyr, random=~1|an, method='ML')
fit_pr_int_pyr_ml<-lme(f12 ~ pr + int + pyr, random=~1|an, method='ML')

# PARTIAL FIVEN RATE CHANGE (1 ONLY - EITHER PYR OR INT
p = toString(anova(fit_int_ml, fit_pr_int_ml)$"p-value"[2])
#p = toString(anova(fit_pyr_ml, fit_pr_pyr_ml)$"p-value"[2])

#anp = toString(anova(fit2_m, fit2_noan)$"p-value"[2])
anp = toString(anova(fit_pr_m, fit_pr_noan)$"p-value"[2])

anpc = toString(anova(fit_pr_pyr_m, fit_pr_pyr_noan)$"p-value"[2])
#anpc = toString(anova(fit_pr_int_m, fit_pr_int_noan)$"p-value"[2])


# FRACTION OF REMAINING VARIANCE EXPLAINED
#rp = toString(1 - (rss[[1]][2]) / (rss[[1]][1]))

# FRACTION OF TOTAL VARIANCE EXPLAINED ADDITIONALLY
rp = toString((rss[[1]][1] - rss[[1]][2])/ss)
# FROM F-TEST
#rp = toString((rss[[1]][1] - rss[[1]][2])/(rss[[1]][2]))

# before using mixed:
#pp3 = toString(anova(fit2)[["Pr(>F)"]][1])
#pp2 = toString(anova(fit_pr)[["Pr(>F)"]][1])

# ALT: use t-test of linear model
#pp3 = summary(fit2)[["coefficients"]][2,4]
#pp2 = summary(fit_pr)[["coefficients"]][2,4]


# MIXED MODELS
#pp3 = toString(anova(fit_int_pyr_m)[["p-value"]][2])
pp3 = toString(anova(fit_pr_int_pyr_ml, fit_int_pyr_ml)[["p-value"]][2])
pp2 = toString(anova(fit_pr_m)[["p-value"]][2])

#ppyr = toString(anova(fit2_m)[["p-value"]][4])
#ppyr = toString(anova(fit_pr_pyr_ml, fit_pr_ml)$"p-value"[2])
ppyr = toString(anova(fit_pr_int_ml, fit_pr_ml)$"p-value"[2])

# MIXED MODEL:


detach(a)

return(list("p"=p,"rp"=rp,"anp"=anp, "pp3"=pp3, "pp2"=pp2, "anpc"=anpc, "ppyr"=ppyr, "pra"=pra))
}

library(nlme)

l1 = pandr("aa1")
l2 = pandr("aa2")
l3 = pandr("aa3")

p1 = l1[["p"]]
rp1 = l1[["rp"]]
p2 = l2[["p"]]
rp2 = l2[["rp"]]
p3 = l3[["p"]]
rp3 = l3[["rp"]]

anp1 = l1[["anp"]]
anp2 = l2[["anp"]]
anp3 = l3[["anp"]]

pp21 = l1[["pp2"]]
pp22 = l2[["pp2"]]
pp23 = l3[["pp2"]]

pp31 = l1[["pp3"]]
pp32 = l2[["pp3"]]
pp33 = l3[["pp3"]]

anpc1 = l1[["anpc"]]
anpc2 = l2[["anpc"]]
anpc3 = l3[["anpc"]]

ppy1 = l1[["ppyr"]]
ppy2 = l2[["ppyr"]]
ppy3 = l3[["ppyr"]]

pra1 = l1[["pra"]]
pra2 = l2[["pra"]]
pra3 = l3[["pra"]]

# PAIRING GIVEN INT (AND PYR) - MODEL COMPARISON
write(p1, file="an_mod_p", append=TRUE)
write(p2, file="an_mod_p", append=TRUE)
write(p3, file="an_mod_p", append=TRUE)

# FRACTION OF TOTAL VARIANCE EXPLAINED ADDITIONALLY
write(rp1, file="an_mod_r", append=TRUE)
write(rp2, file="an_mod_r", append=TRUE)
write(rp3, file="an_mod_r", append=TRUE)

# FULL MODEL - ANIMAL SIGNIFICANCE
write(anp1, file="an_an_p", append=TRUE)
write(anp2, file="an_an_p", append=TRUE)
write(anp3, file="an_an_p", append=TRUE)

# MODEL WITH PAIRING - ANIMAL SIGNIFICANCE
write(anpc1, file="an_anc_p", append=TRUE)
write(anpc2, file="an_anc_p", append=TRUE)
write(anpc3, file="an_anc_p", append=TRUE)

# ANOVA P OF PAIRING IN MODEL WITH PAIRING ONLY
write(pp21, file="an_pp2_p", append=TRUE)
write(pp22, file="an_pp2_p", append=TRUE)
write(pp23, file="an_pp2_p", append=TRUE)

# ANOVA P OF PAIRING IN FULL MODEL
write(pp31, file="an_pp3_p", append=TRUE)
write(pp32, file="an_pp3_p", append=TRUE)
write(pp33, file="an_pp3_p", append=TRUE)

# FULL MODEL SIGNIFICANCE OF PYR !
write(ppy1, file="an_pyr_p", append=TRUE)
write(ppy2, file="an_pyr_p", append=TRUE)
write(ppy3, file="an_pyr_p", append=TRUE)

# FULL MODEL SIGNIFICANCE OF PYR !
write(pra1, file="an_pra_p", append=TRUE)
write(pra2, file="an_pra_p", append=TRUE)
write(pra3, file="an_pra_p", append=TRUE)

#a<-scan("ani",list(f1f2=0, pair=0, bpair=0, anim=""))
#a$anim<-factor(a$anim)
#fit1 <- lm(f1f2 ~ pair + bpair + anim, data=a)
#fit2 <- lm(f1f2 ~ bpair + anim, data=a)
#p1=toString(anova(fit1, fit2)$"Pr(>F)"[2])
#write(p1, file="ares1", append=TRUE)
#fit1 <- lm(f1f2 ~ pair + bpair, data=a)
#fit2 <- lm(f1f2 ~ bpair, data=a)
#anova(fit1, fit2)
#p2=toString(anova(fit1, fit2)$"Pr(>F)"[2])
#write(p2, file="ares2", append=TRUE)
