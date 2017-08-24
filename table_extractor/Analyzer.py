# coding=utf-8

import sys
import rdflib
import HtmlTableParser

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class Analyzer:
    """
    Analyzer class takes resources from a list and call a HtmlTableParser  over them.

    It takes resources from .txt file (generally created by Selector objects) or from a string if a single_resource is
     involved.
    Therefore a Table Parser object is called over their wiki page representation.
     This representation is retrieved by a utilities object (calling html_object_getter()).
    Once the list of resources is finished or the analysis of a resource is done some useful statistics values are set.
    Some of them are passed to the utilities object (res_analyzed), as they are useful to print a final cumulative
     report, while some others (headers with no mapping rules found) are just print out and to the log.
    They are used to give to the user an idea of which headers he can find in tables but which has not yet a
     corresponding mapping rule. This is so important, as tables in wiki pages (even in pages with same topic
     or describing the same phenomenons) are as well heterogeneous as the taste of users who wrote them.

    Public Methods:
        -analyze(): it is used to analyze a list of resources(or a single resource) passed once analyzer has been
            initialized. Once you have created Analyzer object simply call this method to begin the analysis.
            This method doesn't return nothing by itself as useful informations are printed out both in the log and
            in the console.

        -serialize(): method used to serialize the RDF graph fulfilled with triples during analysis (mapping) phase.
            it creates a .ttl file (serialization of the RDF graph).
            Filename and directory (it should be /Extractions) are reported in the log.
            Please call serialize() after analyze() method!
    """

    def __init__(self, chapter, topic, utils, filename=None, single_res=None):
        """
        Analyzer object takes resources from a list and call a TableParser (html |json) over them.

        Please, after initialization, use the analyze() method to start the analysis and the serialize() one to
         serialize the RDF graph.
        During the initialization a rdf graph is created (the class need rdflib to work) and a iterator is set over the
         list of resources or over the single_resource passed.

        Arguments:
        :param chapter (str): a two alpha-characters string representing the chapter of wikipedia user chose.
        :param topic (str): a string representing the common topic of the resources considered.
        :param utils (Utilities object): utilities object used to access common log and to set statistics values used to
                print a final report.
        :param filename (str): DEFAULT:None filename of a resources' list. It should be a .txt file containing name
            of wiki pages (with spaces replaced by underscores Eg. Elezioni_amministrative_italiane_del_2016).
            Note that filename is mutual exclusive with single_res (if one is set, the other should not)
        :param single_res (str): DEFAULT:None string with a single resource name, as for list of resources file,
            the name should have spaces replaced by underscores Eg. Elezioni_amministrative_italiane_del_2016
            Note that single_res is mutual exclusive with filename (if one is set, the other should not)

        """
        # parameters are registered in the object
        self.chapter = chapter
        self.topic = topic
        self.utils = utils
        self.logging = self.utils.logging  # just for reading comfort
        self.filename = filename
        self.single_res = single_res

        # These values are used to statistics purposes
        self.res_analyzed = 0  # number of resources correctly analyzed
        self.total_table_num = 0  # Extraction tables number

        self.res_list = None

        # setup a list of resources  from the file (filename) passed to __init__
        if self.filename:
                self.open_stream()
        else:
            # if self.filename == None, the single_res should be set, so use a iterator over it.
            self.res_iterator = iter([self.single_res])

        # boolean value to check if others lines are in the list file
        self.lines_to_read = True

        # Set a RDF graph, using rdflib. Ensure to have rdflib installed!
        self.graph = rdflib.Graph()

    def open_file(self):
        """
        open_file is used to open a input stream from a file.
        Filename has to be set in self.filename, and the file should exists or an IOError Exception is raised.
        :return: the function returns lines from the file opened.
        """
        try:
            # open file in read mode
            file_opened = open(self.filename, 'r')
            return file_opened.readlines()
        except IOError:
            print "IOError opening the file: " + str(self.filename)

    def setup_iterator(self):
        """
        setup_iterator tries to make a iterable object from self.res_list.

        Note: res_list should be set to a list of string (use open_file() method)
        :return:
        """
        try:
            res_iterator = iter(self.res_list)
            return res_iterator
        except TypeError:
            print "Check file's existence. "
            sys.exit(0)

    def open_stream(self):
        """
        open_stream() is used to set res_list (with a stream coming from file) and a res_iterator (see setup_iterator())

        If filename is set, setup res_list with a input stream coming from file (filename) and res_iterator with
         setup_iterator().
        :return: nothing
        """
        if self.filename:
            # set lines to be read
            self.res_list = self.open_file()
            # set the iterator from that self.res_list
            self.res_iterator = self.setup_iterator()
        else:
            print " File name not set, please check it. "
            sys.exit(0)

    def analyze(self):
        """
        This method iterates over a list of resources and setup a TableParser on a html representation of it.

        Then it uses the analyze_tables() method of Table Parsers to start the analysis process for tables of current
            resource.
        Finally, once the list of resources is empty, the method set some statistics value and print out headers with no
            adequate mapping rules.
        This last feature is useful to find out headers in tables of a specific topic with a name user or
         developer had not considered (to improve data mapped)
        :return: nothing
        """

        # lines_to_read is used to know when the iterator is finished.It is set to False once StopIteration is raised
        while self.lines_to_read:

            try:
                # set resource to the next element in the iterator
                resource = self.res_iterator.next()
                # delete newline tag from the resource name
                resource = resource.replace("\n", "")
                print("Analyzing " + str(resource))
                self.logging.info("Analyzing " + str(resource))
                # update res_analyzed index
                self.res_analyzed += 1
                if self.res_list:
                    # search over many resources
                    self.utils.print_progress_bar(self.res_analyzed, len(self.res_list))
                else:
                    # uses chose to analyze only one resource
                    self.utils.print_progress_bar(self.res_analyzed, 1)
                if resource:
                    html_doc_tree = self.utils.html_object_getter(resource)
                    if html_doc_tree:
                        """
                        Then a HtmlTableParser object is created and the tables for the current resource are
                            analyzed with HtmlTableParser.analyze_tables() method.
                        """
                        html_parser = HtmlTableParser.HtmlTableParser(html_doc_tree, self.chapter, self.graph,
                                                                      self.topic, resource, self.utils, mapping=True)
                        html_parser.analyze_tables()

                        # Add to the total the number of tables found for this resource
                        self.total_table_num += html_parser.tables_num
            except StopIteration:
                self.lines_to_read = False
                self.utils.res_analyzed = self.res_analyzed

                # Print out and in the log every header cell without mapping rule
                print("There are %d sections without mapping rules." % self.utils.no_mapping_rule_errors_section)
                self.logging.info("There are %d sections and sections without mapping rules" %
                                  self.utils.no_mapping_rule_errors_section)
                # Print out and in the log every section cell without mapping rule
                print("There are %d headers without mapping rules." % self.utils.no_mapping_rule_errors_headers)
                self.logging.info("There are %d headers and sections without mapping rules" %
                                  self.utils.no_mapping_rule_errors_headers)
                # end of resources involved
                self.logging.info("End Of File reached, now you can serialize the graph")
                print ("\nEnd Of Resource File reached")

    def get_filename(self):
        """
        It returns the filename set to this analyzer.
        It is intended to be a txt file with a list of wiki resources divided by newline tag.
        :return: filename
        """
        return self.filename

    def serialize(self):
        """
        Call serialize() when you want to serialize the RDF graph created with a Analyzer object.

        The graph should be fulfilled with triples during the mapping process, so analyze() method should be called
         before serialize() otherwise the graph would be empty.
        Messages are printed in console and in log file to update the user on the result.
        :return: nothing
        """
        # serialize the graph if only contains triples
        if len(self.graph) > 0:

            # get the current directory using utils.get_current_dir()
            cur_dir = self.utils.get_current_dir()

            # if this Extraction is over a single resource use single_res joined with the resource name as self.topic
            if self.topic == 'single_resource':
                self.topic = "single_res_" + str(self.single_res)

            # compose filename of the .ttl file
            if self.utils.research_type == "w":
                filename = self.utils.get_date_time() + "_T_Ext_" + self.chapter + "_custom.ttl"
            else:
                filename = self.utils.get_date_time() + "_T_Ext_" + self.chapter + '_' + \
                           self.topic + ".ttl"
            # join path of execution with that of ../Extraction
            destination = self.utils.join_paths(cur_dir, '../Extractions/'+filename)

            # setting the rdf_format
            rdf_format = "turtle"
            # serialize the graph using graph.serialize. It needs destination and the rdf format as parameters
            self.graph.serialize(destination, rdf_format)

            # Writing down triples number in the log
            self.logging.info('Triples in the graph: ' + str(len(self.graph)))

            # updating triples serialized for report purpose
            self.utils.triples_serialized = len(self.graph)

            # show the user result of serialization both in log and in console
            print('GRAPH SERIALIZED, filename: ' + destination)
            self.logging.info('Graph serialized, filename: ' + destination)

        # if no triple is in graph
        else:
            print('Something went wrong: Nothing to serialize')
            self.logging.warn('Nothing to serialize, you have to choose right scope or resource,'
                              'or something went wrong scraping tables')
