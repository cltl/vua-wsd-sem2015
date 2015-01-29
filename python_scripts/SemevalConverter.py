from nltk.corpus import wordnet as wn
from glob import glob
from lxml import etree
import argparse

class SemevalConverter():
    '''
    this class converts the sense output (and perhaps later on entity output
    to the output format of semeval. The ilidefs will be converted into
    sensekeys.
    
    @requires: glob
    @requires: lxml (I used lxml.etree '3.3.5')
    @requires: nltk (I used 3.0)
    @requires: argparse
    
    @type  input_folder: str
    @param input_folder: full path to folder in which naf files are stored
    ( *.naf will be used in this folder)
    
    @type  system_label: str
    @param system_label: label of system
    
    @type  output_path: str
    @param output_path: full path to output path
    
    @type system_label: str
    @ivar system_label: label of system
    '''
    def __init__(self,input_folder, system_label, output_path):
        #make param system_label ivar
        self.system_label = system_label
        
        self.loop(input_folder, output_path)
    
    def obtain_highest_ilidef(self, ext_refs_el):
        '''
        given an externalReferences lxml element,
        this method returns the ilidef with the highest confidence given
        the ivar system_label. In addition, the original identifier in the task
        is found.
        
        @type  ext_refs_el: lxml.etree._Element
        @param ext_refs_el: externalReferences element in naf file
        
        @rtype: tuple
        @return: (ilidef (empty string if not found), identifier)
        '''
        #original identifier
        ext_ref_el_with_semeval_attrib = ext_refs_el.find("externalRef[@resource='semeval']")
        if ext_ref_el_with_semeval_attrib == None:
            #print 
            #print etree.tostring(ext_refs_el)
            return ("","")
        else:
            identifier = ext_ref_el_with_semeval_attrib.get('reference')

        #find highest ilidef given ivar system_label
        system = [(float(el.get("confidence")),el.get("reference"))
                  for el in ext_refs_el.iterfind("externalRef[@resource='{system_label}']".format(system_label=self.system_label))]
        
        if system:
            return (sorted(system, reverse=True)[0][1], identifier)
        else:
            return ("",identifier)
        
    def ilidef_to_sensekey(self,ilidef,lemma):
        '''
        given an ilidef and a lemma, this method
        returns the wn30 senseky
        
        @requires: nltk (3.0 was used)
        
        @type  ilidef: str
        @param ilidef: wn30 ilidef (for example "ili-30-05768553-n")
        
        @type  lemma: str
        @param lemma: lemma (for example "dream")
        '''
        ili,version,offset,pos = ilidef.split('-')
        synset                 = wn._synset_from_pos_and_offset(pos,int(offset))
        sense_keys = [synset_lemma.key
                      for synset_lemma in synset.lemmas
                      if synset_lemma.key.startswith(lemma+"%")]
        if sense_keys:
            return sense_keys[0]
        else:
            return ""
    
    def loop(self,input_folder, output_path):
        '''
        for each externalReferences in the naf, the ilidef
        with the highest confidence is converted into a wn sensekey
        and written to param output_path
        
        @type  input_folder: str
        @param input_folder: full path to folder in which naf files are stored
        ( *.naf will be used in this folder)
    
        @type  output_path: str
        @param output_path: full path to output path
        '''
        #set xml path to external references element
        path_to_ext_refs_el = "terms/term/externalReferences"
        
        #open param output_path and loop naf files
        with open(output_path, "w") as outfile:
            for naf_file in glob("{input_folder}/*".format(input_folder=input_folder)):
                
                #parse file with etree.parse
                doc = etree.parse(naf_file)
                            
                #find ext_refs el
                for ext_refs_el in doc.iterfind(path_to_ext_refs_el):
                    wn30_sensekey     = ""
                    lemma              = ext_refs_el.getparent().get("lemma")
                    ilidef, identifier = self.obtain_highest_ilidef(ext_refs_el)
                    
                    if ilidef:
                        wn30_sensekey  = self.ilidef_to_sensekey(ilidef, lemma)
                    
                    if wn30_sensekey:
                        outfile.write("\t".join([identifier,
                                                identifier,
                                                #try without wn:
                                                wn30_sensekey])+"\n")
                        
if __name__ == "__main__":
    #parse user input
    parser = argparse.ArgumentParser(description='Convert vua-background to semeval output format')
    
    parser.add_argument('-i', dest='input_folder', help='full path to folder in which naf files are stored', required=True)
    parser.add_argument('-s', dest='system_label', help='system label',                                      required=True)
    parser.add_argument('-o', dest='output_path' , help='full path to output path',                          required=True)

    args = parser.parse_args().__dict__    
    
    input_folder = args["input_folder"]
    system_label = args["system_label"]
    output_path  = args["output_path"]

    SemevalConverter(input_folder, 
                     system_label, 
                     output_path)
    
