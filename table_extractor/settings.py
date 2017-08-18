# coding=utf-8

# This file contains some default configuration for the table_extractor. Please, be aware of customization!

# SETTINGS FOR pyTableExtractor

# When using a online service, number of seconds between two tries
SECONDS_BTW_TRIES = 2

# Max number of attempts to contact a web service.
MAX_ATTEMPTS = 3

# Timeout for url request (write that in seconds)
REQUEST_TIMEOUT = 5

# Following are values used to compose urls of web services.

SPARQL_CALL_FORMAT = "&format=application%2Fsparql-results%2Bjson&debug=on"


# comment to write in mapping_rules.py
COMMENT_MAPPING_RULES = "# coding = utf-8 \n# Mapping rules used to map table's data, topics are used to evaluate " +\
                        "functions with same name."

# mapping rule's prefix
MAPPING_RULE_PREFIX = "MAPPING_RULES_"

# check if a particular property is defined
SPARQL_CHECK_IN_ONTOLOGY = "ASK { <http://dbpedia.org/ontology/", "> ?s ?o }"

PREFIX_MAPPING_RULE = "MAPPING_RULES_"

# Path where the pyTableExtractor dictionary is located
PATH_ACTUAL_DICTIONARY = "../table_extractor/mapping_rules.py"

APPLY_FILTER_TO_TABLE_DATA = True

CHECK_USER_INPUT_PROPERTY = False

# SETTINGS FOR pyDomainExplorer
# strings for settings file's header
CODING_DOMAIN = "# coding = utf-8 \n"
RESEARCH_TYPE = "RESEACH_TYPE"
VERBOSE_TYPE = "VERBOSE_VALUE"
DOMAIN_TITLE = "DOMAIN_EXPLORED"
CHAPTER = "CHAPTER"
SECTION_NAME = "SECTION_"
CHARACTER_SEPARATOR = "_tte_"
SECTION_NAME_PROPERTY = "sectionProperty"
FIRST_COMMENT = "# Comments below will help you in filling this file settings. Remember to change only " +\
                SECTION_NAME + " variables.\n# Please do not modify pyDomainExplorer parameters. \n\n" \
                               "# pyDomainExplorer parameters "
COMMENT_FOR_EXAMPLE_PAGE = "# Example page where it was found this section: "
COMMENT_SECTION_PROPERTY = "# The entry named " + SECTION_NAME_PROPERTY + " represents ontology property associated " +\
    "to table's section.\n" \
    "# (Eg. in basket domain, section named playoff can be mapped with something like 'playoff' or "\
    " 'playoffMatch').\n# Triple example: <http://dbpedia.org/resource/Kobe_Bryant> " \
    "<http://dbpedia.org/ontology/playoffMatch>\n# <http://dbpedia.org/resource/Kobe_Bryant__1>"
COMMENT_FILLED_ELEMENT = "# If you see elements already filled, it means that I have already found that header" \
                         " in pyTableExtractor dictionary\n# or on dbpedia ontology\n" \
                         "# If you empty a field that was filled, you will delete that rule from dictionary."

RESOURCE_FILE = "RESOURCE_FILE"
END_OF_FILE = "\n# END OF FILE \n"

# Path where pyDomainExplorer print the result file .py
FILE_PATH_DOMAIN_EXPLORED = "../domain_settings.py"

# Help for verbose input
VERBOSE_DEFAULT = '1'
VERBOSE_CHOISES = [1, 2]
VERBOSE_HELP = " Verbose can be 1,2. Verbose 1 list all headers for each section, while verbose 2 write only one" \
               " time a header.( Eg. if two sections named 'playoff' and 'regular season' has header 'Year', in " \
               " verbose 2 you will see 'Year' only one time in file settings) "

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
TOPIC_HELP = "Topic input. In this field you have to one of the mapping classes defined on dbpedia. (Eg." \
             "BasketballPlayer, Broadcaster) Go there: http://mappings.dbpedia.org/server/ontology/classes/ " \
             "to see all available classes."

# Single clause message help
SINGLE_HELP = "Search for a single resource, named like wikipedia page. Remember to include" \
              " underscore in resource's name. (Eg. Kobe_Bryant or Mick_Jagger)"

# Where clause message help
WHERE_HELP = "Define a correct SPARQL where clause. It's important to name '?s' results given by query." \
             "(Eg. -w ' ?s foaf:name ?name.  FILTER(?name = \"Kobe Bryant\"@it) "

# define different topic selected by user
TOPIC_WHERE = "SPARQL where clause defined"

# path for dictionary created by pyDomainExplorer
PATH_DOMAIN_EXPLORER = "../domain_settings.py"

# path where a file with all resources will created
PATH_FOLDER_RESOURCE_LIST = "../Resource_lists"

# languages available in scripts
LANGUAGES_AVAILABLE = ["en", "it", "fr", "de", "pt", "es"]

# Query for getting DBpedia class resources
SPARQL_GET_RESOURCES = ["select ?s where{ ", "}"]

# Query for verifying if there is a resource with a particular property
SPARQL_CHECK_PROPERTY = ["select ?s where{", " ?s rdfs:label ", " } LIMIT 10"]

# which property's type I have to pick - I have found three different types: 'resource','ontology','property'
ONTOLOGY_TYPE = ["ontology"]

# Queries to select a list of resources and the number of resources involved
SPARQL_RES_LIST_QUERY = ["SELECT distinct ?s as ?res WHERE{", "} LIMIT 5 OFFSET "]

# Query to get number of resources involved in an execution
SPARQL_NUM_RES_QUERY = ["select (count(distinct ?s) as ?res_num) where{", "}"]

NUMBER_OF_WIKI_EXAMPLES = 3