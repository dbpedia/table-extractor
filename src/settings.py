# Some default configurations

# Here you are a general description of what the script (pyTableExtraction.py) do
GENERAL_DESCRIPTION = "This script try to parse data from tables in wiki pages.\n  \
                                                            Data found are reorganized in a RDF dataset (format:turtle)"

# Single
SINGLE_HELP = "Use -s | --single to specify a single Wikipedia resource to parse. \n \
                                    Eg: -s Andrea_Pirlo"

TOPIC_DEFAULT = 'all'
TOPIC_HELP = "Use -t | --topic to specify a set of wiki pages to work with. "
# Topic you can choose from as -t parameter choice. Eg: -t actors
TOPIC_CHOICES = ['all', 'soccer', 'actors', 'directors', 'writers', 'elections', 'elections_USA']

#
TOPIC_SPARQL = {
                'soccer': "?s a <http://dbpedia.org/ontology/SoccerPlayer>",

                'elections': "?s a <http://dbpedia.org/ontology/Election>",

                'elections_USA': "?s <http://it.dbpedia.org/property/wikiPageUsesTemplate> \
                             <http://it.dbpedia.org/resource/Template:Elezioni_negli_Stati_Uniti_d'America>",

                'actors': "?s a <http://dbpedia.org/ontology/Actor>",

                'directors': "?film <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/Film>. \
                             ?film <http://dbpedia.org/ontology/director> ?s",

                'writers': "?s a <http://dbpedia.org/ontology/Writer>"

                }

# WHERE
WHERE_HELP = "Use -c | --custom to specify a custom SPARQL where clause, \
                                    capable of select a subset of wiki pages to work with. \n \
                                    Note: you have to use ?s as the final query output. \n \
                                    Eg: \"?s a <http://dbpedia.org/ontology/Writer>\" to select all \
                                    pages describing writers. "

# MODE you can choose, as -m parameter. Eg: -m json
MODE_CHOICES = ['html', 'h', 'json', 'j']
MODE = {'html': 'html',
        'h': 'html',
        'json': 'json',
        'j': 'json'
        }
MODE_DEFAULT = 'html'
MODE_HELP = "Mode used to parse the web pages, \n \
             With 'h' | 'html' script will use htmlParser.py, \n \
             With 'j' | 'json' script will use tableParser.py, a parser which use JSONPedia results. \n \
             DEFAULT = "+MODE_DEFAULT

#
CHAPTER_DEFAULT = 'en'
CHAPTER_HELP = "Language of Wikipedia pages/resources to analyze. \n \
                Please ensure you are using an existing wikipedia chapter tag! \n \
                Eg: 'it' ---> it.wikipedia.org \n \
                'en' ---> en.wikipedia.org \n \
                'fr' ---> fr.wikipedia.org  etc. etc. \n \
                DEFAULT = "+CHAPTER_DEFAULT



#
jsonpedia_call_format = "?&procs=Extractors,Structure"

jsonpedia_section_format = "?filter=@type:section&procs=Extractors,Structure"

jsonpedia_tables_format = "?filter=@type:table&procs=Extractors,Structure"

call_format_sparql = "&format=application%2Fsparql-results%2Bjson&debug=on"

jsonpedia_base_url = "http://jsonpedia.org/annotate/resource/json/"

wiki_page = ". ?s <http://dbpedia.org/ontology/wikiPageID> ?f"
