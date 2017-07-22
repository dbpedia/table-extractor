# coding=utf-8
import rdflib

resources_found = []


class Mapper:
    """
    Mapper is a class used to choose mapping rules to apply over data extracted from a wiki table.

    It fundamentally use topic and the wiki chapter to choose which method to use in order to map data passed to
    the class as an argument (table_data).
    Please, use map() method to start mapping process

    Public methods:
        -map() # used to start the mapping process and so fulfill the RDF graph

    """

    def __init__(self, chapter, graph, topic, resource, table_data, utils, index, table_section=None):
        """
        Mapper is a class used to choose mapping rules over refined cells of data in order to compose a rdf dataset.

        It uses chapter and topic to choose which method use in a extraction.
        Once you have created a mapper object, simply call map() method

        :param chapter (str): a two alpha-characters string representing the chapter of wikipedia user chose.
        :param graph: (rdflib graph) graph which will contain our RDF triples set
        :param topic (str): a string representing the common topic of the resources considered.
        :param resource (str): string representing the resource we are analyzing
        :param table_data: (list) list of data rows. Every row is a unique dictionary containing  'header1':[values1]
            and so on.
        :param utils (Utilities object): utilities object used to access common log and to set statistics values used to
                print a final report.
        :param index: last row's number of a resource added to graph
        :param table_section: (str) string representing section under which this table resides
        """
        # parameters are registered in the object
        self.chapter = chapter
        self.graph = graph
        self.topic = topic
        self.table_section = table_section
        self.table_data = table_data
        self.utils = utils
        self.logging = utils.logging
        self.resource = self.utils.delete_accented_characters(resource)
        self.dictionary = self.utils.dictionary

        # Reification_index is and index used to make a reification possible. It use the concept of row.
        self.reification_index = index

        # array to print key in log file only one time
        self.printed_key = []

        # Defining namespace used by the rdf graph
        self.dbo = None
        self.dbr = None
        self.dbp = None
        self.db = None
        self.define_namespace()
        self.filter_table_data()

    def define_namespace(self):
        """
        Method used to set standard names (dbr stands for dbpediaresource, dbp for dbpediaproperty,
          dbo for dbpediaontology)

        :return:
        """

        if self.chapter != 'en':
            self.dbr = rdflib.Namespace("http://" + self.chapter + ".dbpedia.org/resource/")
        else:
            self.dbr = rdflib.Namespace("http://dbpedia.org/resource/")

        self.dbo = rdflib.Namespace("http://dbpedia.org/ontology/")
        self.dbp = rdflib.Namespace("http://dbpedia.org/property/")

    def map(self):
        """
        Method used to map table data choosing correct mapping rules.

        It will use dictionary to map section and headers table to the property defined by user.

        :return:
        """

        # in row[cell] (that is table's cell value) contains even link in first position
        for row in self.table_data:
            # link with between resource section property and each section's row
            section_property, section_row_property = self.define_row_and_section_property()
            # if i find a section property that is defined
            if section_property:
                self.reification_index += 1
                self.add_triple_to_graph(self.dbr + self.resource, self.dbo + section_property, section_row_property)
                self.utils.triples_row += 1
                for cell in row:
                    value = self.extract_value_from_cell(row[cell])
                    # character "-" means that cell is empty
                    if value != '-':
                        dictionary_property = self.search_on_dictionary(self.table_section + "_" + cell)
                        if dictionary_property:
                            self.add_triple_to_graph(section_row_property, self.dbo + dictionary_property, value,
                                                     type="cell")
                            self.utils.mapped_cells += 1

    def extract_value_from_cell(self, cell):
        """
        Cell can be a link and value or only a value
        :param cell: table's cell
        :return: value of cell
        """
        # take only value's cell and not possible link
        if len(cell) > 1:
            value = cell[-1]
        else:
            value = cell
        if isinstance(value, list):
            return value[0]
        else:
            return value

    def define_row_and_section_property(self):
        """
        Method to search property of section and to create row's resource with its own index
        :return: section property and row resource
        """
        resource = self.resource.replace("'", "")
        section_property = self.search_on_dictionary(self.table_section)
        section_row_property = self.dbr + self.resource + "__" + str(self.reification_index)
        return section_property, section_row_property

    def add_triple_to_graph(self, subject, prop, value, type="row"):
        """
        Simply add triple to graph
        :param subject: subject of triple
        :param prop: property of triple
        :param value: value of triple (value has to check type of value)
        :param type: can be "row" if i'm adding a row triple or something else if it's a simple triple.
        :return: nothing
        """
        subject = rdflib.URIRef(subject)
        prop = rdflib.URIRef(prop)
        # check if i'm working with rows or single header
        if type == "row":
            value = rdflib.URIRef(value)
        else:
            value = self.check_value_type(value)
        # print subject, prop, value
        self.graph.add((subject, prop, value))

    def check_value_type(self, value):
        """
        Check type of a value that I'm analyzing
        :param value to check
        :return: value that are casted to a rdflib type (float, string or uri if it's a resource)
        """
        # i can have input value like list or like single input, i need to make a filter and get
        # unique element of this list
        result = value
        if self.is_float(result):
            data_type = rdflib.namespace.XSD.float
        elif self.is_int(result):
            data_type = rdflib.namespace.XSD.int
        else:
            # If this string represents a resource
            resource = self.check_if_is_resource(result)
            if resource:
                return rdflib.URIRef(resource)
            else:
                data_type = rdflib.namespace.XSD.string
        return rdflib.Literal(result, datatype=data_type)

    def check_if_is_resource(self, resource):
        """
        Make a SPARQL query in dbpedia dataset to know if exists a resource named in a particular way
        :param resource: name of resource that you want to check if it's a reresource
        :return:
            - empty if it's not a resource
            - uri of resource if it exists
        """
        resource_to_search = self.adjust_resource(resource)
        saved_resource = [r for r in resources_found if r in resource_to_search]
        if not saved_resource:
            if self.utils.ask_if_resource_exists(self.dbr + self.utils.delete_accented_characters(resource_to_search)):
                resources_found.append(resource_to_search)
                result = self.dbr + resource_to_search
            else:
                result = ""
        else:
            result = self.dbr + saved_resource[-1]
        return result

    def adjust_resource(self, text):
        """
        Remove space from beginning and ending of a string.
        After that I replace other spaces with _ in order to get a resource suitable for uri
        :param text: string to process
        :return: string without blank spaces
        """
        if text.startswith(" "):
            text = text[1:]
        if text.endswith(" "):
            text = text[:-1]
        text = text.replace(" ", "_")
        return text

    def search_on_dictionary(self, key):
        """
        Search over dictionary previously defined for header or section that is passed to this method
        :param key: string that you want to search over dictionary
        :return: two possible retrive:
                - empty if 'key' is not defined in dictionary
                - property associated to 'key' if this exists
        """
        try:
            # if verbose is 2 i have to make a deep search ( i will search for same key (eg. 3P%) in different sections)
            if self.utils.verbose == "2" and key != self.table_section:
                header = key.split("_")[1]
                return self.dictionary[header]
            else:
                return self.dictionary[key]
        except KeyError:
            # there's no mapping rule in dictionary for this header ( deep search isn't for table section)
            self.utils.no_mapping_rule_errors += 1
            already_printed = [x for x in self.printed_key if x == key]
            if len(already_printed) == 0:
                self.printed_key.append(key)
                print "Key '", key, "' not found. Check actual dictionary on mapping_rules.py"
                self.logging.warn("Key " + key + " not found. Check actual dictionary on mapping_rules.py")
            return ""

    def is_float(self, value):
        """
        Test out if a value passed as parameter is a float number
        :param value: a string you want to test
        :return: True if value is a float | False otherwise
        """
        try:
            float(value)
            return True
        except TypeError:
            return False
        except ValueError:
            return False

    def is_int(self, value):
        """
        Test out if a value passed as parameter is an integer
        :param value: a string you want to test
        :return: True if the value is an integer | False otherwise
        """
        try:
            int(value)
            return True
        except TypeError:
            return False
        except ValueError:
            return False

    def filter_table_data(self):
        """
        This method is used to delete last table's row if it represents sum or mean of previous values.
        It's useful in order to not create triples for this type of information
        :return:
        """
        table_list = dict()
        n = len(self.table_data)
        i = 0
        # variables used to count how many cells of last row contains sum or mean of previously cell's value in
        # same column
        summarized = 0
        num_cols = 0
        for row in self.table_data:
            for cell in row:
                value = self.extract_value_from_cell(row[cell])
                if self.is_float(value) or self.is_int(value):
                    # i have to avoid last row
                    if i < n - 1:
                        try:
                            new_value = table_list[cell] + value
                            table_list.__setitem__(cell, new_value)
                        except KeyError:
                            table_list.__setitem__(cell, value)
                    else:
                        try:
                            mean_value = (table_list[cell]/(n-1))
                            # check if last row is sum or mean value of cells
                            if value == table_list[cell] or str(value) == str(mean_value):
                                summarized += 1
                                num_cols = len(row)
                        except KeyError:
                            continue
            i += 1
        # delete last row if summarized is higher than 1 or 2
        if summarized >= 2:
            del self.table_data[-1]
            # for a well done statistic, i have to decrease data_extracted so that it will not represents
            # even summary rows (like Career in athlete tables)
            self.utils.data_extracted -= num_cols
