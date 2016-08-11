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
        if self.topic == 'elections_USA':
            self.topic = 'elections'

        self.total_cell_mapped = 0
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
                print "Mapping: " + str(self.table_data) + " under section: " + str(self.table_section) + \
                      " , coming from resource: " + str(self.resource) + " of topic: " + str(topic)
                reification_index = 0
                for single_row in self.table_data:
                    self.reification_index += 1
                    # choose the right mapping for this kind of data, based upon language and topic parameters
                    try:
                        eval("self." + self.language + "_" + topic + "(single_row, self.reification_index)")
                    except:
                        print("Exception during mapping of: " + self.resource + "with this mapping rules: "+topic)

        elif self.topic:
            print "Mapping: " + str(self.table_data) + " under section: " + self.table_section + \
                  " , coming from resource: " + str(self.resource) + " of topic: " + str(self.topic)
            reification_index = 0
            for single_row in self.table_data:
                self.reification_index += 1
                # choose the right mapping for this kind of data, based upon language and topic parameters
                try:
                    eval("self." + self.language + "_" + self.topic + "(single_row, self.reification_index)")
                except:
                    print("Exception during mapping of: " + self.resource)

            self.utils.logging.info("Total cell mapped for this table: " + str(self.total_cell_mapped))


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
        self.cell_mapped = 0
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

                        cell_predicate = rdflib.URIRef(self.dbo.VicePresident)  # http://dbpedia.org/ontology/VicePresident

                        if len(value) == 2 and self.mode == 'json':
                            cell_object = value[1]  # value eg [u'Iowa', u'Henry A. Wallace']
                        else:
                            cell_object = value[0]
                            comma_index = cell_object.find(",")
                            if comma_index:
                                cell_object = cell_object[:comma_index]
                        cell_object = cell_object.replace(" ", "_")
                        cell_object = rdflib.URIRef(self.dbr + cell_object)

                    elif cell == 'Candidati - Partito'or cell == 'Partito' or cell == 'Lista':
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
                            or cell== 'Grandi elettori - Num.' or cell == 'Grandi Elettori ottenuti' \
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
                        print ("Something went wrong choosing mapping rules :'((  data: " + str(value) + " header: " + str(cell))
                        cell_subject = None
                        cell_predicate = None
                        cell_object = None

                    # if s,p,o are set for this cell, add them to the graph
                    if cell_predicate and cell_object and cell_subject:
                        self.graph.add((cell_subject, cell_predicate, cell_object))
                        self.cell_mapped += 1
                        self.print_triple(cell_subject, cell_predicate, cell_object)

            except:
                print("Error mapping " + str(value) + "  associate with cell: "+str(cell))

        if self.cell_mapped > 0:
            # add only those rows with some mapped cells
            self.graph.add((row_subject, row_predicate, row_object))
            self.print_triple(row_subject, row_predicate, row_object)
            self.total_cell_mapped += self.cell_mapped

        else:
            self.reification_index -= 1

    def print_triple(self, s, p, o):
        print("Added s= " + str(s) + " p= " + str(p) + " o= " + str(o) + " to the graph")

    def is_float(self, value):
        try:
            float(value)
            return True
        except:
            return False