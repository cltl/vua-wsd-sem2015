#!/bin/bash

here=$(pwd)
mkdir libs
cd libs

####################
#1 ixa-pipes-pos
####################

git clone https://github.com/ixa-ehu/ixa-pipe-pos
cd ixa-pipe-pos/src/main/resources
wget http://ixa2.si.ehu.es/ixa-pipes/models/pos-resources.tgz
tar xvzf pos-resources.tgz
rm pos-resources.tgz
cd ../../../
wget http://ixa2.si.ehu.es/ixa-pipes/models/pos-models-1.3.0.tgz
tar xvzf pos-models*.tgz
model_file=$(ls pos-models-1.3.0/en/en-maxent* | head -1)
path_to_model=$here/libs/ixa-pipe-pos/$model_file
mvn clean package
jar_file=$(ls target/ixa-pipe-pos-*[0-9].jar | head -1)	#this contains target/....
echo "java -jar $here/libs/ixa-pipe-pos/$jar_file tag -m $path_to_model" >> ../../scripts/run_pos.sh
chmod +x ../../scripts/run_pos.sh
cd ..	#back to $here/libs
####################



####################
# It makes sense WSD system
####################
git clone https://github.com/rubenIzquierdo/it_makes_sense_WSD
cd it_makes_sense_WSD
install_ims.sh
ims=$here/libs/it_makes_sense_WSD/call_ims.py
echo "python $ims" >> ../../scripts/run_ims.sh
chmod +x ../../scripts/run_ims.sh
cd .. #back to libs
####################


####################
# DBPEDIA NER
####################
git clone https://github.com/rubenIzquierdo/dbpedia_ner
dbpedia_ner=$here/libs/dbpedia_ner/dbpedia_ner.py
echo "python $dbpedia_ner" >> ../scripts/run_dbpedia_ner.sh
chmod +x ../scripts/run_dbpedia_ner.sh
####################

