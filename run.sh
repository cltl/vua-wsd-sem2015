#!/bin/bash

##############################################
# Author:   Ruben Izquierdo Bevia            # 
#           VU University of Amsterdam       #
# Mail:     ruben.izquierdobevia@vu.nl       #
#           rubensanvi@gmail.com             #
# Webpage:  http://rubenizquierdobevia.com   #
# Version:  1.0                              #
# Modified: 26-jan-2015                      #
##############################################

here=$(pwd)

##########################
#1) Convert to NAF
##########################
python $here/python_scripts/semeval2naf.py -i $here/SemEval-2015-task-13_original_data/data/semeval-2015-task-13-en.xml -o $here/data/data_en_naf
##########################



##########################
#2) Call to the pos-tagger
##########################
for file in $here/data/data_en_naf/*.naf
do
  folder=$(dirname $file)
  basename=$(basename $file)
  outfile=$folder/${basename::-4}.pos.naf
  cat $file | $here/scripts/run_pos.sh > $outfile 2> $outfile.err
  echo Created $outfile
done
##########################



##########################
#3) Call to the IMS
##########################
for file in $here/data/data_en_naf/*.pos.naf
do
  folder=$(dirname $file)
  basename=$(basename $file)
  outfile=$folder/${basename::-4}.ims.naf
  cat $file | $here/scripts/run_ims.sh > $outfile 2> $outfile.err
  echo Created $outfile
done
##########################



##########################
#4) Call to dbpedia ner
##########################
my_list=$here/data/my_list_naf.txt
for file in $here/data/data_en_naf/*.pos.ims.naf
do
  folder=$(dirname $file)
  basename=$(basename $file)
  outfile=$folder/${basename::-4}.ner.naf
  cat $file | $here/scripts/run_dbpedia_ner.sh > $outfile 2> $outfile.err
  echo Created $outfile
  echo $outfile >> $my_list
done
##########################



########################## 
#5) Generate the background corpus
##########################
out_folder=$here/background_corpus
rm -rf $out_folder 2> /dev/null		#The output folder is removed
python python_scripts/generate_background_corpus.py -il $my_list -of $out_folder -bd -naf -all_nodes
##########################



##########################
# 6) Generate the entity overlapping extended corpus
##########################
in_folder=$out_folder
out_folder=$here/entity_expanded_corpus
min_matches=5
python python_scripts/corpus_expansion_entities.py -i $in_folder -o $out_folder -m $min_matches -naf
##########################

##########################
# (7) run predominant sense algorithm
##########################
cd $here/predominantsense
bash predominant_sense.sh 'yes' 'n_v' '100' '5000' 'no' 'yes' $here/entity_expanded_corpus
##########################


