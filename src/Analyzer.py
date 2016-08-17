import sys

import rdflib

import HtmlTableParser
import JsonTableParser

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class Analyzer:
    # TODO DOCSTRINGS
    """

    """

    def __init__(self, chapter, topic, utils, mode="html", filename=None, single_res=None):
        self.chapter = chapter
        self.topic = topic
        self.utils = utils
        self.logging = self.utils.logging
        self.filename = filename
        self.mode = mode
        self.logging.info(self.mode + " mode activated.. ")

        self.res_analyzed = 0
        self.total_table_num = 0

        self.current_resource = None
        # composing a list of resources from the file (filename) passed
        if self.filename:
                self.open_stream()
                self.res_list = self.open_file()
                # instancing a iterator
                try:
                    self.res_iterator = iter(self.res_list)
                except TypeError:
                    print "Check the file's existence "
                    sys.exit(0)
        else:
            self.res_iterator = iter([single_res])


        self.lines_to_read = True
        self.last_json_object = None

        self.graph = rdflib.Graph()

    def open_file(self):
        """
        open_file is used to open a input stream from a file.
        Filename has to be set in self.filename, or an IOError Exception is raised.
        :return: the function returns lines from the file opened.
        """
        try:
            file_opened = open(self.filename, 'r')
            return file_opened.readlines()
        except IOError:
            print "IOError opening the file: " + str(self.filename)

    def open_stream(self):
        if self.filename:
            self.res_list = self.open_file()
            self.res_iterator = self.setup_iterator()
        else:
            print " File name not set, please check it. "
            sys.exit(0)

    def setup_iterator(self):
        try:
            res_iterator = iter(self.res_list)
            return res_iterator
        except TypeError:
            print "Check file's existence. "
            sys.exit(0)

    def analyze(self):
        """

        :return:
        """
        while self.lines_to_read:
            try:
                resource = self.res_iterator.next()
                resource = resource.replace("\n", "")
                self.logging.info("Analyzing " + str(resource))
                self.res_analyzed += 1
                print("Analyzing " + str(resource))
                if resource:
                    self.current_resource = resource
                    if self.mode == "json":

                        json_object = self.utils.json_object_getter(resource, 'jsonpedia_sections')
                        t_parser = JsonTableParser.JsonTableParser(json_object, self.chapter, self.graph, self.topic, resource)
                        t_parser.analyze_tables()

                    elif self.mode == "html":
                        html_doc_tree = self.utils.html_object_getter(resource)
                        html_parser = HtmlTableParser.HtmlTableParser(html_doc_tree, self.chapter, self.graph, self.topic, resource, self.utils)
                        html_parser.analyze_tables()

                        # Add to the total the tables for this resource
                        self.total_table_num += html_parser.tables_num


                    else:
                        print("mode")
            except StopIteration:
                self.lines_to_read = False
                self.utils.res_analyzed = self.res_analyzed
                self.logging.info("End Of File reached, now you can serialize the graph")
                print (" End Of File reached")

    def get_filename(self):
        """
        It returns the filename set to this analyzer.
        It is intended to be a txt file with a list of wiki resources divided by newline tag.
        :return: filename
        """
        return self.filename

    def serialize(self):
        """

        :return:
        """
        # serialize the graph if only contains triples
        if len(self.graph) > 0:

            cur_dir = self.utils.get_current_dir()
            if self.topic == 'single_resource':
                self.topic = "single_res_" + str(self.current_resource)
            filename = "T_Ext_" + self.mode + '_' + self.chapter + '_' + self.topic + '_(' + self.utils.get_date_time() + ").ttl"
            destination = self.utils.join_paths(cur_dir, '../Extractions/'+filename)

            rdf_format = "turtle"
            self.graph.serialize(destination, rdf_format)

            self.logging.info('Triples in the graph: ' + str(len(self.graph)))
            # updating triples serialized for report purpose
            self.utils.triples_serialized = len(self.graph)
            print('Graph serialized, filename: ' + destination)
            self.logging.info('Graph serialized, filename: ' + destination)
        else:
            print('Something went wrong: Nothing to serialize')
            self.logging.warn('Nothing to serialize, you have to choose right scope or resource, \
                            or something went wrong scraping tables')
