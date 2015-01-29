from nltk.corpus import wordnet as wn
from lxml import etree
import glob
from collections import defaultdict
import argparse

#parse user input
parser = argparse.ArgumentParser(description='Add multiwords to output (option to remove single terms in multiwords)')

parser.add_argument('-i', dest='input_folder',   help='full path to naf files with system added',    required=True)
parser.add_argument('-o', dest='semeval_output', help='output file in semeval format'           ,    required=True)
parser.add_argument('-r', dest='remove_single',  help='remove single terms when adding multi words', required=True)

args = parser.parse_args().__dict__    

input_folder   = args["input_folder"]
semeval_output = args["semeval_output"]
remove_single  = args["remove_single"]

def synset_to_senseky(synset,lemma):
    '''
    given an ilidef and a lemma, this method
    returns the wn30 senseky
    
    @requires: nltk (2.0 was used)
    
    @type  synset: nltk.corpus.reader.wordnet.Synset
    @param synset: instance of class nltk.corpus.reader.wordnet.Synset
    
    @type  lemma: str
    @param lemma: lemma (for example "dream")
    '''
    sense_keys = [synset_lemma.key
                  for synset_lemma in synset.lemmas
                  if synset_lemma.key.startswith(lemma+"%")]
    if sense_keys:
        return sense_keys[0]
    else:
        return ""

def loop(input_folder):
    terms_to_not_assign_alone = []
    bigrams = {}
    
    previous             = ""
    identifier_previous  = ""
    
    for input_file in glob.glob("{input_folder}/*".format(input_folder=input_folder)):
        doc = etree.parse(input_file)
        for term_el in doc.iterfind('terms/term'):
            lemma = term_el.get("lemma")
            
            #change this
            try:
                t_id  = term_el.find("externalReferences/externalRef[@resource='semeval']").get("reference")
            except:
                t_id = ""
                lemma = ""
                

            if all([previous,lemma]):
                
                key   = (identifier_previous, t_id) 
                value = "_".join([previous,lemma])
                
                senses = wn.synsets(value)
                if senses:
    
                    terms_to_not_assign_alone.append(identifier_previous)
                    terms_to_not_assign_alone.append(t_id)
                    
                    if senses.__len__() == 1:
                        #put sensekey here
                        sensekey = synset_to_senseky(senses[0], value)
                        if sensekey:
                            bigrams[key] = sensekey
    
            #reset previous and identifier previous
            previous            = lemma
            identifier_previous = t_id
    return bigrams,terms_to_not_assign_alone


bigrams, terms_to_not_assign_alone = loop(input_folder)

with open(semeval_output) as infile:
    lines = infile.readlines()
    
    with open(semeval_output+".multi","w") as outfile:
        for line in lines:
            
            first_identifier = line.strip().split()[0]
            
            #check if line has to be removed from output
            add = all([remove_single == "yes",
                       not any([line.startswith(term) for term in terms_to_not_assign_alone])
                       ])
            if add:
                outfile.write(line)
            
            #check if multiword line has to be added
            check = [ (one,two)          
                      for one,two in bigrams.iterkeys()
                      if first_identifier == one ]

            if check:
                (one,two) = check[0]
                sensekey = bigrams[(one,two)]
                output = "\t".join([one, two, sensekey])
                outfile.write(output+"\n")

