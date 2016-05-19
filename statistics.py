import urllib
import json
import datetime
import time
import logging

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'
__coauthor__ = 'feddie - Federica Baiocchi - feddiebai@gmail.com'

# Some STD configurations: getting time and formatting the date
time = time.time()
date = datetime.datetime.fromtimestamp(time).strftime('%Y_%m_%d')

# scope is used to compose log's name
scope = "WIKI PAGES - TABLES - EN "
# configuring log
logging.basicConfig(filename="statistics -"+scope+" - "+date+".log", filemode='w', level=logging.WARNING, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# baseurl to JSONpedia service
jsonpedia = "http://jsonpedia.org/annotate/resource/json/"

# wiki chapter to be used when requesting resources on JSONpedia, it should be same language of wiki used to retrieve resources' list
#jsonpedia_lan = "it:"
jsonpedia_lan = "en:"

# These two strings is used to request the application of filters in JSONpedia service, for more info visit jsonpedia.org
jsonpedia_call_format_table = "?filter=@type:table&procs=Extractors,Structure"
jsonpedia_call_format_list = "?filter=@type:list&procs=Extractors,Structure"

# version of DBpedia used
#dbpedia = "it.dbpedia.org"
dbpedia = "dbpedia.org"

# setting the BaseUrl to the DBpedia SPARQL Endpoint
dbpedia_sparql = "http://"+dbpedia+"/sparql?default-graph-uri=&query="

# string containing the query in SPARQL language used to enumerate  type's searched resources
query_num_res = "select count(?s) as ?res_num where{?s <http://dbpedia.org/ontology/wikiPageID> ?f}"
#query_num_res = "select count(?s) as ?res_num where{?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f}"
#query_num_res = "select count(?s) as ?res_num  where{?s <http://dbpedia.org/ontology/wikiPageID> 736 }"

# string wich contains the query to get the list of resources you want to analyze

query_scope = "SELECT ?s as ?res WHERE{?s <http://dbpedia.org/ontology/wikiPageID> ?a} LIMIT 1000 OFFSET "
#query_scope = "SELECT ?s as ?res WHERE{ ?s a <http://dbpedia.org/ontology/SoccerPlayer> . ?s <http://dbpedia.org/ontology/wikiPageID> ?a} LIMIT 1000 OFFSET "
#query_scope = "select ?s as ?res  where{?s <http://dbpedia.org/ontology/wikiPageID> 736 } LIMIT 1000 OFFSET "

# format required from a call to the endpoint
call_format_sparql = "&format=application%2Fsparql-results%2Bjson&debug=on"

# global variables are set to 0
total_res_found = 0
offset = 0
res_num = 0
res_lost_jsonpedia = 0


''':param question is the url to jsonpedia service, used to retrieve info of interest
Json_call is used to recall a web service with the query question as parameter asking for a json formatted response.
Urllib is used to instance a communication while json library to deserialize the answer
'''


def json_call(question):
    call = urllib.urlopen(question)
    answer = call.read()
    deserialized = json.loads(answer)
    return deserialized

''':param query is the query to submit to the web service (endpoint sparql or jsonpedia)
:param type is used to switch between service requested, 1 = dbpedia sparql endpoint , 2 = jsonpedia searching for tables , 3 = jsonpedia searching for lists
 Url_composition is a function that compose correctly the url to call a jsonpedia or a dbpedia/sparql service'''


def url_composition(query,type):
    query= urllib.quote_plus(query)
    if type == 1 :
        url = dbpedia_sparql+query+call_format_sparql
        return url
    elif type == 2 :
        url = jsonpedia+jsonpedia_lan+query+jsonpedia_call_format_table
        return url
    elif type == 3:
        url = jsonpedia + jsonpedia_lan + query + jsonpedia_call_format_list
        return url
    else:
        print "type error"

''':param url is the url already composed and ready to be called
Dbpedia_tot_res is a function used to know how many pages are related to the scope considered
'''


def dbpedia_tot_res(url):
    # obtaining the answer from the web service
    tot_res = json_call(url)
    # finding usable results
    tot_res = tot_res['results']['bindings'][0]['res_num']['value']
    return tot_res

''':param url is the url already composed and ready to be called
Dbpedia_res_list is a function used to retrieve resources (LIMIT at a time) from dbpedia
'''


def dbpedia_res_list(url):
    # obtaining the answer from the web service
    list_res = json_call(url)
    # finding usable results
    list_res = list_res['results']['bindings']
    return list_res

''':param json_answer contains an array delivered by JSONpedia and already deserialized
   :param type indicates which kind of information do you want, type = 2 for tables, type = 3 for lists
 tl_retrieve is a function used to retrieve the number of tables or lists in a wiki page
'''


def tl_retrieve(json_answer,type):
    if type == 2:
        total_structures = len(json_answer['result'])
        #logging.warning("Elements found for this resource: "+str(total_structures))
        #print "Tables: "+str(total_structures)
    elif type == 3:
        total_structures = len(json_answer['result'])
        #logging.warning("Elements found for this resource: " + str(total_structures))
        #print "Lists: "+str(total_structures)
    return total_structures

# brief stat at the beginning of log, it indicates the scope of data and wiki/dbpedia chapter
logging.warning("You're analyzing statistics about "+scope+ " at "+dbpedia)
# composing the request to get the total number of data scope considered
res_num_query = url_composition(query_num_res,1)
# call to dbpedia to get the total number of resources considered
tot_resources = dbpedia_tot_res(str(res_num_query))
# writing result on the log
logging.warning("Total number of resources of "+scope+" in "+dbpedia+" : "+tot_resources)

# cycling result list to inspect wiki pages
# condition to stop the cycle is that var offset become bigger than the number of total resources
while offset <= int(tot_resources):

    # retrieving a list of 1000 resources of the kind of interest
    try:
        #composing query
        res_list_url= url_composition(query_scope+str(offset),1)
        #retrieve the list
        res_list = dbpedia_res_list(res_list_url)
    except:
        logging.exception("Exception: Lost resources from  " + str(offset) + " to " + str(offset+1000) + ", REPORT: ")

    # updating the offset in order to cycle with new resources
    offset += 1000
    # if res_list has some results in it:
    if res_list:
        try:
            #for every resource in res_list
            for resource in res_list:
                # res is a var containing the URI of a resource
                res = resource['res']['value']
                # extracting name of the resource
                res_name = res.replace("http://"+dbpedia+"/resource/", "")
                # encoding the name in utf-8 , useful because a lot of URIs are composed by utf-8
                res_name = res_name.encode('utf-8')
                # printing on the log the name of the resource analyzed
                try:
                    #logging.warning("Total elements found : " + str(total_res_found))
                    # updating resource index
                    res_num +=1
                    res_name_spaced = res_name.replace("_", " ")
                    #logging.warning("Analyzing "+str(res_name_spaced)+". Resource # "+str(res_num)+" of "+str(tot_resources))
                    logging.warning("Resource # " + str(res_num) + " of " + str(tot_resources)+". Total tables found : "+str(total_res_found))
                    # composing the url to call the jsonpedia service, filtering the wiki page in order to catch only tables
                    table_call_to_jsonpedia = url_composition(res_name, 2)
                    # call to api
                    table_json_answer = json_call(table_call_to_jsonpedia)
                    # call to function used to count the number of tables(2) or list(3) in a wiki page
                    if len(table_json_answer) == 3:
                        print "Problems related to JSONpedia service :"+str(table_json_answer)
                        logging.warning("JSONpedia failure")
                        res_lost_jsonpedia +=1
                    else:
                        # calling the function to count tables/lists and adding result to total number
                        total_res_found += tl_retrieve(table_json_answer, 2)

                except:
                    print "Lost: "+res_name
                    logging.exception("Exception REPORT: ")
        except:
            print "Exception during cycle"
    else:
        print "Exception during the retrieval of resource list"

logging.warning("Resources lost due to JSONPedia related problems:"+str(res_lost_jsonpedia))
logging.warning(scope+" - Total number of TABLES:  "+str(total_res_found))