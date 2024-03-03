#Blood pressure control among people with hypertension
require(data.table)
require(magrittr)
patients<- read.csv("materials/patients.csv",
                    as.is = T) %>% 
  setDT()
# drug availability
facilities<- read.csv("materials/facilities.csv",
                      as.is = T) %>% 
  setDT()

#intial visit
initialvisit<- read.csv("materials/htn_initial_visits.csv",
                        as.is=T) %>% 
  setDT()


followupvisit<- read.csv("materials/htn_follow_up_visits.csv",
                         as.is=T) %>% 
  setDT()


initialvisit[, sbp.folloup:=NA_real_]
initialvisit[, sbp.folloup:=apply(.SD,
                                  1L,
                                  function(x){
                                    retv<-   followupvisit[patient_id ==x, sbp]
                                    if(length(retv)>1){
                                      browser()
                                    } else if(length(retv)==0){
                                      return(NA_real_)
                                    }else{
                                      return(retv)
                                    }
                                    
                                  }), .SDcols = 'patient_id']


initialvisit[, dbp.folloup:=apply(.SD,
                                  1L,
                                  function(x){
                                    retv<-   followupvisit[patient_id ==x, dbp ]
                                    if(length(retv)>1){
                                      browser()
                                    } else if(length(retv)==0){
                                      return(NA_real_)
                                    }else{
                                      return(retv)
                                    }
                                  }), .SDcols = 'patient_id']

initialvisit[, facility_id:=apply(.SD,
                                  1L,
                                  function(x){
                                    retv<-   patients[patient_id ==x, facility_id ]
                                    if(length(retv)>1){
                                      browser()
                                    } else if(length(retv)==0){
                                      return(NA_character_)
                                    }else{
                                      return(retv)
                                    }
                                  }), .SDcols = 'patient_id']



initialvisit[, sex:=apply(.SD,
                          1L,
                          function(x){
                            retv<-   patients[patient_id ==x, gender]
                            if(length(retv)>1){
                              browser()
                            } else if(length(retv)==0){
                              return(NA_character_)
                            }else{
                              return(retv)
                            }
                          }), .SDcols = 'patient_id']




initialvisit[, facilityName:=apply(.SD,
                                   1L,
                                   function(x){
                                     retv<-   facilities[facility_id  ==x,
                                                         facility] %>% unique()
                                     if(length(retv)>1){
                                       browser()
                                     } else if(length(retv)==0){
                                       return(NA_character_)
                                     }else{
                                       return(retv)
                                     }
                                   }), .SDcols = 'facility_id']


initialvisit[, district :=apply(.SD,
                                1L,
                                function(x){
                                  retv<-   facilities[facility_id  ==x, district ] %>% unique()
                                  if(length(retv)>1){
                                    browser()
                                  } else if(length(retv)==0){
                                    return(NA_character_)
                                  }else{
                                    return(retv)
                                  }
                                }), .SDcols = 'facility_id']


initialvisit[, province  :=apply(.SD,
                                 1L, 
                                 function(x){
                                   retv<-   facilities[facility_id  ==x, province  ] %>% 
                                     unique()
                                   if(length(retv)>1){
                                     browser()
                                   } else if(length(retv)==0){
                                     return(NA_character_)
                                   }else{
                                     return(retv)
                                   }
                                 }), .SDcols = 'facility_id']


initialvisit[, country  :=apply(.SD,
                                1L,
                                function(x){
                                  retv<-   facilities[facility_id  ==x, country] %>% unique()
                                  if(length(retv)>1){
                                    browser()
                                  } else if(length(retv)==0){
                                    return(NA_character_)
                                  }else{
                                    return(retv)
                                  }
                                }), .SDcols = 'facility_id']

#Criteria 1: Systolic blood pressure (SBP) <140 mmHg and diastolic blood pressure (DBP) <90 mmHg
initialvisit[, key:=.I]
initialvisit[, bpcontrolled.measurements:=NA]
initialvisit[!is.na(sbp.folloup) &
               !is.na(dbp.folloup), bpcontrolled.measurements:=F, by=key]
#use folloup
initialvisit[ sbp.folloup<140 & dbp.folloup<90
              ,bpcontrolled.measurements:=T
              , by=key]

initialvisit[is.na(bpcontrolled.measurements) & !is.na(sbp) &
               !is.na(dbp), bpcontrolled.measurements:=F, by=key]

initialvisit[is.na(bpcontrolled.measurements) &
               sbp<140 & dbp<90
             ,bpcontrolled.measurements:=T
             , by=key]


# citeria 2: SBP <130 mmHg among people with history of CVD

initialvisit[, cvdHistory:=apply(.SD,
                                 1L,
                                 function(x){
                                   retv<-   followupvisit[patient_id==x,
                                                          cvd_diagnosis   ] %>% unique()
                                   if(length(retv)>1){
                                     browser()
                                   } else if(length(retv)==0){
                                     return(NA_character_)
                                   }else{
                                     return(retv)
                                   }
                                 }), .SDcols = 'patient_id']


initialvisit[, bpcontrolled.cvd:=NA]
initialvisit[!is.na(sbp) & !is.na(cvdHistory),
             bpcontrolled.cvd:=F, by=key]

initialvisit[!bpcontrolled.cvd &
               sbp<130 & cvdHistory=="Yes",
             bpcontrolled.cvd:=T, by=key]


# criteria 3: SBP <130 mmHg among high-risk people with hypertension, i.e., those with high CVD risk, diabetes mellitus, chronic kidney disease (CKD)


