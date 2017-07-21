# The table extractor - GSoC 2017 project 

## Abstract
 _Wikipedia is full of data hidden in tables. The aim of this project is to explore the possibilities of exploiting all the data represented with the appearance of tables in Wiki pages, in order to populate the different chapters of DBpedia through new data of interest. The Table Extractor has to be the engine of this data “revolution”: it would achieve the final purpose of extracting the semi structured data from all those tables now scattered in most of the Wiki pages._

 
## Project
###**Requirements**
You can install requirements using requirements.txt `pip install -r requirements.txt`
* Python 2.7
* [RDFlib library](http://rdflib.readthedocs.io/en/stable/gettingstarted.html "RDFlib homepage") (v. >= 4.2)
* [lxml library](http://lxml.de/lxmlhtml.html "lxml homepage") (v. 3.6 Tested)
* Stable internet connection

###**User guide**

Idea's project is to: analyze selected resources and then create related RDF triples. First of all you have to run `pyDomainExplorer`, passing right arguments. This script will create a settings file (named `domain_settings.py`) that you have to fill: it is commented in order to help you.
Finally you can run `pyTableExtractor` that read previous filled file and start to map all resources so that you can obtain RDF triples saved in `Extractions` folder.

###**How to run pyDomainExplorer.py**

`python pyDomainExplorer.py [--chapter --verbose (--where|--single|--topic)]`

* `-c`, `--chapter` : Optional. 2 letter long string representing the desidered endpoint/Wikipedia language (e.g. `en`, `it`, `fr` ...) Default value: 'en'.
* `-v`, `--verbose` : Optional. One number that can be 1 or 2. Each value correspond to a different organization of output file.

###**How to run pyTableExtractor.py**

`python pyTableExtractor.py`
* this script read all parameters in `domain_settings.py` file, so you can run `pyTableExtractor.py` without any problem. It will print file in output that contains RDF triples obtained by domain's analysis.

####**Verbose**
* 1 - Output file will contain new data to map and old mapping rules contained in the table extractor's dictionary.
* 2 - Output file will contain new data to map (shown only one time) and the mapping rules saved in table extractor's dictionary

#####**Note:** -w -s -t are all mutual exclusive parameters  

* `-t`, `--topic` : Optional. Represents a DBpedia ontology class that you want to explore and analyze. It's important to preserve the camelcase form. Eg. "BasketballPlayer".
* `-w`, `--where` : Optional. A SPARQL where clause. Eg. "?film <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/Film>.  ?film <http://dbpedia.org/ontology/director> ?s" is used to collect all film directors of a wiki chapter. Note: please ensure that the set you want to collect is titled as ?s
* `-s`, `--single` : Optional. can be used to select a wiki page at a time. Eg. -s 'Channel_Tunnel' takes only the [wiki page](https://en.wikipedia.org/wiki/Channel_Tunnel "Channel Tunnel wiki page") representing the European channel tunnel between France and UK. [-s]Note: please use only the name of a wiki page without spaces ( substitued by underscores) Eg. Use -s [German_federal_election,_1874](https://en.wikipedia.org/wiki/German_federal_election,_1874 "German federal 1874 election") and not https://en.wikipedia.org/wiki/German_federal_election,_1874 or German federal election, 1874 .

###**Usage examples**

* `python pyDomainExplorer.py -c it -v 1 -w "?s a <http://dbpedia.org/ontology/SoccerPlayer>"` ---> chapter = 'it', verbose= '1', tries to collect resources (soccer players) which answer to this sparql query from DBpedia.

* `python pyDomainExplorer.py -c en -v 2 -t BasketballPlayer` ---> chapter='en', verbose='1', topic='BasketballPlayer', collect resources that are in DBpedia ontology class 'BasketballPlayer'.

* `python pyDomainExplorer.py -c it -v 2 -s "Kobe_Bryant"` ---> the script will works only one [wiki page](https://it.wikipedia.org/wiki/Kobe_Bryant "Kobe Bryant") of 'it' chapter. It's important to use the same name of wikipedia page.

Notes:
* If you choose a topic (-t) or you pass to the script a custom where clause, a list of resources (.txt files) are created in /Resource_lists . 
* If everything is ok, two files are created in /Extractions : a log file (for reporting purpose) and a .ttl file containing the serialized rdf data set.



## Results
Please refer to [Progress_page](https://github.com/dbpedia/extraction-framework/wiki/GSoC_2016_Progress_Simone)

## Folders
**table_extractor** Folder containing sources files for analyzing and mapping all properties found in the script "pyDomainExplorer.py"

**domain_explorer** Folder containing sources files for exploring and reading all properties of a domain.

**Extractions** In this folder you will find .ttl and .log files about extractions you have completed.

**Resource_lists** Here are collected .txt files as result from Selector.py work. Every .txt file contains a list of resources gathered by a SPARQL query (using -t topic or -w custom_where_clause). 

## Sources Files

### pyTableExtractor module
**pyTableExtractor** Module: contains main() function. It will read research's parameters from `domain_settings.py` and it will organize the workflow of all classes.
 
**settings** A settings file used to store default values, both for `pyDomainExplorer` and for `pyTableExplorer`. You can customize scripts from here. 

**Analyzer** Once a list of resources (or a single one) has been formed, Analyzer is summoned in order to analyze tables. It takes a single resource at a time, from a .txt file or from -s parameter.
 
**Utilities** Contains accessory methods used, for example, to setup log file, to get time and date or to call outer services (sparql dbpedia endpoints, JSONPedia, wiki pages as html object).

**Table** Class representing a table. It has some data structures used by other classes in order to recreate the table structure and to extract data.

**HtmlTableParser** Class which takes a html object representing a wiki page of interest. It has the mission to find the structure (extract coherently headers) of the tables in the wiki page selected. Then it tries to extract data and to associate them with the corresponding headers. If the extraction is successful it calls the mapper to map data in RDF statements.

**Mapper** Class used to manage data extracted by the parsers. Depending on mapping_rules.py settings, it tries to map data applying different mapping rules. These rules depend on the chapter and the topic selected. 

**mapping_rules** File that contains mapping rules defined in all previously execution of pyTableExtractor.

### pyDomainExplorer module

**pyDomainExplorer** Main file for exploring the domain or single resource under exam.

**ExplorerTools** Set of functions that help the previous script in the explorer task. There are methods for making SPARQL query on DBpedia, for working with HtmlTableParser and more over.

**Selector** A class used to gather a list of resources calling a SPARQL dbpedia endpoint of chapter selected. It then serialize the list in a .txt file so you can keep trace of which set of resources has been found.   

**WriteSettingsFile** Class built to print file `domain_settings.py` that will contains information about research made by user (resource file, verbose, chapter and more over) and all table's headers found. These headers can be empty (so there isn't any properties previously defined) or can contains 

---

####**statistics.py**

This script, written in collaboration with Federica Baiocchi (@github/Feddie), is useful to know the number of tables or lists contained in Wikipedia pages from a given topic, and was created in collaboration with Feddie who is working on the [List Extractor](https://github.com/dbpedia/list-extractor). We both used it in the beginning of our projects to choose a domain to start from.
#####**How to run statistics.py**

`python statistics.py language struct_type topic`
* `language` : a two letter long prefix representing the desidered endpoint/Wikipedia language to search (e.g. `en`, `it`, `fr` ...)
* `struct_type` : `t` for tables, `l` for lists
* `topic ` : can be either a where clause of a sparql query specifying the requested features of a ?s subject, or a keyword from the following: _dir_ for all DBpedia directors with a Wikipedia pages,  _act_ for actors, _soccer_ for soccer players,_writer_ for writers

######**Usage examples**

*`python statistics.py it t "?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f"`
*`python statistics.py en l writer`


## Progress pages
 *  [GSoC 2016 progress page](https://github.com/dbpedia/extraction-framework/wiki/GSoC_2016_Progress_Simone "Progress")
 *  [GSoC 2017 progress page](https://github.com/dbpedia/table-extractor/wiki/GSoC-2017:-Luca-Virgili-progress)

For any questions please feel to contact:
* Simone papalini, papalini.simone.an@gmail.com , GSoC 2016 student.
* Luca Virgili, lucav48@gmail.com , GSoC 2017 student.
