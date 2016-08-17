import rdflib
import re

import mapping_rules


class Mapper:
    """

    """

    def __init__(self, language, graph, topic, resource, table_data, mode, utils, table_section=None):

        self.language = language
        self.graph = graph
        self.topic = topic
        self.resource = resource
        self.table_section = table_section
        self.table_data = table_data
        self.mode = mode
        self.utils = utils
        self.logging = utils.logging

        # TODO change this part
        if self.topic == 'elections_USA':
            self.topic = 'elections'

        # This dictionary it is used to have an idea of which headers haven't a mapping rule.
        self.headers_not_mapped = {}
        # Statistical values
        self.triples_added_to_the_graph = 0
        self.cells_mapped = 0
        self.total_cell_mapped = 0
        self.num_of_mapping_errors = 0
        self.no_mapping_found_cells = 0

        self.reification_index = 0

        self.dbo = None
        self.dbr = None
        self.dbp = None
        self.define_namespace(self.language)

    def define_namespace(self, language):
        if language != 'en':
            self.dbr = rdflib.Namespace("http://" + language + ".dbpedia.org/resource/")
        else:
            self.dbr = rdflib.Namespace("http://dbpedia.org/resource/")

        self.dbo = rdflib.Namespace("http://dbpedia.org/ontology/")
        self.dbp = rdflib.Namespace("http://dbpedia.org/property/")

    def map(self):
        if self.topic == 'single_resource' or self.topic == 'custom':
            rules = mapping_rules.MAPPING_TOPICS[self.language]
            for topic in rules:
                print ("Mapping: %s under section: %s , coming from resource: %s of topic: %s "
                       % (self.table_data, self.table_section, self.resource, self.topic))
                reification_index = 0
                for single_row in self.table_data:
                    self.reification_index += 1
                    # choose the right mapping for this kind of data, based upon language and topic parameters
                    try:
                        eval("self."+self.language+"_"+topic+"(single_row, self.reification_index)")
                    except:
                        print("Exception during mapping of: %s with this mapping rules: %s" % (self.resource, self.topic))
                        if self.reification_index > 0:
                            self.reification_index -= 1

        elif self.topic:
            print ("Mapping: %s under section: %s , coming from resource: %s of topic: %s "
                   % (self.table_data, self.table_section, self.resource, self.topic))
            reification_index = 0
            for single_row in self.table_data:
                self.reification_index += 1
                # choose the right mapping for this kind of data, based upon language and topic parameters
                try:
                    eval("self."+self.language+"_"+self.topic+"(single_row, self.reification_index)")
                except:
                    print("Exception during mapping of: %s " % self.resource)
                    if self.reification_index > 0:
                        self.reification_index -= 1

        # print in the log useful infos to keep trace of results

        if self.headers_not_mapped:
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
        Italian mapping rules for USA presidential elections
        :param reification_index:
        :param single_row:
        :return:
        """

        row_subject = rdflib.URIRef(self.dbr + self.resource)  # resource eg USA_presidential_elections_1992
        row_predicate = self.dbo.Election  # Election http://dbpedia.org/ontology/Election
        row_object = rdflib.URIRef(self.dbr + self.resource + "__" + str(
            reification_index))  # Reification eg USA_presidential_elections_1984__1 for the first row, #  __2 for second one etc.

        # keeping track of how many cells are added to the graph, for this row
        self.cells_mapped = 0
        for cell in single_row:
            value = single_row[cell]
            try:

                if value[0] != "-":
                    row = row_object
                    cell_subject = None
                    cell_predicate = None
                    cell_object = None

                    if cell == 'Candidati - Presidente' or cell == 'Candidato' or cell == 'candidato':
                        cell_subject = row  # row

                        cell_predicate = rdflib.URIRef(self.dbo.President)  # http://dbpedia.org/ontology/President

                        if len(value) == 2 and self.mode == 'json':
                            cell_object = value[1]  # value: eg [u'New York (stato)', u'Franklin D. Roosevelt']
                        else:
                            cell_object = value[0]
                            comma_index = cell_object.find(",")
                            if comma_index:
                                cell_object = cell_object[:comma_index]
                        cell_object = cell_object.replace(" ", "_")
                        cell_object = rdflib.URIRef(self.dbr + cell_object)

                    elif 'Candidati - Vicepresidente' in cell or 'Candidato Vicepresidente' in cell:
                        cell_subject = row  # row

                        cell_predicate = rdflib.URIRef(
                            self.dbo.VicePresident)  # http://dbpedia.org/ontology/VicePresident

                        if len(value) == 2 and self.mode == 'json':
                            cell_object = value[1]  # value eg [u'Iowa', u'Henry A. Wallace']
                        else:
                            cell_object = value[0]
                            comma_index = cell_object.find(",")
                            if comma_index:
                                cell_object = cell_object[:comma_index]
                        cell_object = cell_object.replace(" ", "_")
                        cell_object = rdflib.URIRef(self.dbr + cell_object)

                    elif cell == 'Candidati - Partito' or cell == 'Partito' or cell == 'Lista':
                        cell_subject = row  # row

                        cell_predicate = rdflib.URIRef(
                            self.dbo.PoliticalParty)  # http://dbpedia.org/ontology/PoliticalParty

                        cell_object = value[0]  # value eg [u'Partito Democratico (Stati Uniti)']
                        basestr = isinstance(cell_object, basestring)
                        if basestr:
                            if "Stati Uniti" in cell_object or "Stati_Uniti" in cell_object:
                                cell_object = cell_object[:-1] + " d'America)"
                            cell_object = cell_object.replace(" ", "_")
                            cell_object = rdflib.URIRef(self.dbr + cell_object)

                    elif cell == 'Grandi elettori - #' or cell == 'Grandi elettori - n.' \
                            or cell == 'Grandi elettori - Num.' or cell == 'Grandi Elettori ottenuti' \
                            or cell == 'Voti Elettorali' or cell == 'Grandi Elettori':
                        cell_subject = row  # row

                        cell_predicate = rdflib.URIRef(self.dbp.electoralVote)  # number of Great Electors

                        if value[0] >= 0:
                            cell_object = int(value[0])  # value eg [449.0]
                            cell_object = rdflib.Literal(cell_object, datatype=rdflib.namespace.XSD.positiveInteger)

                    elif cell == 'Voti - #' or cell == 'Voti - n.' or cell == 'Voti - Num.' or cell == 'Voti' \
                            or cell == 'Voti Popolari':
                        cell_subject = row  # row

                        cell_predicate = rdflib.URIRef(self.dbo.popularVote)  # popular vote number

                        if value[0] >= 0:
                            if type(value[0]) is float:
                                test = str(value[0])
                                if '.' in test:
                                    value[0] = test.replace('.', '')
                                cell_object = int(value[0])
                                cell_object = rdflib.Literal(cell_object,
                                                             datatype=rdflib.namespace.XSD.positiveInteger)  # value (number)

                    elif cell == 'Voti - %' or cell == '?% voti' or cell == '% voti' \
                            or cell == 'Percentuale' or cell == '%' or cell == '?%' in cell:
                        cell_subject = row  # row

                        cell_predicate = rdflib.URIRef(self.dbp.pvPct)  # pvPct stands for popular vote, percentage

                        # Sometimes wiki Users use comma instead of dot desribing percentage, so we have to convert commas in dots.
                        if ',' in value[0]:
                            value[0] = value[0].replace(",", ".")

                        if self.is_float(value[0]):
                            cell_object = rdflib.Literal(value[0], datatype=rdflib.namespace.XSD.float)  # value
                        basestr = isinstance(value[0], basestring)
                        if basestr:
                            percentage = value[0][-1:]
                            percentage = re.match(r'%', percentage)
                            if percentage:
                                value[0] = value[0].replace(",", ".")
                                value[0] = float(value[0][:-1])
                                cell_object = rdflib.Literal(value[0], datatype=rdflib.namespace.XSD.float)

                    else:

                        cell_subject = None
                        cell_predicate = None
                        cell_object = None

                        print ("Something went wrong choosing mapping rules :'((  data: %s header: %s" % (value, cell))
                        self.no_mapping_found_cells += 1
                        if cell not in self.headers_not_mapped.keys():
                            # Add to the list of headers with no mapping rules defined the current header
                            self.headers_not_mapped[cell] = value


                    # if s,p,o are set for this cell, add them to the graph
                    if cell_predicate and cell_object and cell_subject:
                        self.cells_mapped += 1
                        # Adding the triple to the graph
                        self.graph.add((cell_subject, cell_predicate, cell_object))
                        self.triples_added_to_the_graph += 1
                        self.print_triple(cell_subject, cell_predicate, cell_object)

            except:
                print("Error mapping %s   ,associate with cell: %s" % (value, cell))
                self.num_of_mapping_errors += 1

        if self.cells_mapped > 0:
            # add only those rows with some mapped cells to the graph
            self.graph.add((row_subject, row_predicate, row_object))
            # adding the row to the triples mapped
            self.triples_added_to_the_graph += 1
            self.print_triple(row_subject, row_predicate, row_object)

            self.total_cell_mapped += self.cells_mapped

        else:
            self.reification_index -= 1

    def print_triple(self, s, p, o):
        print("Added sub= %s pred= %s obj= %s to the graph" % (s, p, o))

    def is_float(self, value):
        try:
            float(value)
            return True
        except:
            return False
