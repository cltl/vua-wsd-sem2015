#!/bin/bash

here=$(pwd)


#1) Convert to NAF
python $here/scripts/semeval2naf.py -i $here/SemEval-2015-task-13_original_data/data/semeval-2015-task-13-en.xml -o $here/data/data_en_naf


#2) Call to the pos-tagger
for file in $here/data/data_en_naf/*.naf
do
  folder=$(dirname $file)
  basename=$(basename $file)
  outfile=$folder/${basename::-4}.pos.naf
  cat $file | $here/scripts/run_pos.sh > $outfile 2> $outfile.err
  echo Created $outfile
done


#3) Call to the IMS
for file in $here/data/data_en_naf/*.pos.naf
do
  folder=$(dirname $file)
  basename=$(basename $file)
  outfile=$folder/${basename::-4}.ims.naf
  cat $file | $here/scripts/run_ims.sh > $outfile 2> $outfile.err
  echo Created $outfile
done

#4) Call to dbpedia ner
for file in $here/data/data_en_naf/*.pos.ims.naf
do
  folder=$(dirname $file)
  basename=$(basename $file)
  outfile=$folder/${basename::-4}.ner.naf
  cat $file | $here/scripts/run_dbpedia_ner.sh > $outfile 2> $outfile.err
  echo Created $outfile
done
 