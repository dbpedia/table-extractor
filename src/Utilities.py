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


__author__='papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class Utilities:
    # TODO DOCSTRINGS
    """

    """
    def __init__(self, lang, topic):





        self.lang = lang
        self.topic = topic

        self.setup_log()

        self.jsonpedia_call_format = settings.jsonpedia_call_format
        self.jsonpedia_section_format = settings.jsonpedia_section_format
        self.jsonpedia_tables_format = settings.jsonpedia_tables_format
        self.call_format_sparql = settings.call_format_sparql

        self.jsonpedia_base_url = settings.jsonpedia_base_url
        self.jsonpedia_lan = lang + ":"
        self.dbpedia = None

        self.dbpedia_sparql_url = self.dbpedia_selection()
        self.html_format = "https://" + lang + ".wikipedia.org/wiki/"
        self.res_lost_jsonpedia = 0

        self.parser = etree.HTMLParser(encoding='utf-8')

        self.test_dir_existance('../Extractions')

        self.logging = logging

        # Variables used in final report see print_report()
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

        self.test_dir_existance('../Extractions')
        current_dir = self.get_current_dir()
        filename = "TableExtraction_" + self.topic + "_" + self.lang + "_(" + current_date_time + ")" + ".log"
        path_desired = self.join_paths(current_dir, '../Extractions/' + filename)

        logging.basicConfig(filename=path_desired, filemode='w', level=logging.DEBUG,
                            format='%(levelname)-3s %(asctime)-4s %(message)s', datefmt='%m/%d %I:%M:%S %p')

        # brief stat at the beginning of log, it indicates the scope of data and wiki/dbpedia chapter
        logging.info("You're analyzing wiki tables, wiki chapter: " + self.lang + ", topic: " + self.topic)

    def test_dir_existance(self, directory):
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

        :return:
        """
        if self.lang != "en":
            self.dbpedia = self.lang + ".dbpedia.org"
        else:
            self.dbpedia = "dbpedia.org"
        return "http://" + self.dbpedia + "/sparql?default-graph-uri=&query="

    def url_composer(self, query, service):
        """
        This function is used to compose a url to call some std services used by the selector,
        such as sparql endpoints or as jsonpedia rest service.
        Before returning the url composed, the method replaces
        :param query: is the string used in some rest calls. For a jsonpedia service is typically the resource name.
        :param service: type of service you request (jsonpedia, dbpedia sparql endpoint..)
        :return url: the url composed
        """
        # TODO conditions for dbpedia/jsonpedia services
        query = urllib.quote_plus(query)
        if service == 'dbpedia':
            url = self.dbpedia_sparql_url + query + self.call_format_sparql

        elif service == 'jsonpedia':
            url = self.jsonpedia_base_url + self.jsonpedia_lan + query + self.jsonpedia_call_format

        elif service == 'jsonpedia_tables':
            url = self.jsonpedia_base_url + self.jsonpedia_lan + query + self.jsonpedia_tables_format

        elif service == 'jsonpedia_sections':
            url = self.jsonpedia_base_url + self.jsonpedia_lan + query + self.jsonpedia_section_format

        elif service == 'html':
            url = self.html_format+query

        else:
            url = "ERROR"
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
        except IOError:
            print ("Try, again, some problems due to Internet connection, url: "+url_passed)
            return "Internet problems"
        except ValueError:
            print ("Not a JSON object.")
            return "ValueE"
        except:
            print "Exception with url:" + str(url_passed)
            return "GeneralE"

    def html_answer(self, url_passed):
        try:
            call = urllib.urlopen(url_passed)
            html_document = lxml.html.parse(call, self.parser)
            return html_document
        except IOError:
            print ("Try, again, some problems due to Internet connection, url: " + url_passed)
            return "Internet problems"
        except ValueError:
            print ("Not a JSON object.")
            return "ValueE"
        except:
            print "Exception with url:" + str(url_passed)
            return "GeneralE"

    def json_object_getter(self, resource, struct='jsonpedia'):
        """
        :param resource:
        :param struct:
        :return:
        """
        jsonpedia_url = self.url_composer(resource, struct)
        json_object_state = 'try'
        while json_object_state == 'try':
            try:
                json_answer = self.json_answer_getter(jsonpedia_url)
                if type(json_answer) != str:
                    json_object_state = self.test_json_result(json_answer)
            except:
                print("Error during json_object_getter")
        print(json_object_state)
        return json_answer

    def html_object_getter(self, resource):
        html_url = self.url_composer(resource, 'html')
        answer_ok = 'try'
        while answer_ok == 'try':
            try:
                html_answer = self.html_answer(html_url)
                if type(html_answer) != str:
                    answer_ok = self.test_html_result(html_answer)
            except:
                print("Error trying to get html object")
        print("Html document well formed..")
        return html_answer

    def test_json_result(self, json_obj):
        if 'message' in json_obj.keys():
            # TODO think about the possibility of write down problems encountered
            message = json_obj['message']
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

            elif len(json_obj) == 3:
                print "Problems related to JSONpedia service :" + str(json_obj) + " - RETRYING"
                return 'try'
        else:
            return 'JSON object well formed'

    def test_html_result(self, html_doc):
        # TODO implement a test on html_object
        """if 'message' in json_obj.keys():
            # TODO think about the possibility of write down problems encountered
            message = json_obj['message']
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

            elif len(json_obj) == 3:
                print "Problems related to JSONpedia service :" + str(json_obj) + " - RETRYING"
                return 'try'

        else:"""
        return 'JSON object well formed'

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
        This method retrieve a list of 1000 resources.

        :param query:
        :param offset: is the offset served to sparql service in order to get res from "offset" to "offset"+1000
        :return: res_list is a vector of resources, typically 1000 resources
        """
        try:
            url_res_list = self.url_composer(query + str(offset), 'dbpedia')
            answer = self.json_answer_getter(url_res_list)
            res_list = answer['results']['bindings']
            return res_list
        except:
            logging.info("Lost resources with this offset range: " + str(offset) + " / " + str(offset + 1000))
            print ("ERROR RETRIEVING RESOURCES FROM " + str(offset) + " TO " + str(offset + 1000))

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
        # if the Table Extractor is executed in single_res mode, no resources are collected from dbpedia sparql endpoints
        if self.res_collected:
            self.logging.info("# of resources collected for this topic (%s) : %d" % (self.topic, self.res_collected))

        self.logging.info("Total # resources analyzed: %d" % self.res_analyzed)

        self.logging.info("Total # tables found : %d" % self.tot_tables)

        self.logging.info("Total # tables analyzed : %d" % self.tot_tables_analyzed)

        self.logging.info("Total # of rows extracted: %d" % self.rows_extracted)

        self.logging.info("Total # of data cells extracted : %d" % self.data_extracted)

        self.logging.info("Total # of exceptions extracting data : %d" % self.data_extraction_errors)

        self.logging.info("Total # of \'header not resolved\' errors : %d" % self.not_resolved_header_errors)

        self.logging.info("Total # of \'no headers\' errors : %d" % self.headers_errors)

        self.logging.info("Total # of mapping errors : %d" % self.mapping_errors)

        self.logging.info("Total # of \'no mapping rule\' errors : %d" % self.no_mapping_rule_errors)

        self.logging.info("Total # cells mapped : %d" % self.mapped_cells)

        self.logging.info("Total # of triples serialized : %d" % self.triples_serialized)
