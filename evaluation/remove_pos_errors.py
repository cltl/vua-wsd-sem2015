import argparse

#parse user input
parser = argparse.ArgumentParser(description='Remove identifiers which have pos erros according to us')

parser.add_argument('-i', dest='input_file',  help='semeval output file',     required=True)
parser.add_argument('-e', dest='pos_errors',  help='file with pos erros',    required=True)

args = parser.parse_args().__dict__    

input_file  = args["input_file"]
pos_errors  = args["pos_errors"]

wrong_identifiers = [line.strip() for line in open(pos_errors)]

with open(input_file+".pos","w") as outfile:
    with open(input_file) as infile:
        for line in infile:
            outwrite = True
             
            if any([identifier in line
                    for identifier in wrong_identifiers]):
                outwrite = False
            
            if outwrite:
                outfile.write(line)

