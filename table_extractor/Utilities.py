# coding=utf-8

import urllib
import json
import time
import datetime
import lxml.html
import lxml.etree as etree
import os
import errno
import logging
import settings

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class Utilities:
    """
    Utilities is a class containing a lot of methods and attributes used by the others class and modules.
    It requires only a 2 alpha-characters string representing a wiki chapter and a topic of interest.
    Topic is used mainly in reporting and composing filename for log while chapter is used to correctly address the outer
    service calls.

    Public methods:
    - setup_log()
    - test_dir_existence(directory_to_test) # to tests if a directory exists in current filesystem
    - get_current_dir() # returns current directory
    - join_paths(path1, path2) # use os.path to join tho relative paths

    - json_object_getter(resource, struct='jsonpedia') # retrieve a json representation of the requested resource
    - html_object_getter(resource) # return a html representation of the requested resource

    - tot_res_interested(query) # return the total number of the resources selected with the Sparql query passed as a parameter.
    - dbpedia_res_list(query, offset) # return 1000 resources at a time of the scope identified by 'query'
    - ask_if_resource_exists(resource) # test if a resource currently exists in the dbpedia endpoint RDF graph of reference.
    - get_date_time() # return YEAR_MONTH_DAY_HOUR_MINUTES
    - get_date() # return YEAR_MONTH_DAY
    - print_report() # print in the log metrics to evaluate efficiency of the script

    """

    def __init__(self, chapter, topic):

        self.chapter = chapter
        self.topic = topic

        # test if the directory ../Extractions exists (or create it)
        self.test_dir_existence('../Extractions')

        # First of all setup the log and initialize it
        self.setup_log()

        # These values are used to compose calls to services as JsonPedia or Sparql endpoints or to a html wiki page
        self.jsonpedia_call_format = settings.JSONPEDIA_CALL_FORMAT
        self.jsonpedia_section_format = settings.JSONPEDIA_SECTION_FORMAT
        self.jsonpedia_tables_format = settings.JSONPEDIA_TABLES_FORMAT
        self.jsonpedia_base_url = settings.JSONPEDIA_BASE_URL
        self.jsonpedia_lan = self.chapter + ":"
        self.call_format_sparql = settings.SPARQL_CALL_FORMAT
        self.html_format = "https://" + self.chapter + ".wikipedia.org/wiki/"
        # self.res_lost_jsonpedia is used to count how many resources are lost due to jsonpedia service problems
        self.res_lost_jsonpedia = 0

        # Parameters used in methods which need internet connection
        self.time_to_attend = settings.SECONDS_BTW_TRIES  # seconds to sleep between two internet service call
        self.max_attempts = settings.MAX_ATTEMPTS  # max number of internet service' call tries

        # self.dbpedia is used to contain which dbpedia to use Eg. dbpedia.org
        self.dbpedia = None
        # use dbpedia_selection to set self.dbpedia and self.dbpedia_sparql_url
        self.dbpedia_sparql_url = self.dbpedia_selection()

        # Instancing a lxml HTMLParser with utf-8 encoding
        self.parser = etree.HTMLParser(encoding='utf-8')

        self.logging = logging

        # Variables used in final report, see print_report()
        self.res_analyzed = 0
        self.res_collected = 0
        self.data_extracted = 0
        self.tot_tables = 0
        self.tot_tables_analyzed = 0
        self.rows_extracted = 0
        self.data_extraction_errors = 0
        self.not_resolved_header_errors = 0
        self.headers_errors = 0
        self.mapping_errors = 0
        self.no_mapping_rule_errors = 0
        self.mapped_cells = 0
        self.triples_serialized = 0

    def setup_log(self):
        """
        Initializes and creates log file containing info and statistics
        """
        # getting time and date
        current_date_time = self.get_date_time()

        # obtain the current directory
        current_dir = self.get_current_dir()
        # composing the log filename as current_date_and_time + _LOG_T_EXT + chapter_chosen + topic_chosen
        filename = current_date_time + "_LOG_T_Ext_" + self.chapter + '_' + self.topic + ".log"
        # composing the absolute path of the log
        path_desired = self.join_paths(current_dir, '../Extractions/' + filename)

        # configuring logger
        logging.basicConfig(filename=path_desired, filemode='w', level=logging.DEBUG,
                            format='%(levelname)-3s %(asctime)-4s %(message)s', datefmt='%m/%d %I:%M:%S %p')

        # brief stat at the beginning of log, it indicates the  wiki/dbpedia chapter and topic selected
        logging.info("You're analyzing wiki tables, wiki chapter: " + self.chapter + ", topic: " + self.topic)

    def test_dir_existence(self, directory):
        current_dir = self.get_current_dir()
        dir_abs_path = self.join_paths(current_dir, directory)

        if not os.path.exists(dir_abs_path):
            print('Folder doesn\'t exist, creating..')
            try:
                os.makedirs(dir_abs_path)
                print('done')
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

    def get_current_dir(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        return cur_dir

    def join_paths(self, path1, path2):
        destination = os.path.join(path1, path2)
        return destination

    def dbpedia_selection(self):
        """
        Method used to set self.dbpedia and to return the URL to the correct dbpedia sparql endpoint depending on the
        chapter (self.chapter) used.
        :return: URL to the correct dbpedia sparql endpoint.
        """
        if self.chapter != "en":
            self.dbpedia = self.chapter + ".dbpedia.org"
        else:
            self.dbpedia = "dbpedia.org"
        return "http://" + self.dbpedia + "/sparql?default-graph-uri=&query="

    def url_composer(self, query, service):
        """
        This function is used to compose a url to call some web services, such as sparql endpoints or jsonpedia
        rest service.

        :param query: is the string used in some rest calls. For a jsonpedia service is typically the resource name.
        :param service: type of service you request (jsonpedia, dbpedia sparql endpoint..)
        :return url: the url composed
        """
        # use quote_plus method from urllib to encode special character (must to do with web service)
        query = urllib.quote_plus(query)

        """
        The following if clause are differentiated by service requested Eg. 'dbpedia', 'jsonpedia'...
            but in all the cases url is composed using pre formatted string along with the query
        """
        if service == 'dbpedia':
            url = self.dbpedia_sparql_url + query + self.call_format_sparql

        elif service == 'jsonpedia':
            url = self.jsonpedia_base_url + self.jsonpedia_lan + query + self.jsonpedia_call_format

        elif service == 'jsonpedia_tables':
            url = self.jsonpedia_base_url + self.jsonpedia_lan + query + self.jsonpedia_tables_format

        elif service == 'jsonpedia_sections':
            url = self.jsonpedia_base_url + self.jsonpedia_lan + query + self.jsonpedia_section_format

        elif service == 'html':
            url = self.html_format + query

        else:
            url = "ERROR"
        return url

    def json_answer_getter(self, url_passed):
        """
        json_answer_getter is a method used to call a web service and to parse the answer in json.
        It returns a json parsed answer if everything is ok
        :param url_passed: type string,is the url to reach for a rest service
        :return json_parsed: the method returns the JSON parsed answer to the call to JSONpedia
        """
        try:
            # open a call with urllib.urlopen and passing the URL
            call = urllib.urlopen(url_passed)
            # read the answer
            answer = call.read()
            # decode the answer in json
            json_parsed = json.loads(answer)
            # return the answer parsed
            return json_parsed
        except IOError:
            print ("Try, again, some problems due to Internet connection, url: " + url_passed)
            return "Internet problems"
        except ValueError:
            print ("Not a JSON object.")
            return "ValueE"
        except Exception as e:
            print "Exception with url:" + str(url_passed)
            return "GeneralE"

    def html_answer(self, url_passed):
        try:
            call = urllib.urlopen(url_passed)
            html_document = lxml.html.parse(call, self.parser)
            return html_document
        except IOError:
            print ("Try, again, some problems due to Internet connection, url: " + url_passed)

            return "Internet Error"
        except ValueError:
            print ("Not a HTML object.")
            return "Value Error"
        except:
            print "Exception with url:" + str(url_passed)
            return "General Error"

    def json_object_getter(self, resource):
        """
        Method used to retrieve a JSON representation of the wiki page (from JSONpedia) of 'resource' parameter.

        :param resource: (str) the name of resource which JSON representation we want to get.
                Eg. "Elezioni_amministrative_italiane_del_2016"
        :return json_answer: is the JSON parsed answer to the call to JSONpedia service. If everything is ok it would be
            the JSON wrapped representation of the resource's wiki page
        """
        json_answer = None

        # compose the URL to make the call to the JSONpedia web service
        jsonpedia_url = self.url_composer(resource, 'jsonpedia')

        """
        set json_object_state to 'try'.
        json_object_state is a string used to track the status of object_state. Once the web server answer, this answer
         is tested in order be sure of its correctness. json_object_state can be 'try','JSON object well formed','Invalid page metadata',
         'Expected DocumentElement found ParameterElement', 'Expected DocumentElement found ListItem',
         'Expected DocumentElement found TableCell'  (see test_json_result())

        """
        json_object_state = 'try'

        while json_object_state == 'try':
            try:
                # call to JSONpedia service  using json_answer_getter(URL)
                json_answer = self.json_answer_getter(jsonpedia_url)

                if type(json_answer) != str:
                    # test if json answer well formed using test_json_result(json_answer)
                    json_object_state = self.test_json_result(json_answer)
                else:

                    # waiting time_to_attend before trying again
                    time.sleep(self.time_to_attend)
            except:
                print("Error during json_object_getter")
        # if json_object_state is not equal to 'try' return json_answer
        print(json_object_state)
        return json_answer

    def html_object_getter(self, resource):
        html_url = self.url_composer(resource, 'html')
        is_answer_ok = False
        attempts = 0
        html_answer = None

        while is_answer_ok != True and attempts < self.max_attempts:
            try:
                attempts += 1
                html_answer = self.html_answer(html_url)
                if type(html_answer) != str:
                    is_answer_ok = self.test_html_result(html_answer)
                else:
                    time.sleep(self.time_to_attend)
            except:
                print("Error trying to get html object")

        if is_answer_ok:
            print("Html document well formed..")
        else:
            print("Error trying to get html object : %s" % html_answer)
            html_answer = None
        return html_answer

    def test_json_result(self, json_obj):
        # JSONPedia returns a message part if there are problems with that resource, or with the service itself
        if 'message' in json_obj.keys():
            # keep and set message
            message = json_obj['message']

            # Following different values are all possible JSONpedia fatal errors for a specific resource.
            if message == u'Invalid page metadata.':
                self.res_lost_jsonpedia += 1
                return 'Invalid page metadata'

            elif message == u'Expected DocumentElement found ParameterElement':
                self.res_lost_jsonpedia += 1
                return 'Expected DocumentElement found ParameterElement'

            elif message == u'Expected DocumentElement found ListItem':
                self.res_lost_jsonpedia += 1
                return 'Expected DocumentElement found ListItem'

            elif message == u'Expected DocumentElement found TableCell':
                self.res_lost_jsonpedia += 1
                return 'Expected DocumentElement found TableCell'

            # if the problem regarding server traffic on JSONpedia the length of json_obj is == 3
            elif len(json_obj) == 3:
                print "Problems related to JSONpedia service :" + str(json_obj) + " - RETRYING"
                return 'try'

        # if 'message' is not in json_obj the object is correctly formed
        else:
            return 'JSON object well formed'

    def test_html_result(self, html_doc):
        # TODO implement a test on html_object
        if type(html_doc) == str and "Error" in html_doc:
            return False
        else:
            return True

    def tot_res_interested(self, query):
        """
        Method used to retrieve the total number of resources (wiki pages) interested.
        It uses url_composer passing by the query to get the number of res.
        Then it sets tot_res as the response of a call to jsonpedia.
        Last it sets the local instance of total_res_found.
       :return nothing
        """
        try:
            url_composed = self.url_composer(query, 'dbpedia')
            json_answer = self.json_answer_getter(url_composed)
            tot_res = json_answer['results']['bindings'][0]['res_num']['value']
            total_res_found = int(tot_res)
            return total_res_found
        except:
            logging.exception("Unable to find the total number of resource involved..")
            print("total resource not found")

    def dbpedia_res_list(self, query, offset):
        """
        This method retrieve a list of 1000 resources using a SPARQL query.
        It composes the URL to be called, and then retrieve the JSON answer.
        Finally returns the result

        :param query: SPARQL query
        Eg. 'SELECT distinct ?s as ?res WHERE{?s a <http://dbpedia.org/ontology/Election>} LIMIT 1000 OFFSET '
        :param offset: is the offset served to sparql service in order to get res from "offset" to "offset"+1000
        :return: res_list is a list of resources, typically 1000 resources
        """
        try:
            # composing the url with the help of url_composer and passing the offset, along with the service required
            url_res_list = self.url_composer(query + str(offset), 'dbpedia')
            # call to the web service with json_answer_getter(url_res_list) and obtain a json answer
            answer = self.json_answer_getter(url_res_list)
            # the actual res_list resides in answer['results']['bindings']
            res_list = answer['results']['bindings']
            return res_list
        except:
            logging.info("Lost resources with this offset range: " + str(offset) + " / " + str(offset + 1000))
            print ("ERROR RETRIEVING RESOURCES FROM " + str(offset) + " TO " + str(offset + 1000))

    def ask_if_resource_exists(self, resource):
        """
        This method asks to a dbpedia sparql endpoint if a resource exists or not.
        This is useful to compose the new dataset, so that it can be coherent with the DBpedia RDF dataset.

        :param resource: is the resource which existence you want to test
                        Eg.  Elezioni_presidenziali_negli_Stati_Uniti_d'America_del_1789 (it chapter) or
                             Bavarian_state_election,_2013 (en chapter)
        :return: response (true if the resource exists in the dataset, false otherwise)
        """
        try:
            query = "ASK { <" + resource + "> ?p ?o }"
            ask_url = self.url_composer(query, 'dbpedia')
            answer = self.json_answer_getter(ask_url)
            if "boolean" in answer:
                response = answer["boolean"]
                return response
            else:
                return False
        except:
            print("Exception asking if %s exists" % resource)
            return False

    def get_date_time(self):
        """
        It returns current YEAR_MONTH_DAY_HOUR_MINUTES as a string
        """
        timestamp = time.time()
        date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d-%H_%M')
        return date

    def get_date(self):
        """
        It returns current YEAR_MONTH_DAY as a string
        """
        timestamp = time.time()
        date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d')
        return date

    def print_report(self):
        """ Method used to print a final report of table extractor execution.

            It has statistics regarding # of:
            - Total res collected
            - Total res analyzed
            - Total tables found
            - Total rows successfully extracted
            - Total cells successfully extracted
            - Total errors trying to extract table's data
            - Total headers which the Parser wasn't able to resolve
            - Total errors trying to extract headers of a table
            - Total mapped cells
            - Total mapping errors
            - Total cells serialized in RDF triples

            Usually other classes set these values during their normal working cycle
            Simply call print_report() as last method of entire extraction
        """
        self.logging.info("REPORT:")
        # if the table_extractor is executed in single_res mode, no resources are collected from dbpedia sparql endpoints
        if self.res_collected:
            self.logging.info("+           # of resources collected for this topic (%s) : %d" % (self.topic, self.res_collected))

        self.logging.info("+           Total # resources analyzed: %d" % self.res_analyzed)

        self.logging.info("+           Total # tables found : %d" % self.tot_tables)

        self.logging.info("+           Total # tables analyzed : %d" % self.tot_tables_analyzed)

        self.logging.info("+           Total # of rows extracted: %d" % self.rows_extracted)

        self.logging.info("+           Total # of data cells extracted : %d" % self.data_extracted)

        self.logging.info("+           Total # of exceptions extracting data : %d" % self.data_extraction_errors)

        self.logging.info("+           Total # of \'header not resolved\' errors : %d" % self.not_resolved_header_errors)

        self.logging.info("+           Total # of \'no headers\' errors : %d" % self.headers_errors)

        self.logging.info("+           Total # of mapping errors : %d" % self.mapping_errors)

        self.logging.info("+           Total # of \'no mapping rule\' errors : %d" % self.no_mapping_rule_errors)

        self.logging.info("+           Total # cells mapped : %d" % self.mapped_cells)

        self.logging.info("+           Total # of triples serialized : %d" % self.triples_serialized)

    """ 
    Method used to delete all accented characters from the name of resource.
    It takes in input one string called text and gives in output another string that doesn't have accented characters
    that it's similar to the previous form.
    """
    def delete_accented_characters(self, text):
        try:
            unicode(text, "utf-8")
        except TypeError:
            nfkd_form = unicodedata.normalize('NFKD', text)
            text = nfkd_form.encode('ASCII', 'ignore')
        return text
