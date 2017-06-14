# String for printing to file domain_settings.py
CODING_DOMAIN = "# coding=utf8"
RESEARCH_TYPE ="RESEACH_TYPE"
DOMAIN_TITLE = "DOMAIN_EXPLORED"
MAIN_PROPERTY = "MAIN_PROPERTY"
CHAPTER = "CHAPTER"
SECTION_NAME = "SECTION_"
CHARACTER_SEPARATOR ="_tte_"
SECTION_NAME_PROPERTY = "sectionProperty"
# Query for getting DBpedia class resources
SPARQL_GET_RESOURCES = ["select ?s where{ ", "} LIMIT 5"]

# Query for verifying if there is a resource with a particular property
SPARQL_CHECK_PROPERTY = ["select ?s where{ ?s <http://dbpedia.org/ontology/", "> ?o} LIMIT 1"]

PREFIX_MAPPING_RULE = "MAPPING_RULES_"

# Path where the pyTableExtractor dictionary is located
PATH_ACTUAL_DICTIONARY = "../table_extractor/mapping_rules.py"

# Path where pyDomainExplorer print the result file .py
FILE_PATH_DOMAIN_EXPLORED = "../domain_settings.py"

# Help for verbose input
VERBOSE_DEFAULT = '1'
VERBOSE_CHOISES = [1, 2, 3]
VERBOSE_HELP =" Verbose can be 1,2,3"


# Help for chapter input
CHAPTER_DEFAULT = 'en'

CHAPTER_HELP = "Language of Wikipedia pages/resources to analyze. \n \
                Please ensure you are using an existing wikipedia chapter tag! \n \
                Eg: 'it' ---> it.wikipedia.org \n \
                'en' ---> en.wikipedia.org \n \
                'fr' ---> fr.wikipedia.org  etc. etc. \n \
                DEFAULT = "+CHAPTER_DEFAULT

# Here you have a general description of what the script (pyTableExtraction.py) do
GENERAL_DESCRIPTION = "This script try to parse data from tables in wiki pages.\n " \
                      " To do so, it uses a WYSIWYG approach, using mapping rules " \
                      "over cells of data depending on topic, wiki chapter and on some other parameters." \
                      "Data found are reorganized in a RDF dataset and serialized in turtle format."

# Help for topic input
TOPIC_HELP = "Topic input"

# Single HELP
SINGLE_HELP = "Search for a single resource, named like wikipedia page"

WHERE_HELP = "Define a correct where clause"

# define different topic selected by user
TOPIC_WHERE = "SPARQL where clause defined"
TOPIC_SINGLE ="Analyze single resource"