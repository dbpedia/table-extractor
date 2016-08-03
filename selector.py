import urllib
import json
import datetime
import time
import os.path
import logging

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class Selector:
    # TODO Accurate DOCString
    """
    Class Selector is used to select which kind of pages have to be used in table's analysis.

    Attributes:
        struct_name: is the structures the selector are searching for
        jsonpedia_call_format: suffix used in jsonpedia rest service to get only the part of a wiki page concerning tables
        call_format_sparql:

    """
    def __init__(self, lang, query, topic):
        # TODO USE THE TOPIC ALREADY SET
        """

        :param lang:
        :param query:
        :param topic:
        """
        self.lang = lang
        self.where_clause = query
        self.topic = topic
        self.last_res_list = None
        self.struct_name = "TABLES"

        self.jsonpedia_call_format = "?filter=@type:table&procs=Extractors,Structure"
        self.call_format_sparql = "&format=application%2Fsparql-results%2Bjson&debug=on"
        self.jsonpedia_base_url = "http://jsonpedia.org/annotate/resource/json/"
        self.jsonpedia_lan = lang + ":"
        self.dbpedia = None
        self.dbpedia_sparql_url = self.dbpedia_selection()
        self.query_num_res = "select (count(distinct ?s) as ?res_num) where{" + self.where_clause + "}"
        logging.info("The query used to retrieve the exact number of resources involved is: " + str(self.query_num_res))
        self.query_res_list = "SELECT distinct ?s as ?res WHERE{" + self.where_clause + "} LIMIT 1000 OFFSET "
        logging.info("To find out the actual resources, this SPARQL query is used: " + str(self.query_res_list))
        logging.info("Remember that the OFFSET value is increased by 1000 in a cycle till the total number of resources \
         is reached.")

        self.total_res_found = 0
        self.offset = 0
        self.res_num = 0
        self.tot_res_interested()

        self.res_list_filename = topic+"_"+datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d')+".txt"
        # if os.path.isfile(self.res_list_filename):
        self.list = open(self.res_list_filename, 'w')
        logging.info("The file which contains the list of resources is: " + self.res_list_filename)

        self.written = 0

    def dbpedia_selection(self):
        """

        :return:
        """
        if self.lang != "en":
            self.dbpedia = self.lang + ".dbpedia.org"
        else:
            self.dbpedia = "dbpedia.org"
        return "http://" + self.dbpedia + "/sparql?default-graph-uri=&query="

    def url_composer(self, query):
        """
        This function is used to compose a url to call some std services used by the selector,
        such as sparql endpoints or as jsonpedia rest service.
        Before returning the url composed, the method replaces
        :param query: is the string used in some rest calls.
        :return url: the url composed
        """
        # TODO conditions for dbpedia/jsonpedia services
        query = urllib.quote_plus(query)
        url = self.dbpedia_sparql_url + query + self.call_format_sparql

        return url

    def json_answer_getter(self, url_passed):
        """
        json_answer_getter is a method used to call a REST service and to parse the answer in json.
        It returns a json parsed answer if everything is ok
        :param url_passed: type string,is the url to reach for a rest service
        :return json_parsed: the method returns the answer parsed in json
        """
        try:
            call = urllib.urlopen(url_passed)
            answer = call.read()
            json_parsed = json.loads(answer)
            return json_parsed
        except:
            logging.exception("json answer not well formed for resource: " + str(url_passed))
            print "Exception with url:"+str(url_passed)

    def tot_res_interested(self):
        """
        Method used to retrieve the total number of resources (wiki pages) interested.
        It uses url_composer passing by the query to get the number of res.
        Then it sets tot_res as the response of a call to jsonpedia.
        Last it sets the local instance of total_res_found.
       :return nothing
        """
        try:
            url_composed = self.url_composer(self.query_num_res)
            tot_res = self.json_answer_getter(url_composed)['results']['bindings'][0]['res_num']['value']
            self.total_res_found = int(tot_res)
        except:
            logging.exception("Unable to find the total number of resource involved..")
            print("total resource not found")

    def dbpedia_res_list(self, offset):
        """
        This method retrieve a list of 1000 resources.

        :param offset: is the offset served to sparql service in order to get res from "offset" to "offset"+1000
        :return: res_list is a vector of resources, typically 1000 resources
        """
        try:
            url_res_list = self.url_composer(self.query_res_list+str(offset))
            res_list = self.json_answer_getter(url_res_list)['results']['bindings']
            return res_list
        except:
            logging.info("Lost resources with this offset range: " + str(offset) + " / " + str(offset+1000))
            print ("ERROR RETRIEVING RESOURCES FROM "+str(offset)+" TO "+str(offset+1000))

    def collect_resources(self):
        """
        It is  intended to iterate 1000 resources at once
        :return:
        """
        while self.offset <= self.total_res_found:
            try:
                self.last_res_list = self.dbpedia_res_list(self.offset)
                for res in self.last_res_list:
                    try:
                        res_name = res['res']['value'].replace("http://" + self.dbpedia + "/resource/", "")
                        res_name = res_name.encode('utf-8')
                        self.list.write(str(res_name)+'\n')
                        self.written += 1

                    except:
                        logging.exception("Something went wrong writing down this resource: " + str(res))
                        print("exception for: "+str(res))
                self.__update_offset()

            except:
                print "exception during the iteration of collection of resources"
        self.list.close()
        logging.info("Written down resources:  " + str(self.written))

    def get_lang(self):
        """

        :return:
        """
        return self.lang

    def get_scope(self):
        """

        :return:
        """
        return self.topic

    def get_tot_res(self):
        """

        :return: Number of total resources found for this scope
        """
        return self.total_res_found

    def __update_offset(self):
        """

        :return:
        """
        self.offset += 1000

    def get_res_list_filename(self):

        """

        :return:
        """
        return self.res_list_filename
