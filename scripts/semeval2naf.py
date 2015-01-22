#!/usr/bin/env python

import time
import argparse
import sys
import os
import cPickle
from lxml import etree

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert a single semeval file into a directory of NAF files.')
    parser.add_argument('-i','--input', dest='input_path', help='path to SemEval input file', required=True)
    parser.add_argument('-o','--output', dest='output_path',help='path to NAF directory', required=True)
    parser.add_argument('-np','--no-pos', dest='pos_enabled',help='path to NAF directory', required=False, action='store_false')
    parser.add_argument('-no_term_layer', dest='term_layer', help='No term layer included', action='store_false')
    
    parser.set_defaults(pos_enabled=True)
    args = parser.parse_args()

    if os.path.exists(args.output_path):
        if len(os.listdir(args.output_path)) > 0:
            print 'Output directory exists and is not empty. Aborted.'
            sys.exit(-1)
    else:
        os.makedirs(args.output_path)
    
    texts_sem = etree.parse(args.input_path).getroot()
    for text_sem in texts_sem:
        mapping_ids = {}
        naf = etree.Element("NAF")
        naf.append(etree.Element('fileDesc', 
                                 attrib={'creationtime':time.strftime('%Y-%m-%d')}))
        raw = etree.Element("raw")
        raw.text = '' 
        naf.append(raw)
        text = etree.Element("text")
        naf.append(text)
        naf.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        naf.set('version','1.0')

        num_wf = 0
        for num_sent, sentence_sem in enumerate(text_sem):
            for wf_sem in sentence_sem:
                if len(raw.text) > 0:
                    raw.text = raw.text + ' '
                offset = len(raw.text)
                raw.text = raw.text + wf_sem.text
                
                this_id = 'w'+str(num_wf+1)
                num_wf += 1
                mapping_ids[wf_sem.attrib['id']] = this_id
                
                wf = etree.Element('wf', 
                                   attrib={'id': this_id,
                                           'offset': str(offset),
                                           'length': str(len(wf_sem.text)),
                                           'sent': str(num_sent+1)},)
                wf.text = wf_sem.text
                text.append(wf)
                
        path = os.path.join(args.output_path, text_sem.attrib['id'] + ".naf")
        with open(path, "wt") as f:
            f.write(etree.tostring(naf, xml_declaration=True, pretty_print=True))    
            print 'Created document',path            
        path_map = os.path.join(args.output_path, text_sem.attrib['id'] + ".map")
        faux = open(path_map,'w')
        cPickle.dump(mapping_ids,faux)
        faux.close()