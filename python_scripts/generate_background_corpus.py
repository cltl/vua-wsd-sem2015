#!/usr/bin/env python

import glob
import shutil
import argparse
import sys
import time
import filenames_and_paths

from collections import defaultdict
from subprocess import Popen, PIPE


sys.path.append('./libs')

from KafNafParserPy import *
from dbpediaEnquirerPy import Cdbpedia_enquirer, Cdbpedia_ontology
from wikipediaEnquirerPy.query_wikipedia import *


class Tocurrence:
    def __init__(self,reference=None, document=None,confidence=None,entity_id=None,entity_type=None):
        self.reference = reference
        self.document = document
        self.confidence = confidence
        self.entity_id = entity_id
        self.entity_type = entity_type
    
    def get_reference(self):
        return self.reference
        

def get_all_references(reference_ocurrences, only_leaves=True):
    '''
    This will return all the possible references (with no repetition)
    All possible filters must be here
    '''
    my_dbpedia = Cdbpedia_enquirer()
    my_ontology = Cdbpedia_ontology()
    
    final_references = set()
    for ocurrence in reference_ocurrences:
        if ocurrence.get_reference() not in final_references:
            if only_leaves:
                deepest_onto_label = my_dbpedia.get_deepest_ontology_class_for_dblink(ocurrence.get_reference())
                is_leaf_class = my_ontology.is_leaf_class(deepest_onto_label)
                if is_leaf_class:   # Only the most specific entities according to the ontology
                    final_references.add(ocurrence.get_reference())
                else:
                    print ocurrence.get_reference().encode('utf-8'),'is not a leaf'
            else:
                final_references.add(ocurrence.get_reference())
        
    return list(final_references)
        

def obtain_entities_from_documents(list_of_documents, only_best_option_per_entity=False, extref_resource = None, only_monosemous = False, this_only_leaves = True):
    '''
    Reads a list of NAF documents annotated with entities and references and extracts
    all the references. Returns a list of strings (dblinks)
    '''
    
    #Read all the references
    reference_ocurrences = [] #List of Tocurrence elements
    print 'Obtaining entities:'
    for doc_filename in list_of_documents:
        print '\tDoc:', doc_filename
        in_object = KafNafParser(doc_filename)
        for entity in in_object.get_entities():
            reference_confidence = []
            
            for ext_ref in entity.get_external_references():
                #print ext_ref.get_resource(), extref_resource
                if extref_resource is None or ext_ref.get_resource() == extref_resource:
                    
                    val = ext_ref.get_confidence()
                    if val is not None:
                        val = float(val)
                    else:
                        val = 0.0
                    reference_confidence.append((ext_ref.get_reference(), val))
            reference_confidence.sort(key = lambda t: -t[1])
            #print reference_confidence
            
            if only_monosemous:
                if len(reference_confidence) == 1:
                    ref, conf = reference_confidence[0]
                    new_ocurrence = Tocurrence(reference = ref, document = doc_filename, confidence = conf, entity_id = entity.get_id(), entity_type = entity.get_type())
                    reference_ocurrences.append(new_ocurrence)
            else:
                for ref, conf in reference_confidence:
                    new_ocurrence = Tocurrence(reference = ref, document = doc_filename, confidence = conf, entity_id = entity.get_id(), entity_type = entity.get_type())
                    reference_ocurrences.append(new_ocurrence)
                    if only_best_option_per_entity:
                        break
                    
    # This will read all the ocurrences and will select those that we want to use
    list_references = get_all_references(reference_ocurrences, only_leaves = this_only_leaves)
    return list_references
    
      
def save_to_folder(text,out_folder):
    '''
    Save the text to a file in the output folder with name file_0 file_1 ....
    '''
    num_files = len(glob.glob(out_folder+'/*'))
    filename = "%s/file_%i" % (out_folder,num_files)
    fd = open(filename,'w')
    if isinstance(text,unicode):
        text = text.encode('utf-8')
    fd.write(text)  ##Text is UTF-8
    fd.close()
    return filename
    
    
def save_wordnet_types(out_folder, count_wn_types):
    wn_file = out_folder+'/' + filenames_and_paths.wn_type_filename
    fd = open(wn_file,'w')
    for wn_type, freq in sorted(count_wn_types.items(), key = lambda t: -t[1]):
        fd.write('%s\t%s\n' % (wn_type,freq))
    fd.close()
    
    
    
