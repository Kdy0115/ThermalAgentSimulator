library("OpenImageR")
library(Thermimage)
library(data.table)

print("start R program")
te<-function(p0,p1,Z){

  reave<-NULL
  for(i in 1:length(p0))
    reave[i]<-format(round(Z[p0[i], p1[i]],digits = 1),nsmall=1)

  return(reave)
}

f<-list()
#for(i in 0:images_length - 1){
#  f<-paste0(system.file(paste("extdata/",paste(images_path+i)), package="Thermimage"))
#}

f<-paste0(system.file("extdata/D (1).jpg", package="Thermimage"))
f<-c(f,paste0(system.file("extdata/D (2).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (3).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (4).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (5).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (7).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (8).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (9).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (10).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (11).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (12).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (13).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (14).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (15).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (16).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (17).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (18).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (19).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (20).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (21).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (22).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (23).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (24).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (25).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (26).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (27).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (28).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (29).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (30).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (31).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (32).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (33).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (34).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (35).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (36).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (37).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (38).jpg", package="Thermimage")))
f<-c(f,paste0(system.file("extdata/D (39).jpg", package="Thermimage")))

#<-paste0(system.file("extdata/data/thermo_img/get_heat_source/D (1).jpg", package="Thermimage"))
#f<-c(f,paste0(system.file("extdata/data/thermo_img/get_heat_source/D (2).jpg", package="Thermimage")))
#f<-c(f,paste0(system.file("extdata/data/thermo_img/get_heat_source/D (3).jpg", package="Thermimage")))
#f<-c(f,paste0(system.file("extdata/data/thermo_img/get_heat_source/D (4).jpg", package="Thermimage")))
#f<-c(f,paste0(system.file("extdata/data/thermo_img/get_heat_source/D (5).jpg", package="Thermimage")))
#f<-c(f,paste0(system.file("extdata/data/thermo_img/get_heat_source/D (6).jpg", package="Thermimage")))
#f<-c(f,paste0(system.file("extdata/data/thermo_img/get_heat_source/D (7).jpg", package="Thermimage")))
#f<-c(f,paste0(system.file("extdata/data/thermo_img/get_heat_source/D (8).jpg", package="Thermimage")))
#f<-c(f,paste0(system.file("extdata/data/thermo_img/get_heat_source/D (9).jpg", package="Thermimage")))



result_csv<-matrix(0,length(point_picnum),5)
colnames(result_csv)<-c("x","y","z","temp","size")



for(i in 1:length(point_picnum)){
  for(k in 1:images_length){
    if(point_picnum[i]==k-1){
      img<-readflirJPG(f[k], exiftoolpath="installed")
    }
  }


  cams<-flirsettings(f, exiftoolpath="installed", camvals="")
  head(cbind(cams$Info), 20)

  ObjectEmissivity<- cams$Info$Emissivity
  dateOriginal<-cams$Dates$DateTimeOriginal
  dateModif<- cams$Dates$FileModificationDateTime
  PlanckR1<- cams$Info$PlanckR1
  PlanckB<- cams$Info$PlanckB
  PlanckF<- cams$Info$PlanckF
  PlanckO<- cams$Info$PlanckO
  PlanckR2<- cams$Info$PlanckR2
  ATA1<- cams$Info$AtmosphericTransAlpha1
  ATA2<- cams$Info$AtmosphericTransAlpha2
  ATB1<- cams$Info$AtmosphericTransBeta1
  ATB2<- cams$Info$AtmosphericTransBeta2
  ATX<- cams$Info$AtmosphericTransX
  OD<- cams$Info$ObjectDistance
  FD<- cams$Info$FocusDistance
  ReflT<- cams$Info$ReflectedApparentTemperature
  AtmosT<- cams$Info$AtmosphericTemperature
  IRWinT<- cams$Info$IRWindowTemperature
  IRWinTran<- cams$Info$IRWindowTransmission
  RH<- cams$Info$RelativeHumidity
  h<- cams$Info$RawThermalImageHeight
  w<- cams$Info$RawThermalImageWidth

  temperature<-raw2temp(img, ObjectEmissivity, OD, ReflT, AtmosT, IRWinT, IRWinTran, RH, PlanckR1, PlanckB, PlanckF, PlanckO, PlanckR2, ATA1, ATA2, ATB1, ATB2, ATX)
  str(temperature)

  result<-te(point_pich[i],point_picw[i],temperature)

  
  result_csv[i,1]<-point_originx[i]
  result_csv[i,2]<-point_originy[i]
  result_csv[i,3]<-point_originz[i]
  result_csv[i,4]<-result
  result_csv[i,5]<-size[i]
  
}

print(result_csv)

write.csv(3,'controllers/temp_search/result.csv')
result_csv<-data.frame(result_csv)
#write.csv(result_csv,"controllers/temp_search/result.csv")
