import time
import datetime
import sys

import selector
import param_test

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'

'''
The script requires 2 arguments representing:
1) 2-characters string representing the chapter of Wikipedia yuo're interested in
    (e.g. "it" for it.dbpedia.org or "en" for en.wikipedia.org)
    default value is "en"


2) a string representing default queries (soccer, writer, act, all) or a where clause as:
    "?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f"
    (it's important to specify that these resources have a related wikipage)
    Default value is "all"

'''

time = time.time()
date = datetime.datetime.fromtimestamp(time).strftime('%Y_%m_%d')


# First of all a test is run over the parameters passed with the script, see param_test.py
p_tester = param_test.ParamTester(sys.argv)
# Variables language and where_clause are set
# default language is en
language = p_tester.get_lang()
# default where_clause is "all"
where_clause = p_tester.get_where()

# creating a selector object, which is used to retrieve resources of interest (it depends on the scope)
#  from dbpedia/wikipedia/jsonpedia
selec = selector.Selector(language, where_clause)
selec.resources_iterator()
print selec.counter
