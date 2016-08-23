# coding=utf-8

# This file contains some default configuration for the table_extractor. Please, be aware of customization!

# Here you have a general description of what the script (pyTableExtraction.py) do
GENERAL_DESCRIPTION = "This script try to parse data from tables in wiki pages.\n " \
                      " To do so, it uses a WYSIWYG approach, using mapping rules " \
                      "over cells of data depending on topic, wiki chapter and on some other parameters." \
                      "Data found are reorganized in a RDF dataset and serialized in turtle format."

# String of help for -s option
SINGLE_HELP = "Use -s | --single to specify a single Wikipedia resource to parse. \n \
                                    Eg: -s Andrea_Pirlo"
# DEFAULT topic
TOPIC_DEFAULT = 'elections'

# Help for -t option
TOPIC_HELP = "Use -t | --topic to specify a set of wiki pages to work with. "


""" Topic you can choose from as -t parameter choice. Eg: -t actors
     CUSTOMIZATION NOTE: Please ensure to add both the topic here and the relative sparql where_clause in
     TOPIC_SPARQL_WHERE_CLAUSE."""
TOPIC_CHOICES = ['all', 'soccer', 'actors', 'directors', 'writers', 'elections', 'elections_USA']


""" Sparql where clause divided by topic, to access them use TOPIC_SPARQL_WHERE_CLAUSE[topic]
   CUSTOMIZATION NOTE: please ensure that the where clause use ?s as the main variable"""
TOPIC_SPARQL_WHERE_CLAUSE = {
                'soccer': "?s a <http://dbpedia.org/ontology/SoccerPlayer>",

                'elections': "?s a <http://dbpedia.org/ontology/Election>",

                'elections_USA': "?s <http://it.dbpedia.org/property/wikiPageUsesTemplate> \
                             <http://it.dbpedia.org/resource/Template:Elezioni_negli_Stati_Uniti_d'America>",

                'actors': "?s a <http://dbpedia.org/ontology/Actor>",

                'directors': "?film <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/Film>. \
                             ?film <http://dbpedia.org/ontology/director> ?s",

                'writers': "?s a <http://dbpedia.org/ontology/Writer>"

                }

# Help for -w option
WHERE_HELP = "Use -w | --where to specify a custom SPARQL where clause, \
                                    capable of select a subset of wiki pages to work with. \n \
                                    Note: you have to use ?s as the final query output. \n \
                                    Eg: \"?s a <http://dbpedia.org/ontology/Writer>\" to select all \
                                    pages describing writers. "

# MODE you can choose from, as -m parameter. Eg: -m json
MODE_CHOICES = ['html', 'h', 'json', 'j']
# MODE is a dictionary fulfilled with aliases for html and json
MODE = {'html': 'html',
        'h': 'html',
        'json': 'json',
        'j': 'json'
        }
# DEFAULT MODE
MODE_DEFAULT = 'html'
# Help for -m option
MODE_HELP = "Mode used to parse the web pages, \n \
             With 'h' | 'html' script will use HtmlTableParser.py, \n \
             With 'j' | 'json' script will use TableParser.py, a parser which use JSONPedia results. \n \
             DEFAULT = "+MODE_DEFAULT

# DEFAULT chapter
CHAPTER_DEFAULT = 'it'
# Help for -c option
CHAPTER_HELP = "Language of Wikipedia pages/resources to analyze. \n \
                Please ensure you are using an existing wikipedia chapter tag! \n \
                Eg: 'it' ---> it.wikipedia.org \n \
                'en' ---> en.wikipedia.org \n \
                'fr' ---> fr.wikipedia.org  etc. etc. \n \
                DEFAULT = "+CHAPTER_DEFAULT

# When using a online service, number of seconds between two tries
SECONDS_BTW_TRIES = 2
# Max number of attempts to contact a web service.
MAX_ATTEMPTS = 5

# Following are values used to compose urls of web services.
JSONPEDIA_CALL_FORMAT = "?&procs=Extractors,Structure"

JSONPEDIA_SECTION_FORMAT = "?filter=@type:section&procs=Extractors,Structure"

JSONPEDIA_TABLES_FORMAT = "?filter=@type:table&procs=Extractors,Structure"

SPARQL_CALL_FORMAT = "&format=application%2Fsparql-results%2Bjson&debug=on"

JSONPEDIA_BASE_URL = "http://jsonpedia.org/annotate/resource/json/"

# Queries to select a list of resources and the number of resources involved
SPARQL_RES_LIST_QUERY = ["SELECT distinct ?s as ?res WHERE{", "} LIMIT 1000 OFFSET "]

SPARQL_NUM_RES_QUERY = ["select (count(distinct ?s) as ?res_num) where{", "}"]

# where clause to ensure that ?s has a wiki page
WIKI_PAGE = ". ?s <http://dbpedia.org/ontology/wikiPageID> ?f"