def create_documents_for_dblinks(dblinks,out_folder):
    '''
    Create background documents for a list of dbpedia links
    '''
    list_files_created = []
    count_wordnet_types = defaultdict(int)
    
    file_dblinks = 'dblinks_file'
    fd_dblinks = open(out_folder+'/'+filenames_and_paths.file_dblinks,'w')
    
    my_dbpedia = Cdbpedia_enquirer()
    my_ontology = Cdbpedia_ontology()
    
    print 'Creating bg documents for dblinks'
    for dblink in dblinks:
        print '\tDblink:',dblink.encode('utf-8')
        deepest_onto_label = my_dbpedia.get_deepest_ontology_class_for_dblink(dblink)
        wikipedia_page_id = my_dbpedia.get_wiki_page_id_for_dblink(dblink)
        if wikipedia_page_id is not None:   #It's empty for instance http://dbpedia.org/resource/Hiromitsu_Endo
            wiki_text = get_plain_text_from_page_id(wikipedia_page_id)  #Using wikipedia library
            wiki_title = my_dbpedia.get_wiki_page_url_for_dblink(dblink)
            if wiki_text is not None:
                new_file = save_to_folder(wiki_text, out_folder)
                list_files_created.append(new_file)
                print '\t\tLen of wiki text:',len(wiki_text)
                print '\t\tDeepest ontolabel', deepest_onto_label
                print '\t\tIs leaf in ontology?',my_ontology.is_leaf_class(deepest_onto_label)
                fd_dblinks.write(dblink+'\t'+wiki_title+'\t'+new_file+'\n')
                
        # Wordnet type
        wordnet_type = my_dbpedia.get_wordnet_type_for_dblink(dblink)
        count_wordnet_types[wordnet_type] += 1
        print '\t\tWordnet type from dbpedia:',wordnet_type
                    
    fd_dblinks.close()
    #Save the wn types in case    
    save_wordnet_types(out_folder,count_wordnet_types)

    print 'Created',len(list_files_created),'documents in',out_folder
    return list_files_created
    

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates a list of files as a background corpus')
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-if','-input_folder',dest='input_folder',help='Input folder with KAF/NAF files with entities and dbpedia links')
    input_group.add_argument('-il','-input_list', type=argparse.FileType('r'), dest='input_list', help = 'Input file with a list of paths to KAF/NAF files (one per line)')
    parser.add_argument('-bd','-best_dblink', dest='only_best_per_entity', action='store_true',help='Only consider the best dbpedia-link for each entity (default is all)')
    parser.add_argument('-of','-output_folder',dest='out_folder',help='Output folder where store all the files')
    parser.add_argument('-naf',dest='naf_output',action='store_true', help='Generate the output in NAF also (tokens+terms)')
    parser.add_argument('-resource', dest='resource', help='External reference resource to be used (default all are used)')
    parser.add_argument('-monosemous', dest = 'only_monosemous', action='store_true', help='Select only monosemous entities')
    parser.add_argument('-all_nodes', dest='all_nodes', action='store_true', help='Use all ontology nodes from dbpedia (default only leaves)')
    
    start_timestamp = time.strftime('%Y-%m-%dT%H:%M:%S%Z')
    args = parser.parse_args()

    if args.out_folder[-1] == '/': args.out_folder = args.out_folder[:-1]
    log_file = open(args.out_folder+'.metadata','w')
    print>>log_file,str(args)
    print>>log_file,'Start:',str(start_timestamp)
    
    ## Read input files
    list_of_documents = []
    if args.input_folder is not None:
        list_of_documents = glob.glob(args.input_folder+'/*')
    elif args.input_list:
        for line in args.input_list:
            list_of_documents.append(line.strip())
        args.input_list.close()
    print>>log_file,'Num docs:',len(list_of_documents)
    
    # The outputfolder is removed if it exists
    if os.path.exists(args.out_folder):
        shutil.rmtree(args.out_folder)
    os.mkdir(args.out_folder)
    
    
    # A list of dblinks is obtained by reading all the input documents and doing some agglomeration
    list_references = obtain_entities_from_documents(list_of_documents, only_best_option_per_entity = args.only_best_per_entity, extref_resource=args.resource, only_monosemous=args.only_monosemous,
                                                     this_only_leaves = (not args.all_nodes))
    print>>log_file,'Num references (dblink):',len(list_references)
    
    # For each link we create a set of documents stored in args.out_folder
    out_documents = create_documents_for_dblinks(list_references,args.out_folder)
    print>>log_file,'Num output docs:',len(out_documents)
    print>>log_file,'Frequency of wordnet types at:',args.out_folder+'/'+filenames_and_paths.wn_type_filename
    print>>log_file,'File with dblinks and files:', args.out_folder+'/'+filenames_and_paths.file_dblinks
 
    
    if args.naf_output:
        apply_naf_pipeline(out_documents)
        
        
    end_timestamp = time.strftime('%Y-%m-%dT%H:%M:%S%Z')
    print>>log_file,'End:',str(end_timestamp)
    log_file.close()
    print 
    print 'END'
    print '\tStart:', start_timestamp
    print '\tEnd:', end_timestamp
    print 
    print 'See log at:',log_file.name
    
    
        

    
