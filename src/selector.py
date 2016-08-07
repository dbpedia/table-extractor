
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
    def __init__(self, lang, query, topic, utils):
        """

        :param lang:
        :param query:
        :param topic:
        """
        self.lang = lang
        self.where_clause = query
        self.topic = topic
        self.utils = utils
        self.last_res_list = None

        self.query_res_list = "SELECT distinct ?s as ?res WHERE{" + str(self.where_clause) + "} LIMIT 1000 OFFSET "
        self.query_num_res = "select (count(distinct ?s) as ?res_num) where{" + str(self.where_clause) + "}"

        self.current_res_list = []

        self.total_res_found = 0
        self.offset = 0
        self.res_num = 0
        self.tot_res_interested = self.utils.tot_res_interested(self.query_num_res)

        self.res_list_filename = self.set_file()

        # if os.path.isfile(self.res_list_filename):
        self.list = open(self.res_list_filename, 'w')
        self.utils.logging.info("The file which contains the list of resources is: " + self.res_list_filename)

        self.written = 0

    def set_file(self):
        self.utils.test_dir_existance('../Resource lists')
        current_dir = self.utils.get_current_dir()
        filename = self.topic + "_" + self.utils.get_date() + ".txt"
        path_to_file = self.utils.join_paths(current_dir, '../Resource lists/' + filename)
        return path_to_file

    def collect_resources(self):
        """
        It is  intended to iterate 1000 resources at once
        :return:
        """
        while self.offset <= self.total_res_found:
            try:
                self.current_res_list = self.utils.dbpedia_res_list(self.query_res_list, self.offset)
                for res in self.current_res_list:
                    try:
                        res_name = res['res']['value'].replace("http://" + self.utils.dbpedia + "/resource/", "")
                        res_name = res_name.encode('utf-8')
                        self.list.write(str(res_name)+'\n')
                        self.written += 1

                    except:
                        self.utils.logging.exception("Something went wrong writing down this resource: " + str(res))
                        print("exception for: "+str(res))
                self.__update_offset()

            except:
                print "exception during the iteration of collection of resources"
        self.list.close()
        self.utils.logging.info("Written down resources:  " + str(self.written))

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
