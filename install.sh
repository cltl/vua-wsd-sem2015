#!/bin/bash

here=$(pwd)

echo "#Created automatically by install script $(date)" > python_scripts/filenames_and_paths.py
echo "wn_type_filename = 'wordnet_types.freq'" >> python_scripts/filenames_and_paths.py
echo "file_dblinks = 'dblinks.list'" >> python_scripts/filenames_and_paths.py

rm -rf scripts 2> /dev/null
mkdir scripts

rm -rf libs 2> /dev/null
mkdir libs
cd libs

#################
# 0 ixa-pipes-tok
#################

git clone https://github.com/ixa-ehu/ixa-pipe-tok
cd ixa-pipe-tok
mvn clean package
jar_file=$(ls target/ixa-pipe-tok-*[0-9].jar | head -1)
echo "java -jar $here/libs/ixa-pipe-tok/$jar_file tok -l en" > ../../scripts/run_tokeniser.sh
chmod +x ../../scripts/run_tokeniser.sh
cd ..
echo "path_tokeniser = '$here/scripts/run_tokeniser.sh'" >> ../python_scripts/filenames_and_paths.py


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
echo "path_pos_tagger = '$here/scripts/run_pos.sh'" >> ../python_scripts/filenames_and_paths.py

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


#########################
# dbpediaEnquirerPy
######################
git clone https://github.com/rubenIzquierdo/dbpediaEnquirerPy
cd dbpediaEnquirerPy
. install_dependencies.sh #Install SPARQLWrapper and downloads dbpedia ontology
cd .. #back to libs
####################


####################
# wikipediaEnquirerPy
####################
git clone https://github.com/rubenIzquierdo/wikipediaEnquirerPy
####################


####################
# KafNafParserPy (requires lxml)
####################
git clone https://github.com/cltl/KafNafParserPy
####################



