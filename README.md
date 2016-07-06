# table-extractor
### Abstract:
 _Wikipedia is full of data hidden in tables. The aim of this project is to explore the possibilities of exploiting all the data represented with the appearance of tables in Wiki pages, in order to populate the different chapters of DBpedia through new data of interest. The Table Extractor has to be the engine of this data “revolution”: it would achieve the final purpose of extracting the semi structured data from all those tables now scattered in most of the Wiki pages._

####statistics.py
This script is useful to know the number of tables or lists contained in Wikipedia pages from a given topic, and was created in collaboration with Feddie who is working on the [List Extractor](https://github.com/dbpedia/list-extractor). We both used it in the beginning of our projects to choose a domain to start from.
#####How to run statistics.py
`python statistics.py language struct_type topic`
* `language` : a two letter long prefix representing the desidered endpoint/Wikipedia language to search (e.g. `en`, `it`, `fr` ...)
* `struct_type` : `t` for tables, `l` for lists
* `topic ` : can be either a where clause of a sparql query specifying the requested features of a ?s subject, or a keyword from the following: _dir_ for all DBpedia directors with a Wikipedia pages,  _act_ for actors, _soccer_ for soccer players,_writer_ for writers
######Usage examples: 
*`python statistics.py it t "?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f"`
*`python statistics.py en l writer`