# table-extractor, a GSoC 2016 project 


#### You can find progress page [here](https://github.com/dbpedia/extraction-framework/wiki/GSoC_2016_Progress_Simone "Progress")

###Requirements
You can install requirements using requirements.txt `pip install -r requirements.txt`
* Python 2.7
* [RDFlib library](http://rdflib.readthedocs.io/en/stable/gettingstarted.html "RDFlib homepage") (v. >= 4.2)
* [lxml library](http://lxml.de/lxmlhtml.html "lxml homepage") (v. 3.6 Tested)
* Stable internet connection

###How to run pyTableExtractor.py
`python pyTableExtractor.py [(--where|--single|--topic) --chapter --mode]`

* `-c`, `--chapter` : Optional. 2 letter long string representing the desidered endpoint/Wikipedia language (e.g. `en`, `it`, `fr` ...) Default value: 'en'. Reccomendation: do not use  -m 'json'  
* `-m`, `--mode` : Optional. As I changed approach to the problem, I initially face the project working with JSONPedia, I introduced two working method for the algorithm : json or html. Default value: 'html'

#####Note: -w -s -t are all mutual exclusive parameters  

* `-t`, `--topic` : Optional. one of the keywords from the following: 'elections' for pages related to electoral results, 'elections_USA' to limit election result to USA presidential elections, 'all' to select all wiki pages, 'soccer' for soccer players, 'actors' , 'directors' for people who has directed a film, 'writers'. Default value: 'all' (all wiki pages from a chapter).
* `-w`, `--where` : Optional. A SPARQL where clause. Eg. "?film <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/Film>.  ?film <http://dbpedia.org/ontology/director> ?s" is used to collect all film directors of a wiki chapter. Note: please ensure that the set you want to collect is titled as ?s
* `-s`, `--single` : Optional. can be used to select a wiki page at a time. Eg. -s 'Channel_Tunnel' takes only the [wiki page](https://en.wikipedia.org/wiki/Channel_Tunnel "Channel Tunnel wiki page") representing the European channel tunnel between France and UK. [-s]Note: please use only the name of a wiki page without spaces ( substitued by underscores) Eg. Use -s [German_federal_election,_1874](https://en.wikipedia.org/wiki/German_federal_election,_1874 "German federal 1874 election") and not https://en.wikipedia.org/wiki/German_federal_election,_1874 or German federal election, 1874 .

###Usage examples: 
* `python pyTableExtractor.py` ---> as default it takes chapter = 'it', topic= 'elections', mode='html'

* `python pyTableExtractor.py -c it -w "?s a <http://dbpedia.org/ontology/SoccerPlayer>"` ---> chapter = it, tries to collect resources (soccer players) which answer to this sparql query from dbpedia, mode='html'

* `python pyTableExtractor.py -c en -t actors -m html` ---> chapter='en', topic='actors', mode='html'

* `python pyTableExtractor.py -c it -s "Elezioni_presidenziali_negli_Stati_Uniti_d'America_del_1888"` ---> the script will works only one [wiki page](https://it.wikipedia.org/wiki/Elezioni_presidenziali_negli_Stati_Uniti_d%27America_del_1888 "USA 1888 presidential election, it chapter") of 'it' chapter 

Notes:
* If you choose a topic (-t) or you pass to the script a custom where clause, a list of resources (.txt files) are created in /Resource_lists . 
* If everything is ok, two files are created in /Extractions : a log file (for reporting purpose) and a .ttl file containing the serialized rdf data set.

### Little final Report:
Please refer to [Progress_page](https://github.com/dbpedia/extraction-framework/wiki/GSoC_2016_Progress_Simone)

### Results:
Please refer to [Progress_page](https://github.com/dbpedia/extraction-framework/wiki/GSoC_2016_Progress_Simone)

### Abstract:
 _Wikipedia is full of data hidden in tables. The aim of this project is to explore the possibilities of exploiting all the data represented with the appearance of tables in Wiki pages, in order to populate the different chapters of DBpedia through new data of interest. The Table Extractor has to be the engine of this data “revolution”: it would achieve the final purpose of extracting the semi structured data from all those tables now scattered in most of the Wiki pages._

### Folders:
**table_extractor** Folder containing sources files. You can find main script here (pyTableExtractor.py)

**Extractions** In this folder you will find .ttl and .log files about extractions you have completed.

**Resource_lists** Here are collected .txt files as result from Selector.py work. Every .txt file contains a list of resources gathered by a SPARQL query (using -t topic or -w custom_where_clause). 

### Sources Files:

**pyTableExtractor** Module: contains main() function. It calls the other classes/modules as it should be done during usual operations. It first tests parameters calling param_test. Then, if a topic or a where clause are set, it calls selector.py to build up a list of resources. Afterward in all cases it calls the analyzer class. Analyzer is responsible to elaborate a resource at a time, to find out the tables' structure and to extract data. Analyzer finally calls Mapper, used to map data extracted on a RDF dataset. 
 
**param_test** Using ArgParse this class is used to test parameters passed to the main script (pyTableExtractor.py). It takes most of the default values from settings.py, so take a look a that file to change default values or to add custom ones.

**settings** A settings file used to store default values. You can customize the script from here. Eg you can add your personal topic adding a topic in TOPIC_CHOICES list, and the corresponding SPARQL query in TOPIC_SPARQL dictionary (please ensure the consistency of dictionary key and the topic added)

**Selector** A class used to gather a list of resources calling a SPARQL dbpedia endpoint of chapter selected. It then serialize the list in a .txt file so you can keep trace of which set of resources has been found.   

**Analyzer** Once a list of resources (or a single one) has been formed, Analyzer is summoned in order to analyze tables. It takes a single resource at a time, from a .txt file or from -s parameter. Depending on the mode selected (html, or json) it passes, respectively to htmlParser.py or to tableParser.py, the objects (html or json) representing the wiki page of interest.
 
**Utilities** Contains accessory methods used, for example, to setup log file, to get time and date or to call outer services (sparql dbpedia endpoints, JSONPedia, wiki pages as html object).

**Table** Class representing a table. It has some data structures used by other classes in order to recreate the table structure and to extract data.

**JsonTableParser** Class which takes a json object (I used JSONPedia service) representing a wiki page of interest. It has the mission to find the structure (extract coherently headers) of the tables in the wiki page selected. Then it tries to extract data and to associate them with the corresponding headers. If the extraction is successful it calls the mapper to map data in RDF statements. Note: I warn users to not use this parser as I found lot of problems (which depend especially from Wiki users errors) with tables structures. In fact I had to change approach to the problem, realizing a html parser.

**HtmlTableParser** Class which takes a html object representing a wiki page of interest. It has the mission to find the structure (extract coherently headers) of the tables in the wiki page selected. Then it tries to extract data and to associate them with the corresponding headers. If the extraction is successful it calls the mapper to map data in RDF statements.

**Mapper** Class used to manage data extracted by the parsers. Depending on mapping_rules.py settings, it tries to map data applying different mapping rules. These rules depend on the chapter and the topic selected. 

**mapping_rules** File which store rules to be used depending on the topic and the wiki chapter selected.


---

####statistics.py
This script, written in collaboration with Federica Baiocchi (@github/Feddie), is useful to know the number of tables or lists contained in Wikipedia pages from a given topic, and was created in collaboration with Feddie who is working on the [List Extractor](https://github.com/dbpedia/list-extractor). We both used it in the beginning of our projects to choose a domain to start from.
#####How to run statistics.py
`python statistics.py language struct_type topic`
* `language` : a two letter long prefix representing the desidered endpoint/Wikipedia language to search (e.g. `en`, `it`, `fr` ...)
* `struct_type` : `t` for tables, `l` for lists
* `topic ` : can be either a where clause of a sparql query specifying the requested features of a ?s subject, or a keyword from the following: _dir_ for all DBpedia directors with a Wikipedia pages,  _act_ for actors, _soccer_ for soccer players,_writer_ for writers
######Usage examples: 
*`python statistics.py it t "?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f"`
*`python statistics.py en l writer`


For any questions please feel free to contact me by [email](papalini.simone.an@gmail.com "author email")