# String for printing to file domain_settings.py
DOMAIN_TITLE = "DOMAIN_EXPLORED"
MAIN_PROPERTY = "MAIN_PROPERTY"
CHAPTER ="CHAPTER"
SECTION_NAME = "SECTION_"
CHARACTER_SEPARATOR ="_tte_"
SECTION_NAME_PROPERTY = "sectionProperty"
# Query for getting DBpedia class resources
SPARQL_GET_RESOURCES = ["select ?s where{ ?s ?o dbo:", "} LIMIT 100"]

# Query for verifying if there is a resource with a particular property
SPARQL_CHECK_PROPERTY = ["select ?s where{ ?s dbo:", " ?o} LIMIT 1"]

PREFIX_MAPPING_RULE = "MAPPING_RULES_"

# Path where the pyTableExtractor dictionary is located
PATH_ACTUAL_DICTIONARY = "../table_extractor/mapping_rules.py"

# Path where pyDomainExplorer print the result file .py
FILE_PATH_DOMAIN_EXPLORED = "../domain_settings.py"
