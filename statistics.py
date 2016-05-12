import urllib
import json
import datetime
import time
import logging

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'
__coauthor__ = 'feddie - Federica Baiocchi - feddiebai@gmail.com'

# Some STD configurations: logging, scope of analysis, dbpedia used, query to select the scope of interest
time = time.time()
date = datetime.datetime.fromtimestamp(time).strftime('%Y_%m_%d')
scope = "SOCCER PLAYERS"
logging.basicConfig(filename="statistics -"+scope+" - "+date+".log", filemode='w', level=logging.WARNING, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
dbpedia = "it.dbpedia.org"
dbpedia_sparql = "http://"+dbpedia+"/sparql?default-graph-uri=&query="
query_num_res = "select count(?s) as ?res_num where{?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f}"
query_scope = "SELECT ?s as ?res WHERE{ ?s a <http://dbpedia.org/ontology/SoccerPlayer> . ?s <http://dbpedia.org/ontology/wikiPageID> ?a} ORDER BY ?res LIMIT 1000 OFFSET "
call_format_sparql = "&format=application%2Fsparql-results%2Bjson&debug=on"
offset = 0


''':param question is the url to jsonpedia service, used to retrieve info of interest
Json_call is used to recall the jsonpedia service with the query quest as parameter
'''


def json_call(question):
    call = urllib.urlopen(question)
    answer = call.read()
    print "answer: "+answer
    deserialized = json.loads(answer)
    print "deserialized :"+str(deserialized)
    return deserialized

''':param url is the url already composed and ready to be called
Dbpedia_res_list is a function used to know how many pages are related to the scope considered
'''


def dbpedia_tot_res(url):
    # obtaining the answer from the web service
    tot_res = json_call(url)
    # finding usable results
    tot_res = tot_res['results']['bindings'][0]['res_num']['value']
    return tot_res

# Url_composition is a function that compose correctly the url to call a jsonpedia or a dbpedia/sparql service'''


def url_composition(query):
    query= urllib.quote_plus(query)
    url = dbpedia_sparql+query+call_format_sparql
    return url

logging.warning("You're analyzing statistics about "+scope+ " at "+dbpedia)
url = url_composition(query_num_res)
print "url: "+url
tot_resources = dbpedia_tot_res(str(url))
logging.warning("Total number of resources of "+scope+" in "+dbpedia+" : "+tot_resources)
