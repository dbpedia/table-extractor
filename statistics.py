import urllib
import json
import datetime
import time
import logging
import sys
import argparse

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'
__coauthor__ = 'feddie - Federica Baiocchi - feddiebai@gmail.com'

"""
The script requires 3 arguments representing:
1) 2-characters string representing the DBpedia endpoint to query (e.g. it for it.dbpedia.org or en for dbedia.org)
2) character 'l' or 't' to look for lists or tables
3) a string representing default queries (soccer, writer, act, all) or a where clause as:
    "?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f
    (it's important to specify that these resources have a related wikipage)
"""



def set_where_topic(where_clause) :
    """
    Returns where clause of the query and topic name which will be used for the log file.
    It also associates some shortcuts with actual queries
    :param where_clause:
    :return: a couple of string values corresdponding to the where clause to be used in the query
    and the topic or domain to be analyzed
    """
    topic = ''
    # temporary shortcuts for particular searches
    if where_clause == "soccer":
        where_clause = "?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f"
        topic = " Soccer Players"
    elif where_clause == "act":
        where_clause = "?s a <http://dbpedia.org/ontology/Actor>.?s <http://dbpedia.org/ontology/wikiPageID> ?f"
        topic = " Actors"
    elif where_clause == "dir":
        where_clause = "?film <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/Film>. \
         ?film <http://dbpedia.org/ontology/director> ?s . ?s <http://dbpedia.org/ontology/wikiPageID> ?f"
        topic = " Directors"
    elif where_clause == "writer":
        where_clause = "?s a <http://dbpedia.org/ontology/Writer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f"
        topic = " Writers"
    elif where_clause == "all":
        where_clause = "?s <http://dbpedia.org/ontology/wikiPageID> ?f"
        topic = " All wikis"
    return [where_clause, topic]

def json_call(question):
    """
    This method is used to recall a web service with the query question as parameter asking for a json formatted response.
    Urllib is used to instance a communication, while json library to deserialize the answer
    :param question: the url to jsonpedia service, used to retrieve info of interest
    :return: Wiki page representation in JSON format
    """
    try:
        call = urllib.urlopen(question)
        answer = call.read()
        deserialized = json.loads(answer)
        return deserialized
    except IOError:
        print("Connection Error on request: " + question + ". Please try again")
        return "InternetE"
    except ValueError:
        print ("Error! " + answer + " is not a Json object.")
        return "valueE"
    except:
        print ("General Exception during json call")
        return "GeneralE"

def dbpedia_call_compose(query, dbpedia_sparql) :
    """
    Constructs a URL to query a DBpedia endpoint
    :param query: the query to be submitted to the sparql endpoint
    :param dbpedia_sparql: contains URL prefix with the selected endpoint
    :return: complete URL
    """
    query = urllib.quote_plus(query)
    url = dbpedia_sparql + query + "&format=application%2Fsparql-results%2Bjson&debug=on"
    return url

def jsonpedia_call_compose(res, jsonpedia_suffix) :
    """
    Constructs a URL to query JSONpedia web service
    :param res: resource corresponding to the Wikipedia page to be analyzed
    :param jsonpedia_suffix: contains the last part of the request which varies for lists or tables
    :return: complete URL
    """
    res = language + ":" + res
    url = "http://jsonpedia.org/annotate/resource/json/" + res + jsonpedia_suffix
    return url

def dbpedia_tot_res(url):
    """
    it's used to know how many pages are related to the scope considered
    :param url: already composed url, ready to be called
    :return: number of total resources
    """
    try:
        # obtaining the answer from the web service
        tot_res = json_call(url)
        # finding usable results
        tot_res = tot_res['results']['bindings'][0]['res_num']['value']
        return tot_res
    except ValueError:
        print("Connection Error on request "+ url +" , please check your connection and retry")
        return 0
    except :
        print("Something went wrong - Could not retrieve resources")
        return 0

def dbpedia_res_list(url):
    """
    It's used to retrieve resources (LIMIT at a time) from dbpedia
    :param url: already composed url, ready to be called
    :return:  a list of DBpedia resources satisfyng the query
    """
    # obtaining the answer from the web service
    list_res = json_call(url)
    # finding usable results
    list_res = list_res['results']['bindings']
    return list_res


