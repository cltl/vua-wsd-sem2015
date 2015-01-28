#!/usr/bin/env python

##############################################
# Author:   Ruben Izquierdo Bevia            # 
#           VU University of Amsterdam       #
# Mail:     ruben.izquierdobevia@vu.nl       #
#           rubensanvi@gmail.com             #
# Webpage:  http://rubenizquierdobevia.com   #
# Version:  1.0                              #
# Modified: 26-jan-2015                      #
##############################################

import filenames_and_paths
import time
import argparse
import sys
import os
import shutil
import glob
import hashlib
import filenames_and_paths

sys.path.append('./libs')
from collections import defaultdict
from dbpediaEnquirerPy import Cdbpedia_ontology, Cdbpedia_enquirer
from wikipediaEnquirerPy.query_wikipedia import *
from subprocess import Popen, PIPE
import time
import argparse


def apply_naf_pipeline(out_docs):
    '''
    Calls to tokeniser + posTagger to create NAF file also
    '''
    print 'Converting files to NAF (tokeniser+pos-tagger)'
    for doc in out_docs:
        print '\tDocument:', doc,'...'
        fin = open(doc,'r')
        fout = open(doc+'.naf','w')
        tokeniser =  Popen(filenames_and_paths.path_tokeniser+' en',stdout = PIPE, stdin = fin,              stderr = PIPE, shell = True)
        lemmatiser = Popen(filenames_and_paths.path_pos_tagger,     stdout = fout, stdin = tokeniser.stdout, stderr = PIPE, shell = True)
        tokeniser.terminate()
        lemmatiser.wait()
        fin.close()
        fout.close()
        print '\t\tNAF:',fout.name
        sys.stdout.flush()



def save_text_to_folder(out_folder, this_text):
    n = len(glob.glob(out_folder+'/*'))
    new_file = out_folder+'/file_'+str(n)
    fd = open(new_file,'w')
    if isinstance(this_text,unicode):
        this_text = this_text.encode('utf-8')
    fd.write(this_text)
    fd.close()
    return fd.name
    
    

def corpus_expansion_entities(in_folder, out_folder, min_matches):
    #Read the list of dblinks, wikientities and text files created for each
    print time.strftime('%H:%M:%S'),'==> Reading the input file from', in_folder+'/'+filenames_and_paths.file_dblinks
    seed_wiki_entities = set()
    fd = open(in_folder+'/'+filenames_and_paths.file_dblinks)
    for line in fd:
        fields = line.strip().split()       #http://dbpedia.org/resource/Caesium_chloride    http://en.wikipedia.org/wiki/Caesium_chloride    data/bg_corpus/file_9
        large_url = fields[1]
        wiki_title = large_url.split('/')[-1]
        seed_wiki_entities.add(wiki_title)
    fd.close()
    #####

    my_out_folder = out_folder
    if my_out_folder[-1]=='/':
        my_out_folder = my_out_folder[:-1]
    fd_log = open(my_out_folder+'.log','w')
    
    
    out_documents = []
   
   
    for wiki_entity in list(seed_wiki_entities):
        # Get all wikipedia links for this wiki_entity
        print time.strftime('%H:%M:%S'),'==> Expanding ',wiki_entity
        fd_log.write('Seed: %s\n' % wiki_entity)
        #call to query_wikipedia ['William_Denison','World_War_I','Wikipedia:Verifiability'...]
        # we get all the links in each wikipedia seed

        try:
            all_wiki_links = get_all_links_from_page_title(wiki_entity)
        except Exception as e:
            print>>sys.stderr,'Exception querying wikipedia for', wiki_entity,'Skipped'
            print>>sys.stderr,str(e)
            continue
             
        fd_log.write('\tTotal links: %d\n' % len(all_wiki_links))
        #We decide if include depending how many entities are shared with our original corpus (or could be with the original seed)
        for possible_wiki_link in all_wiki_links:
            possible_wiki_link = possible_wiki_link.encode('utf-8')
            print '\tChecking sublink', possible_wiki_link, '(found in the seed wiki'+wiki_entity+')'
            try:
                all_links_for_possible = get_all_links_from_page_title(possible_wiki_link)  #This is the whole list of entities of the possible sublink
            except Exception as e:
                print>>sys.stderr,'Exception querying wikipedia for', wiki_entity,'Skipped'
                print>>sys.stderr,str(e)
                continue
            
            #Count how many in common are with the original corpus
            which_in_common = set(all_links_for_possible) & seed_wiki_entities
            print '\t\tIn common with the whole original seed list:', len(which_in_common)
            for w in which_in_common:
                print '\t\t\t',w
            if len(which_in_common) >= min_matches:
                print '\t\tSAVED to output'
                text = get_plain_text_from_title(possible_wiki_link)
                new_filename = save_text_to_folder(out_folder, text)
                out_documents.append(new_filename)
                print 'TEXT:',len(text),text[:100].encode('utf-8')
                fd_log.write('\tAdded: %s\t\tFile %s\n' %(possible_wiki_link,new_filename))
                for w in which_in_common:
                    fd_log.write('\t\t\tIn common: %s\n' % w)
            else:
                print '\t\tDiscarded'
    fd_log.close()
    print time.strftime('%H:%M:%S'),'==> Log at ',fd_log.name
    return out_documents

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates a background corpus from DBpedia and Wikipedia using a set of dbpedia links and wikipedia links to entities')
    parser.add_argument('-i', dest='in_folder', help='Input folder (result of the generate_background_corpus.py script)', required = True)
    parser.add_argument('-o', dest='out_folder', help='Output folder where store the new files', required = True)
    parser.add_argument('-m', dest='min_matches', type=int, help='Minimum number of entities matched to be selected', required = True)
    parser.add_argument('-keep', dest='keep_out', action='store_true', help='Keep the output folder if exists (by default it will be removed)')
    parser.add_argument('-naf',dest='naf_output',action='store_true', help='Generate the output in NAF also (tokens+terms)')

    args = parser.parse_args()

    if os.path.exists(args.out_folder):
        if args.keep_out:
            pass 
        else:
            shutil.rmtree(args.out_folder)
            os.mkdir(args.out_folder)
    else:
        os.mkdir(args.out_folder)
    
    print 'Arguments:', str(args)
    out_documents = corpus_expansion_entities(args.in_folder, args.out_folder, args.min_matches)
    
    if args.naf_output:
        apply_naf_pipeline(out_documents)
    print time.strftime('%H:%M:%S'),'==> ALL DONE'
