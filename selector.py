import urllib
import json

__author__='papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class Selector:
    # TODO Accurate DOCString
    """
    Class Selector is used to select which kind of pages have to be used in table's analysis.

    Attributes:
        struct_name: is the structures the selector are searching for
        jsonpedia_call_format: suffix used in jsonpedia rest service to get only the part of a wiki page concerning tables
        call_format_sparql:

    """
    def __init__(self, lang, scope):
        """

        :param lang:
        :param scope:
        """
        self.last_res_list = None
        self.struct_name = "TABLES"
        self.jsonpedia_call_format = "?filter=@type:table&procs=Extractors,Structure"
        self.call_format_sparql = "&format=application%2Fsparql-results%2Bjson&debug=on"
        self.lang = lang
        self.jsonpedia_base_url = "http://jsonpedia.org/annotate/resource/json/"
        self.jsonpedia_lan = lang + ":"
        self.where_clause = scope
        self.topic = ""
        self.scope_selection(scope)
        self.dbpedia_sparql_url = self.dbpedia_selection()
        self.query_num_res = "select (count(distinct ?s) as ?res_num) where{" + self.where_clause + "}"
        self.query_res_list = "SELECT distinct ?s as ?res WHERE{" + self.where_clause + "} LIMIT 1000 OFFSET "

        self.total_res_found = 0
        self.offset = 0
        self.res_num = 0
        self.tot_res_interested()
        # tests
        # TODO erase this part once tested
        print str(self.query_num_res)
        self.counter = 0


    def scope_selection(self, scope_passed):
        """

        :param scope_passed:
        :return:
        """
        if scope_passed == "soccer":
            self.topic = " Soccer Players"
            self.where_clause = "?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f"
        elif scope_passed == "act":
            self.topic = " Actors"
            self.where_clause = "?s a <http://dbpedia.org/ontology/Actor>.?s <http://dbpedia.org/ontology/wikiPageID> ?f"
        elif scope_passed == "dir":
            self.where_clause = "?film <http://dbpedia.org/ontology/director> ?s . ?s <http://dbpedia.org/ontology/wikiPageID> ?f"
            self.topic = " Directors"
        elif scope_passed == "writer":
            self.where_clause = "?s a <http://dbpedia.org/ontology/Writer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f"
            self.topic = " Writers"
        elif scope_passed == "all":
            self.where_clause = "?s <http://dbpedia.org/ontology/wikiPageID> ?f"
            self.topic = " All pages"
        else:
            # TODO set a way to accept where clauses with different results than ?s
            self.where_clause = scope_passed
            self.topic = "Custom Selection"
        return

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
            print ("ERROR RETRIEVING RESOURCES FROM "+str(offset)+" TO "+str(offset+1000))

    def resources_iterator(self):
        """
        It is  intended to iterate 1000 resources at once
        :return:
        """
        while self.offset <= self.total_res_found:
            try:
                self.last_res_list = self.dbpedia_res_list(self.offset)
                self.__update_offset()
                # TODO insert the part of iteration
            except:
                print "none"

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

    def __update_offset(self):
        """

        :return:
        """
        self.offset += 1000