def init_log() :
    """
    Initializes and creates log file containing statistics
    :return: log file name
    """
    # Some STD configurations: getting time and formatting the date
    curr_time = time.time()
    date = datetime.datetime.fromtimestamp(curr_time).strftime('%Y_%m_%d')
    # configuring log
    file_name = scope + " (" + date + ").log"
    logging.basicConfig(filename=file_name, filemode='w', level=logging.WARNING,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    # brief stat at the beginning of log, it indicates the scope of data and wiki/dbpedia chapter
    logging.warning("You're analyzing statistics about " + scope + " at " + dbpedia)
    return file_name

def res_count() :
    '''
    Performs a SPARQL query on the given endpoint to retrieve the number of resources from the given type
    :return: total number of resources
    '''
    # string containing the query in SPARQL language used to enumerate  type's searched resources
    query_num_res = "SELECT (count(distinct ?s) as ?res_num) where{" + where_clause + "}"
    # composing the request to get the total number of data scope considered
    res_num_query = dbpedia_call_compose(query_num_res, dbpedia_sparql)
    # call to dbpedia to get the total number of resources considered
    tot_resources = int(dbpedia_tot_res(res_num_query))
    # writing result on the log
    logging.warning("Total number of resources : " + str(tot_resources))
    return tot_resources


def find_res_list(tot_res) :
    """
    Since the maximum number of results is 1000, it performs (N mod 1000) SPARQL queries to the endpoint
    and constructs a list of resource names.
    :param tot_res: number of resources
    :return: complete list of resources
    """
    offset = 0
    tot_list = []
    # string which contains the query to get the list of resources you want to analyze
    query_scope = "SELECT distinct ?s as ?res WHERE{" + where_clause + "} LIMIT 1000 OFFSET "
    while offset <= tot_res:
        # retrieving a list of 1000 resources of the kind of interest
        try:
            # composing query
            query = query_scope + str(offset)
            res_list_url = dbpedia_call_compose(query, dbpedia_sparql)
            # call to dbpedia to get the total number of resources considered)
            # retrieve the list
            list_res = dbpedia_res_list(res_list_url)
            for l in list_res:
                tot_list.append(l)
        except:
            logging.exception("Exception: Lost resources from  " + str(offset) + " to " + str(offset + 1000) + ", REPORT: ")
        # updating the offset in order to cycle with new resources
        offset += 1000
    return tot_list

def analyze_stats(tot_res, res_list) :
    """
    Iterates on list of resources found and updates logfile with the number of lists or tables found
    for each resource, as well as the total number of structures
    :param tot_res: total number of resources found
    :param res_list: list of resources
    """
    # initialize count variables
    total_res_found = 0 #number of list or tables found until now
    res_num = 0 #resource index
    res_lost_jsonpedia = 0 #number of resrources lost due to JSONpedia
    calls_to_jsonpedia = 0 #
    try:
        # for every resource in res_list
        for resource in res_list:
            # res is a var containing the URI of a resource
            res = resource['res']['value']
            # extracting name of the resource
            res_name = res.replace("http://" + dbpedia + "/resource/", "")
            # encoding the name in utf-8 , useful because a lot of URIs are composed by utf-8
            res_name = res_name.encode('utf-8')
            # printing on the log the name of the resource analyzed
            try:
                res_num += 1 # updating resource index
                res_name_spaced = res_name.replace("_", " ")
                # composing the url to call the jsonpedia service, filtering the wiki page in order to catch only tables or lists
                call_to_jsonpedia = jsonpedia_call_compose(res_name, jsonpedia_call_format)
                control = True #flag used to repeat JSONpedia calls
                while control:
                    json_answer = json_call(call_to_jsonpedia)
                    # keeping trace of the number of jsonpedia calls
                    calls_to_jsonpedia += 1
                    if type(json_answer) != basestring:
                        if 'message' in json_answer.keys():
                            message = json_answer['message']
                            if message == u'Invalid page metadata.':
                                logging.warning("Lost: " + res_name + " due to Invalid page metadata exception ")
                                control = False
                                res_lost_jsonpedia += 1
                            elif message == u'Expected DocumentElement found ParameterElement':
                                logging.warning(
                                    "Lost: " + res_name + " due to \'Expected DocumentElement, found ParameterElement\' exception ")
                                control = False
                                res_lost_jsonpedia += 1
                            elif message == u'Expected DocumentElement found ListItem':
                                logging.warning(
                                    "Lost: " + res_name + " due to \'Expected DocumentElement found ListItem\' exception ")
                                control = False
                                res_lost_jsonpedia += 1
                            elif message == u'Expected DocumentElement found TableCell':
                                logging.warning(
                                    "Lost: " + res_name + " due to \'Expected DocumentElement found TableCell\' exception ")
                                control = False
                                res_lost_jsonpedia += 1
                            elif len(json_answer) == 3:
                                print "Problems related to JSONpedia service :" + str(json_answer) + " - RETRYING"
                        else:
                            # set control to false in order to exit the cycle of calls
                            control = False
                            total_res_found += len(json_answer['result'])
                            logging.warning("Resource [" + str(res_name_spaced) + "] #" + str(res_num) + \
                                " of " + str(tot_res) + \
                                ". Tot " + struct_name.lower() + " found : " + str(total_res_found))
            except:
                print "Lost: " + res_name
                logging.exception("Exception REPORT: ")
    except:
        print "Exception during cycle"

    logging.warning("Resources lost due to JSONPedia related problems:" + str(res_lost_jsonpedia))
    logging.warning(scope + " - Total number of " + struct_name + ": " + str(total_res_found))
    logging.warning(scope + " - Total calls to JSONpedia services :" + str(calls_to_jsonpedia))


def main() :
    parser = argparse.ArgumentParser(description='Statistics related to tables and lists in Wikipedia pages')
    parser.add_argument('language', help="Two letter long prefix representing Wikipedia language and SPARQL endpoint to query. Example : en, it")
    parser.add_argument('struct_type', help="Specify whether to analyze statistics about tables (t) or lists (l)", choices=['t', 'l'] )
    parser.add_argument('where_clause', help="Where clause specifying desired topic. Example: \"?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s \
                                <http://dbpedia.org/ontology/wikiPageID> ?f)\"")
    args = parser.parse_args()

    global language
    global struct_name
    global jsonpedia_call_format
    if args.struct_type == "l":
        struct_name = "LISTS"
        # This string is used to request the application of filters in JSONpedia service, for more info visit jsonpedia.org
        jsonpedia_call_format = "?filter=@type:list&procs=Extractors,Structure"
    elif args.struct_type == "t":
        struct_name = "TABLES"
        jsonpedia_call_format = "?filter=@type:table&procs=Extractors,Structure"
    try:
        len(args.language) == 2
        language = args.language
    except:
        print("The first argument should be a language code, as en or it")
        sys.exit(0)

    global where_clause
    global scope
    tw = set_where_topic(args.where_clause)
    where_clause = tw[0]
    topic =tw[1]

    # topic is used to compose log's name - e.g. TABLES WIKI PAGES SoccerPlayers - EN (<current date>)
    scope = struct_name + " WIKI PAGES" + topic + " - " + str(language).upper()

    #specify version of DBpedia used
    global dbpedia
    dbpedia = "dbpedia.org"
    if args.language != "en":
        dbpedia = language + ".dbpedia.org"
    # setting the BaseUrl to the DBpedia SPARQL Endpoint
    global dbpedia_sparql
    dbpedia_sparql = "http://" + dbpedia + "/sparql?default-graph-uri=&query="

    log_file_name = init_log()
    tot_resources = res_count()
    res_list = find_res_list(tot_resources)

    if res_list :
        analyze_stats(tot_resources, res_list)
        print("Statistics stored in "+ log_file_name)
    else:
        print ("Exception during the retrieval of resource list - no resources found")


if __name__ == "__main__":
    main()
