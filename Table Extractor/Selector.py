# coding=utf-8

import settings

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class Selector:
    """
    Class Selector is used to select which kind of wiki pages and so resources, have to be used in table's analysis.
    A selector object creates a .txt file filled with resources' name. Then this file will be used by the analyzer to have a
    set of resources to work with.

    Arguments:
        - chapter (str) # chapter of wikipedia Eg. en, it, de ..
        - where_clause (str) # part of a select query (WHERE) used to retrieve a list of resources from a sparql endpoint
        - topic (str) string representing the scope chose
        - utils (Utilities object) a Utilities object, useful to call dbpedia service depending on the chapter of interest

    Public methods:
        - collect_resources() # Used to start the process of resource collection

    """
    def __init__(self, chapter, where_clause, topic, utils):
        """
        :param chapter: chapter of interest, it has to be a 2 alpha-characters string (Eg. 'en','it','de'...)
        :param where_clause: a SPARQL where clause Eg. "?s a <http://dbpedia.org/ontology/SoccerPlayer>"
        :param topic: a topic of interest Eg. soccer, actors, writers...
        :param utils: a Utilities object which some methods are used to call a endpoint service.
        """
        # set the parameters
        self.chapter = chapter
        self.where_clause = where_clause
        self.topic = topic
        self.utils = utils

        self.last_res_list = None
        self.current_res_list = []

        # set the  SPARQL query used therefore to retrieve a list of 1000 resources at a time, see settings.py.
        self.query_res_list = settings.SPARQL_RES_LIST_QUERY[0] + str(self.where_clause) + \
                              settings.SPARQL_RES_LIST_QUERY[1]

        """ set the  SPARQL query used to know the total number of resources involved in collection.
           It then will be used by the collect_resources() method to augment the offset till the end of resources set"""
        self.query_num_res = settings.SPARQL_NUM_RES_QUERY[0] + str(self.where_clause) +\
                             settings.SPARQL_NUM_RES_QUERY[1]

        # set total number of resources interested in this topic passing the query_num_res to utils.tot_res_interested()
        self.tot_res_interested = self.utils.tot_res_interested(self.query_num_res)

        # self.total_res_found is the number of resources found by Selector
        self.total_res_found = 0
        # self.offset is the offset reached currently (it is updated 1000 by 1000)
        self.offset = 0
        # number of resources written in the .txt file
        self.resources_serialized = 0

        # set the  resources list filename using set_file()
        self.res_list_file = self.set_file()

        # open the list's file as self.list
        self.list = open(self.res_list_file, 'w')
        # Informing user where to find the file created
        self.utils.logging.info("The file which contains the list of resources is: %s" % self.res_list_file)

    def set_file(self):
        """
        Used to set the file which will contain the list of resources involved in this extraction
        :return: path_to_file  absolute path to the file we want to create
        """
        # call test_dir_existence() from Utilities class to test if '../Resource lists' exists.
        self.utils.test_dir_existence('../Resource lists')

        # get current directory
        current_dir = self.utils.get_current_dir()
        # compose list filename
        filename = self.utils.get_date() + "_" + self.topic + "_" + self.chapter + ".txt"
        # recreating abs path from 2 paths
        path_to_file = self.utils.join_paths(current_dir, '../Resource lists/' + filename)
        return path_to_file

    def collect_resources(self):
        """
        This method is used to iterate (1000 in 1000) over the resources retrieved by a dbpedia sparql endpoint.
        Those resources represent wiki pages. They are written in the list file only with the name of resource:
        Eg. the answer from the endpoint is "http://dbpedia.org/resource/Barack_Obama" and we want just "Barack_Obama"
        :return: After the list file has been serialized, it returns nothing
        """
        # Iterate until the offset is <= the total number of resources from that set
        while self.offset <= self.total_res_found:
            try:
                # acquiring a list [] of resources calling utils.dbpedia_res_list(query_res_list, offset)
                self.current_res_list = self.utils.dbpedia_res_list(self.query_res_list, self.offset)
                # for every resource in the list of resources just retrieved
                for res in self.current_res_list:
                    try:
                        # set the res_name which resides under res['res']['value'] and replace useless parts
                        res_name = res['res']['value'].replace("http://" + self.utils.dbpedia + "/resource/", "")
                        # encode res_name in utf-8
                        res_name = res_name.encode('utf-8')
                        # write the resource in the file with a newline tag
                        self.list.write(str(res_name)+'\n')
                        # update the number of resources serialized
                        self.resources_serialized += 1

                    except:
                        self.utils.logging.exception("Something went wrong writing down this resource: %s" % res)
                        print("exception for: %s" % res)

                # update the offset before a new iteration (while cycle)
                self.__update_offset()

            except:
                print "exception during the iteration of collection of resources"
        # close the file
        self.list.close()

        self.utils.logging.info("Resources found and serialized:  %s" % self.resources_serialized)
        # Update number of resources collected in utilities in order to print a final report
        self.utils.res_collected = self.resources_serialized

    def get_chapter(self):
        """

        :return:
        """
        return self.chapter

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
        Add 1000 to the offset

        """
        self.offset += 1000
