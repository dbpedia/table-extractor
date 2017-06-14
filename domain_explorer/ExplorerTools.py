import argparse
import settings_domain_explorer as settings
import sys
from table_extractor import Utilities, mapping_rules,HtmlTableParser
from collections import OrderedDict

class ExplorerTools:

    def __init__(self):
        self.args = self.parse_arguments()
        self.research_type = None
        self.topic = self.set_topic()
        self.chapter = self.set_chapter()
        self.verbose = self.set_verbose()
        self.utils = Utilities.Utilities(self.chapter, self.topic, self.research_type)

    def parse_arguments(self):

        # initialize a argparse.ArgumentParser with a general description coming from settings.GENERAL_DESCRIPTION
        parser = argparse.ArgumentParser(description=settings.GENERAL_DESCRIPTION)

        """ chapter input"""
        parser.add_argument('-c', '--chapter', type=str, default=settings.CHAPTER_DEFAULT, help=settings.CHAPTER_HELP)

        """ verbose input"""
        parser.add_argument('-v', '--verbose', help=settings.VERBOSE_HELP, type=int,
                            choices=settings.VERBOSE_CHOISES, default=settings.VERBOSE_DEFAULT)

        # A mutual exclusive group is used to contain --single or --topic or --where parameters.
        m_e_group = parser.add_mutually_exclusive_group()

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
        if self.args.chapter:
            if self.args.chapter.isalpha() and len(self.args.chapter) == 2:
                return self.args.chapter.lower()
            else:
                return settings.CHAPTER_DEFAULT

    def set_topic(self):
        if self.args.topic:
            self.research_type = "t"
            if self.args.topic.isalpha() and len(self.args.topic) > 2:
                return self.args.topic
            else:
                return settings.DOMAIN_DEFAULT
        elif self.args.single:
            self.research_type = "s"
            return self.args.single
        elif self.args.where:
            self.research_type = "w"
            return self.args.where

    def set_verbose(self):
        if self.args.verbose:
            if len(str(self.args.verbose)) == 1:
                return self.args.verbose
            else:
                return settings.VERBOSE_DEFAULT

    """
    Get uri of all domain's resources.
    """

    def get_uri_resources(self):
        # Metto in inglese per rifarmi all'ontology e scaricare le risorse
        uri_resource_list = []
        if not self.args.single:
            if self.args.topic:
                answer = self.make_sparql_dbpedia("resources", self.topic)
            else:
                answer = self.make_sparql_dbpedia("resources", self.args.where)

            # Compose resource list with all the class uri
            for value in answer["results"]["bindings"]:
                uri_resource_list.append(value["s"]["value"])
        else:
            uri_resource_list.append(self.args.single)
        return uri_resource_list

    """
    Function for making a dbpedia sparql query
    """

    def make_sparql_dbpedia(self, service, data):
        query = ""
        if service == "check_property":
            query = settings.SPARQL_CHECK_PROPERTY[0] + data.lower() + settings.SPARQL_CHECK_PROPERTY[1]
        elif service == "resources":
            where_clause = self.set_where_clause(data)
            query = settings.SPARQL_GET_RESOURCES[0] + where_clause + settings.SPARQL_GET_RESOURCES[1]
        url = self.utils.url_composer(query, "dbpedia")
        answer = self.utils.json_answer_getter(url)
        return answer

    """
    Get the resource name from uri.
    """

    def get_resource_name_from_uri(self, uri):
        res_name = uri.replace("http://" + self.utils.dbpedia + "/resource/", "")
        res_name = res_name.encode('utf-8')
        return res_name

    def html_object_getter(self, name):
        return self.utils.html_object_getter(name)


    """
    Read the dictionary of pyTableExtractor. The script will update this dictionary with information given by user
    """

    def read_actual_dictionary(self):
        dictionary = OrderedDict()
        dictionary_name = settings.PREFIX_MAPPING_RULE + self.chapter.upper()
        for name, val in mapping_rules.__dict__.iteritems():  # iterate through every module's attributes
            if name == dictionary_name:
                dictionary = dict(val)
        return dictionary


    def html_table_parser(self,html_doc_tree, chapter, graph,topic, res_name):
        return HtmlTableParser.HtmlTableParser(html_doc_tree, chapter, graph, topic, res_name,self.utils)

    """
    Write dictionary in a file. Verbose is a variable for defining which output's type produce.
    1 - print all in output file.
    2 - print only resources that aren't mapped in the actual dictionary.
    3 - print only one time the same header.
    """

    def print_dictionary_on_file(self, file, dict, verbose,all_headers):
        for key, value in dict.items():
            if verbose == 1:
                file.write("'" + key + "':'" + value + "'" + ", \n")
            elif verbose == 2 and value == "":
                file.write("'" + key + "':'" + value + "'" + ", \n")
            elif verbose == 3:
                if key != settings.SECTION_NAME_PROPERTY and all_headers[key] != "printed":
                    file.write("'" + key + "':'" + value + "'" + ", \n")
                    all_headers.__setitem__(key, "printed")
                elif key == settings.SECTION_NAME_PROPERTY:
                    file.write("'" + key + "':'" + value + "'" + ", \n")

    """
    Define where clause for getting resources
    """
    def set_where_clause(self,data):
        result = ""
        if self.args.where:
            result = data
        elif self.args.topic:
            result = "?s ?o <http://dbpedia.org/ontology/" + data + ">"
        return result