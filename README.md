# The table extractor - GSoC 2017 project 

## Abstract
 _Wikipedia is full of data hidden in tables. The aim of this project is to explore the possibilities of exploiting all the data represented with the appearance of tables in Wiki pages, in order to populate the different chapters of DBpedia through new data of interest. The Table Extractor has to be the engine of this data “revolution”: it would achieve the final purpose of extracting the semi structured data from all those tables now scattered in most of the Wiki pages._

## Get ready

### Project
Idea's project is to analyze resources chosen by user and to create related RDF triples. First of all you have to run `pyDomainExplorer`, passing right arguments to it. This script will create a settings file (named `domain_settings.py` in `domain_explorer` folder) that you have to fill: it is commented to help you in this work.
Then run `pyTableExtractor` that read previous filled file and start to map all resources so that you can obtain RDF triples saved in `Extractions` folder.

### Requirements
First of all you must have libraries that I used to develop code.
You can install requirements using requirements.txt `pip install -r requirements.txt`
* Python 2.7
* [RDFlib library](http://rdflib.readthedocs.io/en/stable/gettingstarted.html "RDFlib homepage") (v. >= 4.2)
* [lxml library](http://lxml.de/lxmlhtml.html "lxml homepage") (v. 3.6 Tested)
* Stable internet connection

## Get started
### How to run table-extractor

* Clone repository.

* Choose a language (`--chapter`, e.g. `en`, `it`, `fr` ...).

* Choose a set of resources to analyze,  that could be:
   * Single resource (`--single`, e.g. `Kobe_Bryant`, `Roberto_Baggio`, ..). Remember to let underscore instead of space in resource name.
   * DBpedia mapping class (`--topic`, e.g. `BasketballPlayer`, `SoccerPlayer`,..), you have a complete list [there](http://mappings.dbpedia.org/server/ontology/classes/).
   * Where clause (`--where`, e.g. "?film <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/Film>.  ?film <http://dbpedia.org/ontology/director> ?s" is used to collect all film directors of a wiki chapter. Note: please ensure that the set you want to collect is titled as ?s.
   
* Choose a value for output format, that could be 1 or 2. See below to understand how this value influence `domain_settings.py` file.

* Now you can run `pyDomainExplorer.py`:

`python pyDomainExplorer.py [--chapter --output_format (--where|--single|--topic)]`

This module will take resources in language defined by user and will analyze each table that are in wikipedia pages. At the end of execution, it creates a file named `domain_settings.py` in `domain_explorer` folder.

_What is this file for?_

`domain_settings.py` contains all sections and headers found in exploration of the domain. You will observe a dictionary structure and some fields that have to be filled. Below there is an example of output.

* Next step is to fill `domain_settings.py`. Remember that you are writing _mapping rules_, so you are making an association between a table's header (or table's section) with a dbpedia ontology property.

* When you have compiled `domain_settings.py`, you can easily run `pyTableExtractor.py` in this way:

`python pyTableExtractor.py`

This script read all parameters in `domain_explorer/domain_settings.py` and print a .ttl file that contains RDF triples obtained by domain's analysis.

If it goes well, you will get a dataset in `Extraction` folder!

Read below something more about arguments passed to `pyDomainExplorer`.

### Usage examples

* `python pyDomainExplorer.py -c it -f 1 -w "?s a <http://dbpedia.org/ontology/SoccerPlayer>"` ---> chapter = 'it', output_format= '1', tries to collect resources (soccer players) which answer to this sparql query from DBpedia.

* `python pyDomainExplorer.py -c en -f 2 -t BasketballPlayer` ---> chapter='en', output_format='2', topic='BasketballPlayer', collect resources that are in DBpedia ontology class 'BasketballPlayer'.

* `python pyDomainExplorer.py -c it -f 2 -s "Kobe_Bryant"` ---> the script will works only one [wiki page](https://it.wikipedia.org/wiki/Kobe_Bryant "Kobe Bryant") of 'it' chapter. It's important to use the same name of wikipedia page.

Notes:
* If you choose a topic (-t) or you pass to the script a custom where clause, a list of resources (.txt files) are created in /Resource_lists . 
* If everything is ok, three files are created in /Extractions : two log file (one for pyDomainExplorer and one for pyTableExtractor) and a .ttl file containing the serialized rdf data set.


### pyDomainExplorer arguments
There are three arguments that has to be passed to `pyDomainExplorer`.
* `-c`, `--chapter` : Required. 2 letter long string representing the desidered endpoint/Wikipedia language (e.g. `en`, `it`, `fr` ...) Default value: 'en'.

* `-f`, `--output_format` : Required. One number that can be 1 or 2. Each value correspond to a different organization of output file.

* Required one of these arguments:

  * `-t`, `--topic` : Represents a DBpedia ontology class that you want to explore and analyze. It's important to preserve the camelcase form. Eg. "BasketballPlayer".
  
  * `-w`, `--where` : A SPARQL where clause. Eg. "?film http://www.w3.org/1999/02/22-rdf-syntax-ns#type http://dbpedia.org/ontology/Film. ?film http://dbpedia.org/ontology/director ?s" is used to collect all film directors of a wiki chapter. Note: please ensure that the set you want to collect is titled as ?s.
  
  * `-s`, `--single` : can be used to select a wiki page at a time. Eg. -s 'Channel_Tunnel' takes only the wiki page representing the European channel tunnel between France and UK. [-s]Note: please use only the name of a wiki page without spaces ( substitued by underscores) Eg. Use -s German_federal_election,_1874 and not https://en.wikipedia.org/wiki/German_federal_election,_1874 or German federal election, 1874 .

### Small digression on -f parameter
Filling all fields in file like `domain_settings.py` could be a problem for user. So I have to bring ways to facilitate his work. Some of these ways are research over DBpedia ontology and check if a header has already a property. Another way that I provided is through `-f` parameter.

Suppose that you have to analyze domain like basketball player and you read a table's header like `points`.

In all sections you will observe that this header is always associated to `totalPoints` of dbpedia ontology.
For this reason, I think that print only one time this header in `domain_settings.py` will help user that hasn't to rewrite a property n times.

However you can put `-f` to 1, so same header will be printed several times over `domain_settings.py`

In a nutshell, output organization equal to:
* 1 - Output file will contain same header repeated for all sections where it is.
* 2 - Each header is unique, so you won't observe same header in different sections.

Below there is a little example that could explain better how `-f` parameter works.

#### Example of output organization parameter usage

In a domain like basketball player, you can observe these `domain_settings.py` files. The first one refers to `-f` equal to 1 while the second one is related to `-f` equal to 2. You can use this parameter to simplify your work over all different domains.
```
### OUTPUT FORMAT VALUE: 1
# Example page where it was found this section: Kobe_Bryant
SECTION_Playoffs = {
'sectionProperty': '', 
'Year': 'Year', 
'Team': 'team', 
'GamesPlayed': '', 
'GamesStarted': ''
} 
# Example page where it was found this section: Kobe_Bryant
SECTION_Regular_season = {
'sectionProperty': '', 
'Year': 'Year', 
'Team': 'team', 
'GamesPlayed': '', 
'GamesStarted': ''
} 

# END OF FILE 
```
```
### OUTPUT FORMAT VALUE: 2
# Example page where it was found this section: Kobe_Bryant
SECTION_Playoffs = {
'sectionProperty': '', 
'Year': 'Year', 
'Team': 'team', 
'GamesPlayed': '', 
'GamesStarted': ''
} 
# Example page where it was found this section: Kobe_Bryant
SECTION_Regular_season = {
'sectionProperty': '',
} 

# END OF FILE 
```

As you can see above, headers like `GamesPlayed` and `GamesStarted` are printed twice in `domain_settings.py` with `-f` equal to 1, while on second `domain_settings.py` with `-f` equal to 2, you can see that `GamesPlayed` and `GamesStarted` are printed only one time. In this way you can write only one mapping rules instead of two.

## Results
In this page: [Results page](https://github.com/dbpedia/table-extractor/tree/master/Extractions/GSoC%202017%20Results) you can observe dataset (english and italian) extracted using `table extractor` . Furthermore you can read log file created in order to see all operations made up for creating RDF triples.

I recommend to also see [this page](https://github.com/dbpedia/table-extractor/wiki), that contains idea behind project and an example of result extracted from log files and .ttl dataset.

Note that effectiveness of the mapping operation mostly depends on how many rules user has wrote in `domain_settings.py`.

---

## statistics.py

This script, written by Simone Papalini (@github/papalinis) and Federica Baiocchi (@github/Feddie), is useful to know the number of tables or lists contained in Wikipedia pages from a given topic, and was created in collaboration with Feddie who is working on the [List Extractor](https://github.com/dbpedia/list-extractor). We both used it in the beginning of our projects to choose a domain to start from.
### Get started
#### How to run statistics.py

`python statistics.py language struct_type topic`
* `language` : a two letter long prefix representing the desidered endpoint/Wikipedia language to search (e.g. `en`, `it`, `fr` ...)
* `struct_type` : `t` for tables, `l` for lists
* `topic ` : can be either a where clause of a sparql query specifying the requested features of a ?s subject, or a keyword from the following: _dir_ for all DBpedia directors with a Wikipedia pages,  _act_ for actors, _soccer_ for soccer players,_writer_ for writers

#### Usage examples

*`python statistics.py it t "?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f"`
*`python statistics.py en l writer`


## Progress pages
 *  [GSoC 2017 progress page](https://github.com/dbpedia/table-extractor/wiki/GSoC-2017:-Luca-Virgili-progress)
 *  [GSoC 2016 progress page](https://github.com/dbpedia/extraction-framework/wiki/GSoC_2016_Progress_Simone "Progress")

For any questions please feel to contact:
* Luca Virgili, lucav48@gmail.com , GSoC 2017 student.
* Simone papalini, papalini.simone.an@gmail.com , GSoC 2016 student.

