import argparse
import sys
import Selector
import rdflib
from table_extractor import Utilities, mapping_rules, HtmlTableParser, settings
from collections import OrderedDict


class ExplorerTools:
    """
    ExplorerTools implements all methods to support pyDomainExplorer.py
    In this script you will find functions that goes from parsing arguments given by user to get dbpedia resources.
    This is also an interface to class Utilities, HtmlTableParser from table_extractor, because
    I used some methods from those classes.

    """

    def __init__(self):
        """
        Initialize Explorer Tools, that will:
        - parse arguments given by user.
        - get an instance of Utilities.
        - get an instance of Selector, that will fetch dbpedia resources.
        """
        self.args = self.parse_arguments()
        self.research_type = None
        self.topic = self.set_topic()
        self.chapter = self.set_chapter()
        self.output = self.set_output_type()
        # declare pyTableExtractor Utilities
        self.utils = Utilities.Utilities(self.chapter, self.topic, self.research_type)

        # if user doesn't choose for single resource
        if not self.args.single:
            self.selector = Selector.Selector(self.utils)

    def parse_arguments(self):
        """
        Parse arguments given by user. You can observe three different inputs:
        - chapter: language specified by two letters.
        - output organization: number that can be 1 or 2, that will change settings file format.
        - mutual exclusive group:
            - s: single resource.
            - t: dbpedia ontology class.
            - w: where clause of sparql query built by user.
        :return: arguments passed by user
        """

        # initialize a argparse.ArgumentParser with a general description coming from settings.GENERAL_DESCRIPTION
        parser = argparse.ArgumentParser(description=settings.GENERAL_DESCRIPTION)

        """ chapter input"""
        parser.add_argument('-c', '--chapter', type=str, default=settings.CHAPTER_DEFAULT, help=settings.CHAPTER_HELP,
                            required=True)

        """ output organization input"""
        parser.add_argument('-o', '--output', help=settings.OUTPUT_HELP, type=int,
                            choices=settings.OUTPUT_CHOISES, default=settings.OUTPUT_DEFAULT, required = True)

        # A mutual exclusive group is used to contain --single or --topic or --where parameters.
        m_e_group = parser.add_mutually_exclusive_group(required=True)

        # -s|--single unicode string representing a single wiki page you want to analyze.
        m_e_group.add_argument('-s', '--single', type=lambda s: unicode(s, sys.getfilesystemencoding()),
                               help=settings.SINGLE_HELP)

        """-t|--topic string representing a topic or a scope. This scope is used to select a list of resources and
           particular mapping rules during the mapping moment."""
        m_e_group.add_argument('-t', '--topic', type=str, help=settings.TOPIC_HELP)

        # -w |--where string representing a custom where_clause. Please use ?s as the variable you are searching for.
        m_e_group.add_argument('-w', '--where', type=lambda s: unicode(s, sys.getfilesystemencoding()),
                               help=settings.WHERE_HELP)

        # parsing actual arguments and return them to the caller.
        args = parser.parse_args()
        return args

    def set_chapter(self):
        """
        Read and set chapter.
        :return: chapter value
        """
        if self.args.chapter:
            ch = self.args.chapter.lower()
            # search if language is available
            search = [x for x in settings.LANGUAGES_AVAILABLE if x == ch]
            if len(search) > 0:
                return search[0]
            else:
                sys.exit("Wrong chapter, languages available are: " + str(settings.LANGUAGES_AVAILABLE))

    def set_topic(self):
        """
        Read topic and set research_type to identify which input type is selected.
        :return: topic value
        """
        if self.args.topic:
            # topic search
            self.research_type = "t"
            if self.args.topic.isalpha():
                return self.args.topic
            else:
                sys.exit("Error writing DBpedia class - Class doesn't contain punctuation  characters")
        elif self.args.single:
            # single resource
            self.research_type = "s"
            return self.args.single
        elif self.args.where:
            # where clause defined by user
            self.research_type = "w"
            return self.args.where

    def set_output_type(self):
        """
        Read and set output organization. I will use a default value if user makes a mistake.
        :return: output organization value
        """
        if self.args.output:
            # check if output is correcy
            if len(str(self.args.output)) == 1 and self.args.output <= 2:
                return self.args.output
            else:
                # use default output organization if user wrote a wrong value
                print "Wrong output organization value, used default: " + settings.OUTPUT_DEFAULT
                return settings.OUTPUT_DEFAULT

    def get_uri_resources(self):
        """
        Read from Selector class resources that have been found.
        uri_resource_file stands for file that contain uri's list.
        uri_resource_list will contain a uri's list represented all resources.
        :return: list of uri
        """
        uri_resource_list = []
        # if it's not a single resource
        if not self.args.single:
            # if there are resource
            if self.selector.tot_res_interested > 0:
                self.selector.collect_resources()
                uri_resource_file = self.selector.res_list_file
                uri_resource_list = self.extract_resources(uri_resource_file)
            else:
                sys.exit("No resources found. Please check arguments passed to pyDomainExplorer")
        else:
            uri_resource_list.append(self.args.single)
        return uri_resource_list

    def extract_resources(self, uri_resource_file):
        """
        From uri_resource_file extract all resources.
        Delete last element that is empty due to '\n'
        :param uri_resource_file: file that contains resources' uri
        :return: list of uri
        """
        content = open(uri_resource_file).read().split('\n')
        # Last resource is empty due to '\n'
        content = content[:-1]
        return content

    def make_sparql_dbpedia(self, service, data):
        """
        Method for making a sparql query on dbpedia endpoint.

        :param service: type of service, in order to create a unique method to make sparql query.
        :param data: information to use in sparql query.
        :return: response given by dbpedia endpoint
        """
        url = ""
        if service == "check_property":
            # header as wrote in table
            query = settings.SPARQL_CHECK_PROPERTY[0] +\
                    '{' + settings.SPARQL_CHECK_PROPERTY[1] + '"' + data + '"@' + self.chapter + "} UNION " +\
                    '{' + settings.SPARQL_CHECK_PROPERTY[1] + '"' + data.lower() + '"@' + self.chapter + "}" +\
                    settings.SPARQL_CHECK_PROPERTY[2]
            # If I change chapter language of Utilities I will make a sparql query to dbpedia.org ontology
            self.utils.chapter = "en"
            self.utils.dbpedia_sparql_url = self.utils.dbpedia_selection()
            url = self.utils.url_composer(query, "dbpedia")
            # restore chapter given by user
            self.utils.chapter = self.chapter
            self.utils.dbpedia_sparql_url = self.utils.dbpedia_selection()
        # get endpoint's answer
        answer = self.utils.json_answer_getter(url)
        return answer

    def get_ontology_name_from_uri(self, uri):
        """
        Function to read only ontology property.

        :param uri: uri's resource
        :return: property name
        """
        # split by '/', i need last two elements (e.g. 'resource/Kobe_Bryant' or 'ontology/weight')
        split_uri = uri.split("/")
        res_name = split_uri[-1].encode('utf-8')
        return res_name

    def html_object_getter(self, name):
        """

        :param name: resource
        :return: html object that represents resource
        """
        return self.utils.html_object_getter(name)

    def read_actual_dictionary(self):
        """
        Read the pyTableExtractor dictionary. I will choose dictionary of the same language given by chapter.
        If user has written language different from english, I will load anyway english dictionary, because
        I can find something useful in that dictionary. (Remember that dbpedia is in english, and sometimes in
        wikipedia pages (that are written in italian or french) there are english terms)
        :return: pyTableExtractor dictionary
        """
        dictionary = OrderedDict()
        english_dictionary = None
        dictionary_name = settings.PREFIX_MAPPING_RULE + self.chapter.upper()
        if self.chapter != "en":
            english_dictionary = settings.PREFIX_MAPPING_RULE + "EN"
        for name, val in mapping_rules.__dict__.iteritems():  # iterate through every module's attributes
            if name == dictionary_name:
                dictionary = dict(val)
            elif english_dictionary and name == english_dictionary:
                dictionary.update(val)
        return dictionary

    def html_table_parser(self, res_name):
        """
        Method to instantiate HtmlTableParser, analyze tables and then give in output a list of tables.
        :param res_name: resource that has to be analyzed
        :return: list of tables found
        """
        html_doc_tree = self.html_object_getter(res_name)
        # if html doc is defined
        if html_doc_tree:
            graph = rdflib.Graph()
            # instantiate html table parser
            html_table_parser = HtmlTableParser.HtmlTableParser(html_doc_tree, self.chapter, graph,
                                                                self.topic, res_name, self.utils, False)
            # if there are tables to analyze
            if html_table_parser:
                # analyze and parse tables
                html_table_parser.analyze_tables()
                return html_table_parser.all_tables
            # if there aren't tables to analyze result will be empty
            else:
                return ""
        # if html doc is not defined result will be empty
        else:
            return ""

    def replace_accents(self, string):
        """
        Function that replace accented letters with the associated not accented letters

        :param string: string where you have to replace accents
        :return:  string without accents
        """
        return self.utils.delete_accented_characters(string)

    def get_res_list_file(self):
        """
        Get file that contains all resources.
        :return: file with resources
        """
        result = ""
        if not self.args.single:
            result = self.selector.res_list_file.split(settings.PATH_FOLDER_RESOURCE_LIST)[1].replace("/", "")
        return result

    def print_log_msg(self, log_type, msg):
        """
        Print a message to log file
        :param log_type: log type that can be info, warning and error depending on message type
        :param msg: message to print
        :return:
        """
        # info message in log
        if log_type == "info":
            self.utils.logging.info(msg)
        # warning message
        elif log_type == "warning":
            self.utils.logging.warning(msg)
        # exception message
        elif log_type == "exception":
            self.utils.logging.exception(msg)
        # error message
        elif log_type == "error":
            self.utils.logging.error(msg)

    def print_progress_bar(self, iteration, total):
        """
        Print iterations progress
        :param iteration: number of actual iteration
        :param total: total iteration to do
        :return: nothing, print progress bar
        """
        self.utils.print_progress_bar(iteration, total)
