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
import unicodedata
import sys
import socket
import MapperTools

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class Utilities:
    """
    Utilities is a class containing a lot of methods and attributes used by the others class and modules.
    It requires only a 2 alpha-characters string representing a wiki chapter and a topic of interest.
    Topic is used mainly in reporting and composing filename for log while chapter is used to correctly address the
    outer service calls.

    Public methods:
    - setup_log()
    - test_dir_existence(directory_to_test) # to tests if a directory exists in current filesystem
    - get_current_dir() # returns current directory
    - join_paths(path1, path2) # use os.path to join tho relative paths

    - html_object_getter(resource) # return a html representation of the requested resource

    - tot_res_interested(query) # return the total number of the resources selected with the Sparql query passed as a
            parameter.
    - dbpedia_res_list(query, offset) # return 1000 resources at a time of the scope identified by 'query'
    - ask_if_resource_exists(resource) # test if a resource currently exists in the dbpedia endpoint RDF graph of
            reference.
    - get_date_time() # return YEAR_MONTH_DAY_HOUR_MINUTES
    - get_date() # return YEAR_MONTH_DAY
    - print_report() # print in the log metrics to evaluate efficiency of the script

    """

    def __init__(self, chapter, topic, research_type):

        self.chapter = chapter
        self.topic = topic
        self.research_type = research_type
        self.resource_file = None
        self.verbose = None
        # test if the directory ../Extractions exists (or create it)
        self.test_dir_existence('../Extractions')

        """
        update actual mapping rules and set chapter and topic, given by domain_settings.py
        """
        if not self.chapter:
            self.read_parameters_research()
            self.setup_log("extractor")
            self.extractor = True   # utilities called by extractor, so i need to update mapping rules
            self.mapper = MapperTools.MapperTools(self)
        else:
            self.setup_log("explorer")
            self.extractor = False

        # define a log
        self.logging = logging
        # use dbpedia_selection to set self.dbpedia and self.dbpedia_sparql_url
        self.dbpedia_sparql_url = self.dbpedia_selection()

        # These values are used to compose calls to services as Sparql endpoints or to a html wiki page
        self.call_format_sparql = settings.SPARQL_CALL_FORMAT

        # Parameters used in methods which need internet connection
        self.time_to_attend = settings.SECONDS_BTW_TRIES  # seconds to sleep between two internet service call
        self.max_attempts = settings.MAX_ATTEMPTS  # max number of internet service' call tries

        # check if user has written a class that exists in dbpedia ontology
        if self.research_type == "t":
            self.check_dbpedia_class()

        # self.dbpedia is used to contain which dbpedia to use Eg. dbpedia.org
        if self.chapter == "en":
            self.dbpedia = "dbpedia.org"
        else:
            self.dbpedia = self.chapter + ".dbpedia.org"

        # Instancing a lxml HTMLParser with utf-8 encoding
        self.parser = etree.HTMLParser(encoding='utf-8')

        self.html_format = "https://" + self.chapter + ".wikipedia.org/wiki/"

        # if Utilities class is called by pyTableExtractor
        if self.extractor:
            self.dictionary = self.mapper.update_mapping_rules()

        # define timeout for url request in order to don't wait too much time
        socket.setdefaulttimeout(settings.REQUEST_TIMEOUT)

        # Variables used in final report, see print_report()
        self.res_analyzed = 0
        self.res_collected = 0
        self.data_extracted = 0
        # data to map, that doesn't represents sum or mean of previous value
        self.data_extracted_to_map = 0
        self.tot_tables = 0
        self.tot_tables_analyzed = 0
        self.rows_extracted = 0
        self.data_extraction_errors = 0
        self.not_resolved_header_errors = 0
        self.headers_errors = 0
        self.no_mapping_rule_errors_headers = 0
        self.no_mapping_rule_errors_section = 0
        self.mapped_cells = 0
        self.triples_row = 0  # number of triples created for table's rows

    def setup_log(self, script_name):
        """
        Initializes and creates log file containing info and statistics
        """
        # getting time and date
        current_date_time = self.get_date_time()

        # obtain the current directory
        current_dir = self.get_current_dir()
        # composing the log filename as current_date_and_time + _LOG_T_EXT + chapter_chosen + topic_chosen
        if self.research_type == "w":
            filename = current_date_time + "_LOG_" + script_name + "_" + self.chapter + '_' + "custom" + ".log"
        else:
            filename = current_date_time + "_LOG_" + script_name + "_" + self.chapter + '_' + self.topic + ".log"
        # composing the absolute path of the log
        path_desired = self.join_paths(current_dir, '../Extractions/' + filename)

        # configuring logger
        logging.basicConfig(filename=path_desired, filemode='w', level=logging.DEBUG,
                            format='%(levelname)-3s %(asctime)-4s %(message)s', datefmt='%m/%d %I:%M:%S %p')

        # brief stat at the beginning of log, it indicates the  wiki/dbpedia chapter and topic selected
        logging.info("You're analyzing wiki tables, wiki chapter: " + self.chapter + ", topic: " + self.topic)

    def test_dir_existence(self, directory):
        """
        Test if directory exists
        :param directory: name of directory
        :return:
        """
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
        This function is used to compose a url to call some web services, such as sparql endpoints.

        :param query: is the string used in some rest calls.
        :param service: type of service you request (dbpedia sparql endpoint)
        :return url: the url composed
        """
        # use quote_plus method from urllib to encode special character (must to do with web service)
        query = urllib.quote_plus(query)

        """
        The following if clause are differentiated by service requested Eg. 'dbpedia',..
            but in all the cases url is composed using pre formatted string along with the query
        """
        if service == 'dbpedia':
            url = self.dbpedia_sparql_url + query + self.call_format_sparql

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
        :return json_parsed: the method returns the JSON parsed answer
        """
        attempts = 0
        result = ""
        while attempts < settings.MAX_ATTEMPTS:
            try:
                # open a call with urllib.urlopen and passing the URL
                call = urllib.urlopen(url_passed)
                # read the answer
                answer = call.read()
                # decode the answer in json
                json_parsed = json.loads(answer)
                # return the answer parsed
                result = json_parsed
                return result
            except IOError:
                print ("Try, again, some problems due to Internet connection or empty url: " + url_passed)
                attempts += 1
                result = "Internet problems"
            except ValueError:
                # print ("Not a JSON object.")
                result = "ValueE"
                attempts += 1
            except:
                print "Exception with url:" + str(url_passed)
                result = "GeneralE"
                attempts += 1
        return result

    def html_answer(self, url_passed):
        """
        Open url passed to method
        :param url_passed: url to analyze
        :return: html document of that url
        """
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

    def html_object_getter(self, resource):
        """
        Get html object of resource given in input
        :param resource: resource to transform in html
        :return: resource in html
        """
        html_url = self.url_composer(resource, 'html')
        is_answer_ok = False
        attempts = 0
        html_answer = None

        while is_answer_ok is not True and attempts < self.max_attempts:
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

    def test_html_result(self, html_doc):
        """
        Test if html document created is well-formed
        :param html_doc: html document to test
        :return:
            - True if html_doc is well-formed
            - False otherwise.
        """
        if type(html_doc) == str and "Error" in html_doc:
            return False
        else:
            return True

    def tot_res_interested(self, query):
        """
        Method used to retrieve the total number of resources (wiki pages) interested.
        It uses url_composer passing by the query to get the number of res.
        Then it sets tot_res as the response of a call to dbpedia sparql endpoint.
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
            return 0

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
            # print("Exception asking if %s exists" % resource)
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
            - Total of error of searching if a header has its own mapping rule
            - Total triples created to represent table's rows
            - Total triples created for table's cells
            - Total triples added to graph
            - Percentage of effectiveness of mapping process

            Usually other classes set these values during their normal working cycle
            Simply call print_report() as last method of entire extraction
        """
        self.logging.info("REPORT:")
        # if the table_extractor is executed in single_res mode, no resources are collected
        # from dbpedia sparql endpoints
        if self.res_collected:
            self.logging.info("+           # of resources collected for this topic (%s) : %d" %
                              (self.topic, self.res_collected))

        self.logging.info("+           Total # resources analyzed: %d" % self.res_analyzed)

        self.logging.info("+           Total # tables found : %d" % self.tot_tables)

        self.logging.info("+           Total # tables analyzed : %d" % self.tot_tables_analyzed)

        self.logging.info("+           Total # of rows extracted: %d" % self.rows_extracted)

        self.logging.info("+           Total # of data cells extracted : %d" % self.data_extracted)

        self.logging.info("+           Total # of exceptions extracting data : %d" % self.data_extraction_errors)

        self.logging.info("+           Total # of \'header not resolved\' errors : %d" %
                          self.not_resolved_header_errors)

        self.logging.info("+           Total # of \'no headers\' errors : %d" % self.headers_errors)

        if self.extractor:
            self.logging.info("+           Total # of \'no mapping rule\' errors for section : %d" %
                              self.no_mapping_rule_errors_section)

            self.logging.info("+           Total # of \'no mapping rule\' errors for headers : %d" %
                              self.no_mapping_rule_errors_headers)

            self.logging.info("+           Total # of data cells extracted that needs to be mapped: %d" %
                              self.data_extracted_to_map)

            self.logging.info("+           Total # of table's rows triples serialized : %d" % self.triples_row)

            self.logging.info("+           Total # of table's cells triples serialized : %d" % self.mapped_cells)

            self.logging.info("+           Total # of triples serialized : %d" % int(self.mapped_cells +
                                                                                     self.triples_row))

            if self.data_extracted_to_map > 0:
                effectiveness = self.mapped_cells/float(self.data_extracted_to_map)
            else:
                effectiveness = 0
            self.logging.info("+           Percentage of mapping effectiveness  : %.3f" % effectiveness)

    def delete_accented_characters(self, text):
        """
        Method used to delete all accented characters from the name of resource.
        It takes in input one string called text and gives in output another string that doesn't have accented
        characters that it's similar to the previous form.
        :param text: string where you have to delete accented charactes
        :return:
        """
        try:
            text = unicode(text, "utf-8")
            result = unicodedata.normalize('NFD', text).encode('ascii', 'ignore')
            return result
        except TypeError:
            return text

    def print_progress_bar(self, iteration, total, prefix='Progress: ', suffix='Complete', decimals=1, length=30,
                           fill='#'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))

    def read_parameters_research(self):
        """
        Read parameters defined in header of settings file
        :return: set all parameters of research
        """
        if os.path.isfile(settings.PATH_DOMAIN_EXPLORER):
            import domain_settings
            for name, val in domain_settings.__dict__.iteritems():
                # read domain
                if name == settings.DOMAIN_TITLE:
                    self.topic = val
                # read language
                elif name == settings.CHAPTER:
                    self.chapter = val
                # read research type (-s -t or -w)
                elif name == settings.RESEARCH_TYPE:
                    self.research_type = val
                # read name of resource's file
                elif name == settings.RESOURCE_FILE:
                    self.resource_file = val
                # read verbose value
                elif name == settings.VERBOSE_TYPE:
                    self.verbose = val
        else:
            sys.exit("File " + settings.PATH_DOMAIN_EXPLORER + " not found. You should running pyDomainExplorer")

    def validate_user_input(self):
        """
        Verify each option of settings file created. I have to notify user if he wrote something wrong in settings
        file's header
        :return: string that can be
            - 'valid_input' if it's all right
            - message that depend on type of error
        """
        result = "valid_input"
        # check chapter
        if len(self.chapter) != 2:
            result = "Chapter (" + self.chapter + ") is wrong, check domain_settings.py"
        # check research type
        if len(self.research_type) == 1:
            if self.research_type != "t" and self.research_type != "s" and self.research_type != "w":
                result = "Research type (" + self.research_type + ") is wrong, check domain_settings.py"
        else:
            result = "Research type (" + self.research_type + ") is wrong, check domain_settings.py"
        # check resource file
        if self.research_type != "s" and not os.path.isfile(self.get_resource_file()):
            result = "Resource file doesn't exists, check domain_settings.py"
        return result

    def get_resource_file(self):
        """
        :return: resource file
        """
        return settings.PATH_FOLDER_RESOURCE_LIST + "/" + self.resource_file

    def check_dbpedia_class(self):
        """
        Check if user has written a class that is in dbpedia ontology
        :return: nothing
        """
        # uri of class
        class_uri = "http://dbpedia.org/ontology/" + self.topic
        result = self.ask_if_resource_exists(class_uri)
        if not result:
            sys.exit("Class " + self.topic + " defined in arguments doesn't exist in DBpedia ontology")
