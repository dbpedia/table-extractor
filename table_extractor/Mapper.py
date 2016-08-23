# coding=utf-8
import rdflib
import re


import mapping_rules


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

    def __init__(self, chapter, graph, topic, resource, table_data, mode, utils, table_section=None):
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
        self.mode = mode
        self.utils = utils
        self.logging = utils.logging

        # this is a little hook, it is used to change topic from elections_USA to elections
        if self.topic == 'elections_USA':
            self.topic = 'elections'

        # This dictionary  is used to have an idea of which headers haven't a mapping rule.
        self.headers_not_mapped = {}
        # Statistical values
        self.triples_added_to_the_graph = 0  # number of triples added to the graph
        self.cells_mapped = 0  # number of cells mapped for a certain row
        self.total_cell_mapped = 0  # total number of mapped cells for this table
        self.num_of_mapping_errors = 0  # number of mapping exceptions
        self.no_mapping_found_cells = 0  # number of cell for which no mapping rule has found

        # Reification_index is and index used to make a reification possible. It use the concept of row.
        self.reification_index = 0

        # Defining namespace used by the rdf graph
        self.dbo = None
        self.dbr = None
        self.dbp = None
        self.define_namespace(self.chapter)

    def define_namespace(self, chapter):
        """
        Method used to set standard names (dbr stands for dbpediaresource, dbp for dbpediaproperty,
          dbo for dbpediaontology)

        :param chapter: the wiki chapter of reference
        :return:
        """

        if chapter != 'en':
            self.dbr = rdflib.Namespace("http://" + chapter + ".dbpedia.org/resource/")
        else:
            self.dbr = rdflib.Namespace("http://dbpedia.org/resource/")

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
        # In case -s | -w is used as pyTableExtractor option, we know which is the chapter but not the topic,
        # so tries every mapping rule for the selected chapter
        # NOTE: This part seems to be a logical mistake, but I haven't received a feedback by community about this.
        if self.topic == 'single_resource' or self.topic == 'custom':

            # Rules are retrieved using mapping_rules.py
            rules = mapping_rules.MAPPING_TOPICS[self.chapter]
            # Iteraters over topic
            for topic in rules:
                # prints out what the method tries to do
                print ("Mapping: %s under section: %s , coming from resource: %s of topic: %s "
                       % (self.table_data, self.table_section, self.resource, self.topic))
                # reset reification index
                reification_index = 0
                # Iterates row by row in table_data
                for single_row in self.table_data:
                    # Increase reification index by one
                    self.reification_index += 1
                    # choose the right mapping for this kind of data, based upon chapter and topic parameters
                    try:
                        eval("self."+self.chapter+"_"+topic+"(single_row, self.reification_index)")
                    except:
                        print("Exception during mapping of: %s with this mapping rules: %s" % (self.resource, self.topic))
                        # if exception occurs, decrease the reification_index
                        if self.reification_index > 0:
                            self.reification_index -= 1

        # If a topic is set, use it to choose the right mapping method
        elif self.topic:

            print ("Mapping: %s under section: %s , coming from resource: %s of topic: %s "
                   % (self.table_data, self.table_section, self.resource, self.topic))

            # reset reification_index
            reification_index = 0

            # for every row of data
            for single_row in self.table_data:
                # increase the reification_index
                self.reification_index += 1

                # choose the right mapping for this kind of data, based upon chapter and topic parameters
                try:
                    eval("self."+self.chapter+"_"+self.topic+"(single_row, self.reification_index)")
                except:
                    print("Exception during mapping of: %s " % self.resource)
                    # if exception occurs, decrease the reification_index
                    if self.reification_index > 0:
                        self.reification_index -= 1

        # print in the log useful infos to keep trace of results
        if self.headers_not_mapped:   # these headers are ones for which no mapping rules has been found
            self.logging.info("These headers have not a corresponding mapping rule: ")
            for header in self.headers_not_mapped:
                self.logging.info(" - %s , Value Example: %s" % (header, self.headers_not_mapped[header]))

        self.logging.info("Total cell mapped for this table: %s " % self.total_cell_mapped)
        self.logging.info("Total \'no mapping rule\' : %s " % self.no_mapping_found_cells)
        self.logging.info("Total mapping errors: %s " % self.num_of_mapping_errors)

        # Adding values to the total, stored in Utilities class, in order to print a final report
        self.utils.mapped_cells += self.total_cell_mapped
        self.utils.no_mapping_rule_errors += self.no_mapping_found_cells
        self.utils.mapping_errors += self.num_of_mapping_errors

    def it_elections(self, single_row, reification_index):
        """
        Italian mapping rules for elections pages. It is used to add triples to the graph.


        :param reification_index: (int) index used to reification of the row concept
        :param single_row: (dict) dictionary containing data to map. {'header': [values]}
        :return: nothing
        """

        """
        row_subject,row_predicate, row_object are values used to make a triple which represents reification for the
          row concept.

        -subject, as the resources analyzed are in fact wiki pages, is their dbpedia representation
        Eg. http://dbpedia.org/resource/United_States_presidential_election,_2012

        -predicate for the row concept is dbo:Election
         NOTE: it would be better to use a different concept to map the predicate (Electoral Result?) but due to lack of
          time I didn't get a feedback by Community over this idea.

        -object = reification for the row concept
          It uses the resourceName__reificationIndex format as you can see in CareerStation for Soccer Players
          Please see http://dbpedia.org/page/Andrea_Pirlo and http://dbpedia.org/page/Andrea_Pirlo__1 to fully
           understand what is done here.
        """

        row_subject = rdflib.URIRef(self.dbr + self.resource)  # Eg. resource =United_States_presidential_election,_2012
        row_predicate = self.dbo.Election  # Election http://dbpedia.org/ontology/Election
        row_object = rdflib.URIRef(self.dbr + self.resource + "__" + str(
            reification_index))  # Reification eg USA_presidential_elections_1984__1 for the first row,
        #  __2 for second one etc.

        # keeping track of how many cells are added to the graph, for this row
        self.cells_mapped = 0
        # Iterates over cell in the current row. cell equals to header
        for header in single_row:
            # values is a list containing data extracted
            values = single_row[header]
            try:
                # try to map data, but only if data for that cell exists :)
                if values[0] != "-":

                    # set row as the reification of the row's concept
                    row = row_object

                    # set subject, predicate and object for the single cell
                    cell_subject = None
                    cell_predicate = None
                    cell_object = None

                    """
                    NOTE: data are substantially mapped using the corresponding header. In fact manipulation of values
                     and rules to set subject object and predicate of a cell strictly depending on the value of the
                     header associated with values.
                    From here you can see if blocks representing the actual mapping rules.

                    FUTURE DEVELOPMENT: It would be useful to use soft coded mapping rules using standard methods to
                     manipulate values and algorithm to decide how to map each part.
                    """

                    # 1° RULE

                    if header == 'Candidati - Presidente' or header == 'Candidato' or header == 'candidato' \
                            or header == 'Candidato presidente' or header == 'Candidati - Presidente (Stato)':

                        # subject is the row concept
                        # Eg. http://it.dbpedia.org/resource/Elezioni_presidenziali_negli_Stati_Uniti_d'America_del_1940
                        cell_subject = row

                        # Predicate is http://dbpedia.org/ontology/President
                        cell_predicate = rdflib.URIRef(self.dbo.President)  # http://dbpedia.org/ontology/President

                        # if the length of data list is 2
                        if len(values) == 2:
                            # object is the second value
                            cell_object = values[1]  # value: eg [u'New York (stato)', u'Franklin D. Roosevelt']
                        else:
                            # if not, object is the first between values list
                            cell_object = values[0]

                            # find if a comma is inside the object
                            comma_index = cell_object.find(",")
                            if comma_index >= 0:
                                # If so, replace it with everything comes before the comma
                                cell_object = cell_object[:comma_index]

                        # replace the spaces with underscores
                        cell_object = cell_object.replace(" ", "_")

                        # try to know if the value in object is a existing dbpedia resource
                        res_exists = self.utils.ask_if_resource_exists(self.dbr + cell_object)
                        if res_exists:
                            # If the resource already exists use the reference to that resource
                            cell_object = rdflib.URIRef(self.dbr + cell_object)
                        else:
                            # replace underscores with simple spaces
                            cell_object = cell_object.replace("_", " ")
                            # NOTE use lang= instead of datatype?
                            # use a Literal containing value as the object
                            cell_object = rdflib.Literal(cell_object, datatype=rdflib.namespace.XSD.string)

                    # 2° RULE

                    elif header == 'Candidati - Vicepresidente' or header == 'Candidato Vicepresidente' \
                            or header == 'Candidato vicepresidente' or header == 'Candidati - Vicepresidente (Stato)':

                        # subject is the row concept
                        # Eg. http://it.dbpedia.org/resource/Elezioni_presidenziali_negli_Stati_Uniti_d'America_del_1940
                        cell_subject = row  # row

                        # Predicate is http://dbpedia.org/ontology/VicePresident
                        cell_predicate = rdflib.URIRef(self.dbo.VicePresident)

                        # choose which value has to be selected depending on mode and values lenght
                        if len(values) == 2 and self.mode == 'json':
                            cell_object = values[1]  # values eg [u'Iowa', u'Henry A. Wallace']
                        else:
                            cell_object = values[0]

                            # find if there is a comma inside the object
                            comma_index = cell_object.find(",")
                            if comma_index:
                                # if so, replace it with everything comes before the comma
                                cell_object = cell_object[:comma_index]

                        # try to know if the value in object is a existing dbpedia resource
                        res_exists = self.utils.ask_if_resource_exists(self.dbr + cell_object)
                        if res_exists:
                            # If the resource already exists use the reference to that resource
                            cell_object = rdflib.URIRef(self.dbr + cell_object)
                        else:
                            # replace underscores with simple spaces
                            cell_object = cell_object.replace("_", " ")
                            # NOTE use lang= instead of datatype?
                            # use a Literal containing value as the object
                            cell_object = rdflib.Literal(cell_object, datatype=rdflib.namespace.XSD.string)

                    # 3° RULE

                    elif header == 'Candidati - Partito' or header == 'Partito' or header == 'Lista':

                        # subject is the row concept
                        # Eg. http://it.dbpedia.org/resource/Elezioni_presidenziali_negli_Stati_Uniti_d'America_del_1940
                        cell_subject = row  # row

                        # predicate is http://dbpedia.org/ontology/PoliticalParty
                        cell_predicate = rdflib.URIRef(self.dbo.PoliticalParty)

                        # object is values[0]
                        cell_object = values[0]  # values eg [u'Partito Democratico (Stati Uniti)']

                        # test out if object is a string or a unicode
                        basestr = isinstance(cell_object, basestring)
                        if basestr:
                            # if so, test if "Stati Uniti" is inside it
                            if "Stati Uniti" in cell_object or "Stati_Uniti" in cell_object:
                                # if so, add to the last part of the string "_d'America)"
                                cell_object = cell_object[:-1] + "_d'America)"

                        # try to know if the value in object is a existing dbpedia resource
                        res_exists = self.utils.ask_if_resource_exists(self.dbr + cell_object)
                        if res_exists:
                            # If the resource already exists use the reference to that resource
                            cell_object = rdflib.URIRef(self.dbr + cell_object)
                        else:
                            # replace underscores with simple spaces
                            cell_object = cell_object.replace("_", " ")
                            # NOTE use lang= instead of datatype?
                            # use a Literal containing value as the object
                            cell_object = rdflib.Literal(cell_object, datatype=rdflib.namespace.XSD.string)

                    # 4° RULE

                    elif header == 'Grandi elettori - #' or header == 'Grandi elettori - n.' \
                            or header == 'Grandi elettori - Num.' or header == 'Grandi Elettori ottenuti' \
                            or header == 'Voti Elettorali' or header == 'Grandi Elettori' \
                            or header == 'Voti elettorali' or header == 'Elettori':

                        # subject is the row concept
                        # Eg. http://it.dbpedia.org/resource/Elezioni_presidenziali_negli_Stati_Uniti_d'America_del_1940
                        cell_subject = row  # row

                        # predicate is http://dbpedia.org/property/electoralVote which stands for the
                        #  number of Great Electors
                        cell_predicate = rdflib.URIRef(self.dbp.electoralVote)

                        # test if value is >= 0
                        if values[0] >= 0:
                            if self.is_int(values[0]):
                                # if so set object as int(value)
                                cell_object = int(values[0])  # values eg [449.0]

                                # finally  use a Literal with a positiveInteger data type
                                cell_object = rdflib.Literal(cell_object, datatype=rdflib.namespace.XSD.positiveInteger)

                    # 5° RULE

                    elif header == 'Voti - #' or header == 'Voti - n.' or header == 'Voti - Num.' or header == 'Voti' \
                            or header == 'Voti Popolari' or header == 'Voti popolari' \
                            or header == 'Voto popolare - Voti' or header == 'Voto popolare':

                        # subject is the row concept
                        # Eg. http://it.dbpedia.org/resource/Elezioni_presidenziali_negli_Stati_Uniti_d'America_del_1940
                        cell_subject = row  # row

                        # predicate is http://dbpedia.org/property/popularVote which stands for the
                        #  number of votes
                        cell_predicate = rdflib.URIRef(self.dbo.popularVote)

                        basestr = isinstance(values[0], basestring)
                        if basestr:
                            # delete spaces
                            if ' ' in values[0]:
                                values[0] = values[0].replace(' ', '')
                            # delete dots
                            if '.' in values[0]:
                                values[0] = values[0].replace('.', '')

                        # test if value can be casted to int type
                        if self.is_int(values[0]):
                            # cast it to int
                            values[0] = int(values[0])
                            # set object to a Literal with a positiveInteger data type
                            cell_object = rdflib.Literal(values[0], datatype=rdflib.namespace.XSD.positiveInteger)

                    # 6° RULE

                    elif header == 'Voti - %' or header == '?% voti' or header == '% voti' \
                            or header == 'Percentuale' or header == '%' or header == '?%' or header == 'Voti (%)' \
                            or header == 'Voto popolare - Percentuale':

                        # subject is the row concept
                        # Eg. http://it.dbpedia.org/resource/Elezioni_presidenziali_negli_Stati_Uniti_d'America_del_1940
                        cell_subject = row  # row

                        # predicate is http://dbpedia.org/property/pvPct which stands for popular vote, percentage
                        cell_predicate = rdflib.URIRef(self.dbp.pvPct)

                        # test if the value can be casted to a float
                        if self.is_float(values[0]):
                            values[0] = float(values[0])
                            # set object to a float Literal
                            cell_object = rdflib.Literal(values[0], datatype=rdflib.namespace.XSD.float)  # values

                        else:
                            # test if it is a string or a unicode
                            basestr = isinstance(values[0], basestring)
                            if basestr:
                                # Sometimes wiki Users use comma instead of dot desribing percentage, so we have
                                # to convert commas in dots.
                                if ',' in values[0]:
                                    values[0] = values[0].replace(",", ".")

                                # set as percentage the last character of the string
                                percentage = values[0][-1:]
                                # test if this character is a '%'
                                percentage = re.match(r'%', percentage)
                                if percentage:
                                    # if so, replace commas with dots, and value with float(value_less_last_character)
                                    values[0] = values[0].replace(",", ".")
                                    values[0] = float(values[0][:-1])
                                    # set object as a float Literal
                                    cell_object = rdflib.Literal(values[0], datatype=rdflib.namespace.XSD.float)
                                else:
                                    # set object as a float Literal
                                    cell_object = rdflib.Literal(values[0], datatype=rdflib.namespace.XSD.float)

                    # IF HEADER DOES NOT MATCH ANY RULE
                    else:

                        # Reset sub, obj and predicate to None
                        cell_subject = None
                        cell_predicate = None
                        cell_object = None

                        # print out this condition to the console
                        print ("Something went wrong choosing mapping rules :'((  data: %s header: %s"
                               % (values, header))

                        # increase the count of 'no mapping rule found' cells
                        self.no_mapping_found_cells += 1

                        # test if the header is already in headers_not_mapped
                        if header not in self.headers_not_mapped.keys():
                            # If not, add to the list of headers with no mapping rules defined the current header
                            self.headers_not_mapped[header] = values

                    # if sub,pred,obj are set for this cell, add them to the graph
                    if cell_predicate and cell_object and cell_subject:
                        # increase the count of cells mapped for this row
                        self.cells_mapped += 1

                        # Adding the triple to the graph using graph.add(sub, pred, obj)
                        self.graph.add((cell_subject, cell_predicate, cell_object))

                        # increase the amount of triples added to the graph
                        self.triples_added_to_the_graph += 1
                        # print in the console the triple added using print_triple(sub, pred, object)
                        self.print_triple(cell_subject, cell_predicate, cell_object)

            except:
                print("Error mapping %s   ,associate with cell: %s" % (values, header))
                # Increase the number of mapping exceptions
                self.num_of_mapping_errors += 1

        # Finally if at least one cell is correctly mapped
        if self.cells_mapped > 0:
            # add only those rows with some mapped cells to the graph
            self.graph.add((row_subject, row_predicate, row_object))
            # add the row to the triples mapped
            self.triples_added_to_the_graph += 1
            # print triple added
            self.print_triple(row_subject, row_predicate, row_object)
            # added this row cells to the total number of cells maapped
            self.total_cell_mapped += self.cells_mapped

        else:
            # decrease the reification index as the row has not been added to the graph
            self.reification_index -= 1

    def print_triple(self, s, p, o):
        """
         Prints the triple added to the graph
        :param s: subject
        :param p: predicate
        :param o: object
        :return:
        """
        print("Added sub= %s pred= %s obj= %s to the graph" % (s, p, o))

    def is_float(self, value):
        """
        Test out if a value passed as parameter is a float number
        :param value: a string you want to test
        :return: True if value is a float | False otherwise
        """
        try:
            float(value)
            return True
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

        except ValueError:
            return False
