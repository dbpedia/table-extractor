# coding=utf-8
import rdflib
import settings

resources_found = []


class Mapper:
    """
    Mapper is a class used to choose mapping rules to apply over data extracted from a wiki table.

    It fundamentally use topic and the wiki chapter to choose which method to use in order to map data passed to
    the class as an argument (table_data).
    Please, use map() method to start mapping process

    Public methods:
        -map() # used to start the mapping process and so fulfill the RDF graph

    Properties:
        -triples_added_to_the_graph # number of triples added to the graph for this table
        -cells_mapped # number of cells correctly mapped for the current row
        -total_cell_mapped # number of cells correctly mapped for the current table
        -num_of_mapping_errors # number of exceptions during mapping process
        -no_mapping_found_cells # number of cells for which none of the mapping rules has been successful
        -headers_not_mapped # Headers for which the defined mapping rules have not been successful

    """

    def __init__(self, chapter, graph, topic, resource, table_data, utils, table_section=None):
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
        :param mode (str): string used to choose HtmlTableParser or JsonTableParser. Usually it is 'html' or 'json'.
        :param utils (Utilities object): utilities object used to access common log and to set statistics values used to
                print a final report.
        :param table_section: (str) string representing section under which this table resides
        """
        # parameters are registered in the object
        self.chapter = chapter
        self.graph = graph
        self.topic = topic
        self.resource = resource
        self.table_section = table_section
        self.table_data = table_data
        self.utils = utils
        self.logging = utils.logging
        self.dictionary = self.utils.dictionary

        # This dictionary  is used to have an idea of which headers haven't a mapping rule.
        self.headers_not_mapped = {}
        # Statistical values
        self.triples_added_to_the_graph = 0  # number of triples added to the graph
        self.cells_mapped = 0  # number of cells mapped for a certain row
        self.total_cell_mapped = 0  # total number of mapped cells for this table
        self.num_of_mapping_errors = 0  # number of mapping exceptions
        self.no_mapping_found_cells = 0  # number of cell for which no mapping rule has found

        # Reification_index is and index used to make a reification possible. It use the concept of row.
        self.reification_index = 1

        # array to print key in log file only one time
        self.printed_key = []

        # Defining namespace used by the rdf graph
        self.dbo = None
        self.dbr = None
        self.dbp = None
        self.db = None
        self.define_namespace()

    def define_namespace(self):
        """
        Method used to set standard names (dbr stands for dbpediaresource, dbp for dbpediaproperty,
          dbo for dbpediaontology)

        :param chapter: the wiki chapter of reference
        :return:
        """

        if self.chapter != 'en':
            self.dbr = rdflib.Namespace("http://" + self.chapter + ".dbpedia.org/resource/")
            self.db = rdflib.Namespace("http://" + self.chapter + ".dbpedia.org/")
        else:
            self.dbr = rdflib.Namespace("http://dbpedia.org/resource/")
            self.db = rdflib.Namespace("http://dbpedia.org/")

        self.dbo = rdflib.Namespace("http://dbpedia.org/ontology/")
        self.dbp = rdflib.Namespace("http://dbpedia.org/property/")

    def map(self):
        """
        Method used to map table data choosing correct mapping rules.

        It uses chapter to retrieve mapping rules for such wiki chapter, and topic to restrict mapping rules used.
        It prints out some mapping result in log and console and store statistical values in the Utilities object.
        These values are used to print a final report regarding the entire extraction.

        :return:
        """

        # in row[cell] (that is table's cell value) contains even link in first position
        for row in self.table_data:
            # link with between resource section property and each section's row
            section_property, section_row_property = self.define_row_and_section_property()
            # if i find a section property that is defined
            if section_property:
                self.reification_index += 1
                self.add_triple_to_graph(self.dbr + self.resource, self.db + section_property, self.db + section_row_property)
                self.utils.triples_serialized += 1
                for cell in row:
                    value = self.extract_value_from_cell(row[cell])
                    dictionary_property = self.search_on_dictionary(cell)
                    if dictionary_property:
                        self.add_triple_to_graph(self.db + section_row_property, self.db + dictionary_property, value)
                        self.utils.triples_serialized += 1
                        self.utils.mapped_cells += 1

    def extract_value_from_cell(self, cell):
        # take only value's cell and not link
        if len(cell) > 1:
            value = cell[-1]
        else:
            value = cell
        return value

    def define_row_and_section_property(self):
        section_property = self.search_on_dictionary(self.table_section)
        section_row_property = self.search_on_dictionary(self.table_section + settings.ROW_SUFFIX)
        # you can even not specify rowTableProperty
        if not section_row_property:
            section_row_property = section_property + "_" + str(self.reification_index)
        else:
            section_row_property = self.search_on_dictionary(self.table_section + settings.ROW_SUFFIX) + "_" + \
                                   str(self.reification_index)
        return section_property, section_row_property

    def add_triple_to_graph(self, subject, prop, value):
        subject = rdflib.URIRef(subject)
        prop = rdflib.URIRef(prop)
        value = self.check_value_type(value)
        # print subject, prop, value
        self.graph.add((subject, prop, value))

    def check_value_type(self, value):
        # i can have input value like list or like single input, i need to make a filter and get
        # unique element of this list
        if isinstance(value, list):
            result = value[0]
        else:
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
        resource_to_search = resource.replace(" ", "_")
        saved_resource = [r for r in resources_found if r in resource_to_search]
        if not saved_resource:
            if self.utils.ask_if_resource_exists(self.dbr + resource_to_search):
                resources_found.append(resource_to_search)
                result = self.dbr + resource_to_search
            else:
                result = ""
        else:
            result = self.dbr + saved_resource[-1]
        return result

    def search_on_dictionary(self, key):
        try:
            return self.dictionary[key]
        except KeyError:
            # there's no mapping rule in dictionary for this header
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
