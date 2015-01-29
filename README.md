# vua-wsd-sem2015
System for the CLTL participation in SemEval2015 task 13: multilingual all-words sense disambiguation and entity linking.


##Installation

You will need just to clone the repository and run the `instal.sh` script, which will automatically download and install:

* ixa-pipe-pos: pos-tagger developed by the IXA group of the basque country (https://github.com/ixa-ehu/ixa-pipe-pos)
* It Makes Sense (IMS): wrapper around the IMS system for WSD to allow the use of NAF files (https://github.com/rubenIzquierdo/it_makes_sense_WSD)
* dbpedia_ner: wrapper around the dbpedia spotlight NER and NED for working with NAF files (https://github.com/rubenIzquierdo/dbpedia_ner)
* predominantsense: wrapper around predominant sense algorithm (https://bitbucket.org/MartenPostma/predominantsense)

The version of the IMS system only works with java 1.6, so make sure you are using that version, you can check with `java -version`. If you are
using any other version, you will need to modify the file `libs/it_makes_sense_WSD/ims/testPlain.sh` and set the `java` command to the exact
java1.6 binary.
```shell
Change:
java -mx2500m -cp $CLASSPATH sg.edu.
by:
/usr/lib/jvm/java-1.6.0-openjdk-amd64/bin/java -mx2500m -cp $CLASSPATH sg.edu.....
```

So basically these are the the only steps required:
```shell
git clone https://github.com/cltl/vua-wsd-sem2015
cd vua-wsd-sem2015
install.sh
```

##Usage

To run the whole system, you will need to call to the script `run.sh`. This script will automatically call to all the modules
in our pipeline for processing the original SemEval2015 files that can be found at the folder `SemEval-2015-task-13_original_data`.
It will create a new folder `data_en_naf`, where all the NAF files created will be stored. Different files with different suffixes
represent intermediate results of the whole pipeline. After running `run.sh`, 'run_experiment.sh' will run the experiment. The output can be found in evaluation/stats.

##Contact

* Ruben Izquierdo Bevia
  * ruben.izquierdobevia@vu.nl
  * http://rubenizquierdobevia.com/
  * Vrije University of Amsterdam
* Marten Postma
  * m.c.postma@vu.nl
  * Vrije University of Amsterdam

##License
Sofware distributed under GPL.v3, see LICENSE file for details.

