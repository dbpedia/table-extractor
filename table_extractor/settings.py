# coding=utf-8

# This file contains some default configuration for the table_extractor. Please, be aware of customization!

# When using a online service, number of seconds between two tries
SECONDS_BTW_TRIES = 2
# Max number of attempts to contact a web service.
MAX_ATTEMPTS = 5

# Following are values used to compose urls of web services.

SPARQL_CALL_FORMAT = "&format=application%2Fsparql-results%2Bjson&debug=on"

# Queries to select a list of resources and the number of resources involved
SPARQL_RES_LIST_QUERY = ["SELECT distinct ?s as ?res WHERE{", "} LIMIT 5 OFFSET "]

SPARQL_NUM_RES_QUERY = ["select (count(distinct ?s) as ?res_num) where{", "}"]


# path for dictionary created by pyDomainExplorer
PATH_DOMAIN_EXPLORER = "../domain_settings.py"

# comment to write in mapping_rules.py
COMMENT_MAPPING_RULES = "# coding = utf-8 \n# Mapping rules used to map table's data, topics are used to evaluate" +\
                        "functions with same name."

# mapping rule's prefix
MAPPING_RULE_PREFIX = "MAPPING_RULES_"

# identify row section
ROW_SUFFIX = "row"

# SETTINGS FOR pyDomainExplorer
CODING_DOMAIN = "# coding = utf-8"
RESEARCH_TYPE = "RESEACH_TYPE"
DOMAIN_TITLE = "DOMAIN_EXPLORED"
CHAPTER = "CHAPTER"
SECTION_NAME = "SECTION_"
CHARACTER_SEPARATOR = "_tte_"
SECTION_NAME_PROPERTY = "sectionProperty"
ROW_TABLE_PROPERTY = "rowTableProperty"
COMMENT_FOR_EXAMPLE_PAGE = "# Example page where it was found this section: "
RESOURCE_FILE = "RESOURCE_FILE"
# Query for getting DBpedia class resources
SPARQL_GET_RESOURCES = ["select ?s where{ ", "}"]

# Query for verifying if there is a resource with a particular property
SPARQL_CHECK_PROPERTY = ["select ?s where{", " ?s rdfs:label ", " } LIMIT 5"]

PREFIX_MAPPING_RULE = "MAPPING_RULES_"

# Path where the pyTableExtractor dictionary is located
PATH_ACTUAL_DICTIONARY = "../table_extractor/mapping_rules.py"

# Path where pyDomainExplorer print the result file .py
FILE_PATH_DOMAIN_EXPLORED = "../domain_settings.py"

# Help for verbose input
VERBOSE_DEFAULT = '1'
VERBOSE_CHOISES = [1, 2, 3]
VERBOSE_HELP = " Verbose can be 1,2,3"


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


PATH_FOLDER_RESOURCE_LIST = "../Resource_lists"