initialvisit[, cvd_high_risk:=apply(.SD,
                                    1L,
                                    function(x){
                                      retv<-   followupvisit[patient_id ==x, cvd_high_risk ]
                                      if(length(retv)>1){
                                        browser()
                                      } else if(length(retv)==0){
                                        return(NA_character_)
                                      }else{
                                        return(retv)
                                      }
                                    }), .SDcols = 'patient_id']


initialvisit[, diabetes:=apply(.SD,
                               1L,
                               function(x){
                                 retv<-   followupvisit[patient_id ==x, diabetes ]
                                 if(length(retv)>1){
                                   browser()
                                 } else if(length(retv)==0){
                                   return(NA_character_)
                                 }else{
                                   return(retv)
                                 }
                               }), .SDcols = 'patient_id']


initialvisit[, ckd_diagnosis:=apply(.SD,
                                    1L,
                                    function(x){
                                      retv<-   followupvisit[patient_id ==x, ckd_diagnosis ]
                                      if(length(retv)>1){
                                        browser()
                                      } else if(length(retv)==0){
                                        return(NA_character_)
                                      }else{
                                        return(retv)
                                      }
                                    }), .SDcols = 'patient_id']


initialvisit[, hphighrisk:=NA]
initialvisit[!is.na(cvd_high_risk) &
               !is.na(diabetes) &
               !is.na(ckd_diagnosis),
             hphighrisk:=F,
             by=key]

initialvisit[sbp.folloup<130 & (
  cvd_high_risk=="Yes" 
  | diabetes=="True" 
  | ckd_diagnosis =="Yes"
),
hphighrisk:=T,
by=key]


initialvisit[is.na(sbp.folloup) & hphighrisk!=T & sbp<130 & (
  cvd_high_risk=="Yes" 
  | diabetes=="True" 
  | ckd_diagnosis =="Yes"
), hphighrisk:=T,
by=key]

initialvisit[, lastClinicalVisit.date:=apply(.SD
                                             , 1L,
                                             function(x){
                                               retv<-   followupvisit[patient_id ==x, visit_date]
                                               if(length(retv)>1){
                                                 browser()
                                               } else if(length(retv)==0){
                                                 return(NA_character_)
                                               }else{
                                                 return(retv)
                                               }
                                             }), .SDcols = 'patient_id']


initialvisit[, bloodPressureControlled:=F]
initialvisit[bpcontrolled.measurements |
               bpcontrolled.cvd|
               hphighrisk, bloodPressureControlled:=T, by=key]

# last date of vist: initial visit if now folloup exist
initialvisit[is.na(lastClinicalVisit.date),
             lastClinicalVisit.date:=visit_date,
             by=key]

initialvisit[, sex:=as.factor(sex)]
initialvisit[, cvd_high_risk:=as.factor(cvd_high_risk) ]

datatoUseC4<- copy(initialvisit)
# datatoUseC4<- copy(initialvisit[!is.na(lastClinicalVisit.date) &
#                                   as.Date(lastClinicalVisit.date,
#                                           "%Y-%m-%d")==as.Date("2022-12-31",  "%Y-%m-%d"),  ])


datatoUseC4[,denominator:=T]

# by porvince 
tapply(datatoUseC4[, bloodPressureControlled],
       datatoUseC4[, province], function(x){
         table(x) %>% 
           prop.table() %>%
           multiply_by(100)
       })


# by porvince 
tapply(datatoUseC4[, bloodPressureControlled],
       datatoUseC4[, district], 
       function(x){
         table(x) %>% 
           prop.table() %>%
           multiply_by(100)
       })



# by state 
tapply(datatoUseC4[, bloodPressureControlled],
       datatoUseC4[,country],
       function(x){
         table(x) %>% 
           prop.table() %>% 
           multiply_by(100)
       })


tapply(datatoUseC4[, bloodPressureControlled],
       datatoUseC4[,facilityName], 
       function(x){
         retv<- table(x) %>% 
           prop.table() %>%
           multiply_by(100)
       })

updated.ds<- data.table()
split(datatoUseC4,
      datatoUseC4$district) %>% 
  lapply(
    function(district){
      split(district,
            district$facilityName) %>% 
        lapply(function(facid){
          
          returned<- tapply(facid$bloodPressureControlled, 
                            facid$sex, function(xx){
                              ret<- table(xx) %>% prop.table() %>%
                                multiply_by(100) %>% round(2)
                              ret<- ret["TRUE"]
                              ifelse(is.na(ret), 0, ret)
                            })
          
          riskgroup<- tapply(facid$bloodPressureControlled, 
                             facid$cvd_high_risk ,
                             function(xx){
                               ret<- table(xx) %>%
                                 prop.table() %>%
                                 multiply_by(100) %>%
                                 round(2)
                               ret<- ret["TRUE"]
                               ifelse(is.na(ret), 0, ret)
                             })
          
          returnedDs<- data.table(District=unique(facid$district), 
                                  Facility=unique(facid$facilityName),
                                  Female=returned[["Female"]],
                                  Male=returned[["Male"]],
                                  HighRisk=riskgroup[["Yes"]],
                                  LowRisk=riskgroup[["No"]]
          )
          updated.ds<<- rbindlist(list(returnedDs,updated.ds),
                                  use.names=T,
                                  fill=T)
          
        })
    })



avg.fun<- function(...){
  median(as.numeric(...), na.rm = T)
}

vls_to_avg <- c(
  'Female',
  'Male',
  'HighRisk',
  'LowRisk'
)

