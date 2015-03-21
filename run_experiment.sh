
#####
here=$(dirname $(readlink -f $0))
pred_sense=$here/resources/output_predominant_sense/bg.and.entity/yes-n_v-100-5000-predom_and_wordnettype
sys_label="vua_background"
classifier="predom_and_ims"
threshold="0.85"
ims_label="WordNet-3.0"
gold_standard=$here/resources/test_data
suffix=".annotated"
pos_tagger="standard"
only_ours="yes"

#additional paths
path_manual=$here/evaluation/manual_sensekeys.txt


export final_results=$here/evaluation/output_naf
rm -rf $final_results
mkdir -p $final_results
export stats_final_results=$here/evaluation/stats
rm -rf $stats_final_results
mkdir -p $stats_final_results

python predominantsense/scripts/python/add_our_system_to_naf.py -s $suffix -i $gold_standard -p $pos_tagger -b $pred_sense -m $path_manual -c $classifier -l $sys_label -t $threshold -w $ims_label -o $only_ours


#here should be inserted the script to convert to semeval output
python python_scripts/SemevalConverter.py -i $final_results -s $sys_label -o $stats_final_results/semeval_output


#add multiwords and remove single terms in multiwords
#remove pos errors
pos_errors=$here/evaluation/pos_errors.txt
lemma_errors=$here/evaluation/unwanted_lemmas.txt

python evaluation/multiwords.py -i $final_results -o $stats_final_results/semeval_output -r "yes"
python evaluation/remove_pos_errors.py -i $stats_final_results/semeval_output       -e $pos_errors
python evaluation/remove_pos_errors.py -i $stats_final_results/semeval_output.multi -e $pos_errors    
python evaluation/remove_unwanted_lemmas.py -n $final_results -i $stats_final_results/semeval_output.pos -l $lemma_errors
python evaluation/remove_unwanted_lemmas.py -n $final_results -i $stats_final_results/semeval_output.multi.pos -l $lemma_errors

#scorer
cd $here/SemEval-2015-task-13_original_data/scorer

system=$stats_final_results/semeval_output.multi.pos.lemma
gold=$here/SemEval-2015-task-13_original_data/keys/gold_keys/EN/

pwd
for file in $(ls $gold) ;
do
    gold_keys=$gold/$file
    echo $system
    echo
    echo $file
    java Scorer $gold_keys $system
done


