import argparse
import glob
from lxml import etree

#parse user input
parser = argparse.ArgumentParser(description='remove identifiers with wrong pos according to us')

parser.add_argument('-n', dest='naf_files',  help='naf files with system add', required=True)
parser.add_argument('-i', dest="semeval",    help='output file semeval',       required=True)
parser.add_argument('-l', dest='lemma_file', help='file with lemma erros',     required=True)

args = parser.parse_args().__dict__    

input_folder  = args["naf_files"]
semeval       = args['semeval']
lemma_file    = args["lemma_file"]

wrong_lemmas = [line.strip() for line in open(lemma_file)]

#obtain identifiers
wrong_identifiers = []
for input_file in glob.glob("{input_folder}/*".format(input_folder=input_folder)):
    doc = etree.parse(input_file)
    for term_el in doc.iterfind('terms/term'):
        lemma = term_el.get("lemma")
        if lemma in wrong_lemmas:
            try:
                identifier = term_el.find("externalReferences/externalRef[@resource='semeval']").get("reference")
                wrong_identifiers.append(identifier)
            except:
                pass


with open(semeval+".lemma","w") as outfile:
    with open(semeval) as infile:
        for line in infile:
            outwrite = True
             
            if any([identifier in line
                    for identifier in wrong_identifiers]):
                outwrite = False
            
            if outwrite:
                outfile.write(line)

