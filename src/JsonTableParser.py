import logging
import re

import Mapper

# TODO DOCSTRINGS
__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class JsonTableParser:
    """
    This class is used to analyze the structure of a table in order to extract data.
    It needs a data structure representing a general table.

    """

    def __init__(self, json_object, chapter, graph, topic, resource):
        """

        :param table: is a table you want to analyze and parse
        """

        self.json_object = json_object
        self.chapter = chapter
        self.graph = graph
        self.topic = topic
        self.resource = resource

        self.sections_number = 0
        self.article_sections = []
        self.tables_list = []
        self.tables_number = 0
        self.find_sections(self.json_object['result'])
        logging.info("Sections found: ")
        for section in self.article_sections:
            self.find_tables(section['section_title'], section)
            logging.info(section['section_title'])

        self.table_header = None
        self.section_title = None
        # table_content is a list of dictionaries containing cells
        self.table_content = None
        self.row_found = False
        self.table_rows_list = []
        self.last_row = []

        self.table_in_a_unique_list = []
        self.last_item = []
        self.item_to_read = True
        self.temp_list = []
        self.filtered_table = []

        self.table_headers = []
        self.sub_headers = []
        self.super_headers = []
        self.table_data = []
        self.data_rows = []

    def find_sections(self, json_object=None):
        """
        It manipulates a json object (already deserialized in a python object).
        If it find dictionaries containing a section it extract and append them to a specific list.
        :param json_object:

        :return:
        """

        try:
            if json_object:
                if type(json_object) == dict:
                    if '@type' in json_object and json_object['@type'] == 'section':
                        if 'content' in json_object:
                            json_object['content']['section_title'] = json_object['title']
                            self.article_sections.append(json_object['content'])
                            self.sections_number += 1
                            # print("Section Found: "+json_object['content']['section_title'])
                            return
                    else:
                        for value in json_object.values():
                            self.find_sections(value)
                elif type(json_object) == list:
                    for value in json_object:
                        self.find_sections(value)
                else:
                    return
        except:
            logging.exception("find_section threw an exception trying to analyze this object " + str(json_object))
            print("WRONG use with: " + str(json_object))

    def find_tables(self, sec_title, json_object=None):
        """
        Once sections are found, this function find out tables and associate them with the title of section.
        :param json_object:
        :param sec_title:
        :return:
        """

        try:
            if json_object:
                if type(json_object) == dict:
                    if '@type' in json_object and json_object['@type'] == 'table':
                        if 'content' in json_object:
                            json_object['section_title'] = sec_title
                            self.tables_list.append(json_object)
                            self.tables_number += 1
                            print("Table Found for section: " + sec_title)
                            return
                    else:
                        for value in json_object.values():
                            self.find_tables(sec_title, value)
                elif type(json_object) == list:
                    for value in json_object:
                        self.find_tables(sec_title, value)
        except:
            logging.exception("find_tables threw an exception analyzing this json object: " + str(json_object))

    def analyze_tables(self):
        for table in self.tables_list:
            print("Section:" + str(table['section_title']) + " ... Trying to analyze this table: " + str(table))
            self.set_table(table)
            self.find_rows()
            if self.table_rows_list:
                logging.info("1. rows found")
                print("1. Rows FOUND")
                self.find_headers()
                if self.table_headers:
                    logging.info("2. headers found")
                    print ("2. Headers FOUND")
                    self.extract_data()
                    self.refine_data()
                    if self.data_rows:
                        logging.info("3. Data extracted")
                        logging.debug("DATA: " + str(self.data_rows))
                        print("3. Data extracted")
                        map_tool = Mapper.Mapper(self.chapter, self.graph, self.topic, self.resource, self.data_rows, 'json', table['section_title'])
                        map_tool.map()
                    else:
                        logging.debug("e3 - UNABLE TO EXTRACT DATA - resource: " + str(self.resource) + "table : " + str(table))
                        print("e3 UNABLE TO EXTRACT DATA")
                else:
                    logging.debug(
                        " e2 Unable to find headers - resource: " + str(self.resource) + " under section : " \
                        + str(table['section_title']))
                    print("e2 UNABLE TO FIND HEADERS")
            else:
                logging.debug(
                    " e1 Unable to rows - resource: " + str(self.resource) + " table : " + str(table))
                print(" e1 UNABLE TO FIND ROWS")
            self.erase_table_data()

    def set_table(self, table):
        self.table_header = table['header']
        self.section_title = table['section_title']
        # table_content is a list of dictionaries containing cells
        self.table_content = table['content']
        self.row_found = False
        self.table_rows_list = []
        self.last_row = []

        self.table_in_a_unique_list = []
        self.last_item = []
        self.item_to_read = True
        self.temp_list = []

        self.table_headers = []
        self.sub_headers = []
        self.super_headers = []
        self.table_data = []
        self.data_rows = []


    def filter_cells(self):
        """
        filter_cells is used to filter those cells or labels useless.
        """
        # deleting cells containing useless data
        self.filter_align_cells()
        # delete all non-data @an* contents
        self.filter_useless_dash_cells()
        # removing useless tag
        self.filter_content()
        return

    def filter_useless_dash_cells(self):
        """
        It is used to delete dash values (---) with a @an* label from a dictionary
        Eg : {u'content': {u'@an1': u'----', u'@an0': u'0,2'}, u'@type': u'body_cell'}
            ----> {u'content': { u'@an0': u'0,2'}, u'@type': u'body_cell'}
        :param cell: is the cell to test
        :param row:
        :return: nothing
        """

        for row in self.table_rows_list:
            for cell in row:
                for key in cell['content'].keys():
                    test = cell['content'].keys()
                    anonim_label = re.findall(r'@an(.*)', key)
                    if anonim_label and type(cell['content'][key]) == unicode:
                        dash_value = re.search(r'---(.*)', cell['content'][key])
                        if dash_value:
                            del cell['content'][key]
        return

    def filter_content(self):
        for row in self.table_rows_list:
            for cell in row:
                index = row.index(cell)
                row[index] = cell['content']

    def filter_align_cells(self):
        """
        This function delete align_cells from a row.
        Example of align_cell we want to delete: {u'content': {u'align': [u'"center"']}, u'@type': u'body_cell'}
        :param cell: is the cell to test
        :param row: is the row
        :return: nothing
        """
        for row in self.table_rows_list:
            for cell in row:
                if 'content' in cell and 'align' in cell['content']:
                    try:
                        row.remove(cell)
                    except:
                        print("Error removing useless cell:" + str(cell))
        return

    def find_rows(self):
        """
         find_rows is a a function that iterates content of a tables (cells) and compose a list containing table's rows.
         For every cell in table_content the function initially appends the cell int a temporary list called last_row.
         It uses match_row(cell) to understand when a row ends.
         When a new row is found the last_row list is inserted in table_rows_list, obtaining a list of rows, in which /
         every row is a list of cells.
         :return: It returns nothing to the caller.
        """
        for cell in self.table_content:
            # First it appends the new cell in a temporary list called last_row
            self.last_row.append(cell)
            # then it tests if this cell contains a New Row tag calling match_row.
            if '@type' in cell and cell['@type'] != 'head_cell':
                self.match_row(cell)
                # if a row has found  the boolean row_found is equal to TRUE
            if self.row_found:
                # the temporary list has appended to the list of rows of this table 'table_rows_list'
                self.table_rows_list.append(self.last_row)
                # last_row is cleared
                self.last_row = []
                # row_found is set again to False
                self.row_found = False

                print("a row has been found")
                # we need to add the last row manually
        self.table_rows_list.append(self.last_row)
        self.filter_cells()
        for row in self.table_rows_list:
            print(" THIS IS A ROW: " + str(row))
        return

    def match_row(self, cell):
        """
        match_row is a function used to recompose the row structure of a table.
        It is a recursive algorithm which works on a undefined structure (cell).
        It tries to find a pattern (usually the ----) used to tag a new row in tables.
        When a row is found, a boolean tag (row_found) is set to true and then the function exit.
        :param cell: is the data structure passed to the function as an argument, it could be a dictionary or a list.
        :return:nothing
        """
        try:
            if type(cell) == unicode:
                row = re.findall(r'----(.*)', cell)
                if row:
                    del cell
                    self.row_found = True
                    return
            elif type(cell) == dict:
                for value in cell.values():
                    self.match_row(value)
                for key in cell.keys():
                    self.match_row(key)
            elif type(cell) == list:
                for value in cell:
                    self.match_row(value)
            else:
                return
        except:
            print("Problem matching row with :" + str(cell))

    def find_headers(self):
        """
        find_headers, is a function used to find out which cells are  table headers.
        To do so it firstly calls (for every cell in the table), find_colspan, to rebuild the cell if a colspan is found.
        This objective is reached recomposing the cells (dictionary) themselves, adding a label called 'colspan' \
        whom value is a list containing the value of colspan.
        Eg: {u'width': [u'"35%" colspan=3']} ---> {u'width': [u'"35%" colspan=3'], 'colspan': [u'3']}
        I chose a list instead of a simple unicode string containing the value because in some cases there are already \
        cells which represent colspan values in this way.
        Therefore these colspans have to be associated with the respective header, with associate_colspan_with_header.

        :return:
        """
        for row in self.table_rows_list:
            for cell in row:
                try:
                    colspan = self.find_colspan(cell)
                    if colspan:
                        cell[u'colspan'] = [colspan]
                except:
                    print" error finding colspan "
        try:
            self.transform_cells_in_a_unique_list()
            self.filter_useless_row()
            self.associate_colspan_with_header()
            self.add_single_colspan_header()
            self.add_headers()
            self.resolve_sub_headers()
            self.associate_super_and_sub_headers()
        except:
            print("Exception finding headers, table under section :" + str(self.section_title))

    def find_colspan(self, cell_part):
        """
        This is a recursive function used to find out 'colspan=digit' attribute.
        It is useful to calculate out the number of table headers.
        The function takes cell_part as a parameter and tests is type.
        If cell_part is dictionary or a list, it call recursively itself over the values in these data structures.
        Eg: cell_part = {u'width': [u'"35%" colspan=3']} ---> recursive call on [u'"35%" colspan=3']
        Otherwise if cell_part is a simple unicode value the function tests if there is a 'colspan= value' \
        using RegEx, and return the value of colspan if exists.
        Eg: u'"20%" colspan=2' returns '2'

        :param cell_part: is a cell of a part of it. The function recall itself recursively till cell_part is a simple \
         like a unicode string.
        :return: value of result is returned to the original caller. It could be a value of colspan or None.
        """
        if type(cell_part) == dict and cell_part != {}:
            for value in cell_part.values():
                result = self.find_colspan(value)
                if result:
                    return result
        elif type(cell_part) == list and cell_part != []:
            for value in cell_part:
                result = self.find_colspan(value)
                if result:
                    return result
        elif type(cell_part) == unicode:
            colspan = re.search(r'colspan=(.*)', cell_part)
            if colspan:
                result = colspan.group(1)
                return result
            else:
                result = None
                return result
        else:
            result = None
        return result

    def associate_colspan_with_header(self):
        # TODO complete DocString
        """
        associate_colspan_with_header is a function used to associate colspan values found with find_colspan(cell) \
        with their respective header value.
        To do so, in a hand it finds out the next colspan attribute inside a row.
        In another hand, the function extracts the next anonymous value (that should be a header) with find_next_an_value

        :return:
        """
        # TODO  Explain
        for row in self.filtered_table:
            last_colspan = None
            item_iterator = iter(row)
            self.item_to_read = True
            while self.item_to_read:
                try:
                    item = item_iterator.next()

                    if item == u'colspan':
                        last_colspan = item_iterator.next()[0]
                        next_anon_value = self.find_next_an_value(item_iterator)
                        header_index = row.index(next_anon_value)
                        # TODO explain the choice
                        filters = self.filter_false_headers(next_anon_value)
                        if not filters:
                            row[header_index - 1] = {'header': next_anon_value, 'colspan': last_colspan}
                            print(
                            "Found header \"" + row[header_index - 1]['header'] + "\" with colspan = " + last_colspan)

                        ''' Disabled due to logic
                        if 'Altri' in next_anon_value:
                            for n in range(1, int(last_colspan)):
                                row.insert(header_index + 1, u'@an0')
                                row.insert(header_index + 2, u'Altri')
                        '''



                except StopIteration:
                    self.item_to_read = False
        return

    def transform_cells_in_a_unique_list(self):
        for row in self.table_rows_list:
            for cell in row:
                for key in cell.keys():
                    self.last_item.append(key)
                    if type(cell[key]) == list:
                        self.last_item.append(cell[key][0])
                    elif type(cell[key]) == dict:
                        self.resolve_dictionary_in_list(cell[key])
                        self.last_item.append(self.temp_list)
                        self.temp_list = []
                    else:
                        self.last_item.append(cell[key])
            self.table_in_a_unique_list.append(self.last_item)
            self.last_item = []

    def find_next_an_value(self, item_iterator):
        """

        :param item_iterator:
        :return:
        """
        not_found = True
        while not_found:
            try:
                item = item_iterator.next()
                anon_value = re.findall(r'@an(.*)', item)
                if anon_value:
                    return item_iterator.next()

            except StopIteration:
                return None

    def filter_useless_row(self):
        for row in self.table_in_a_unique_list:
            append = True
            for element in row:
                try:
                    if type(element) == unicode:
                        others = re.findall(r'Altri', element)
                        total = re.findall(r'Totale', element)
                        if others or total:
                            append = False
                except:
                    print("Exception removing useless row: "+str(row))
            if append:
                self.filtered_table.append(row)


    def add_single_colspan_header(self):
        header_in_row = True
        for row in self.filtered_table:
            if header_in_row:
                header_in_row = self.check_headers(row)
                for item in row:
                    if '@an' in item:
                        an_index = row.index(item)
                        header = row[an_index + 1]
                        row[an_index] = {'header': header, 'colspan': u'1'}

    def check_headers(self, row):
        """

        :param row:
        :return:
        """
        for element in row:
            if type(element) == dict and 'header' in element:
                return True
        return False

    def add_headers(self):
        for row in self.filtered_table:
            for element in row:
                if type(element) == dict and 'header' in element:
                    header = [element['header'], element['colspan']]
                    self.table_headers.append(header)
        print("Headers found:")
        for header in self.table_headers:
            print str("HEADER: " + str(header[0]) + " COLSPAN: " + str(header[1]))
        print str("Table_Headers ---> " + str(self.table_headers))

    def filter_false_headers(self, value):
        if 'Totale' in value:
            return True
        if 'Altri' in value:
            return True
        else:
            return False

    def resolve_sub_headers(self):
        sum_of_colspan = 0
        number_of_headers_remained = self.table_headers.__len__()
        for header in self.table_headers:
            if sum_of_colspan != number_of_headers_remained:
                sum_of_colspan += int(header[1])
                number_of_headers_remained -= 1
            else:
                last_super_header_index = self.table_headers.index(header)
                self.super_headers = self.table_headers[:last_super_header_index]
                print ("THESE ARE SUPER_HEADERS: " + str(self.super_headers))
                self.sub_headers = self.table_headers[last_super_header_index:]
                print ("THESE ARE SUB_HEADERS: " + str(self.sub_headers))
                return

    def associate_super_and_sub_headers(self):
        self.table_headers = []
        for super_header in self.super_headers:
            colspan = int(super_header[1])
            for number_of_sub_headers in range(0, colspan):
                sub_header = self.sub_headers[0]
                header_to_append = str(super_header[0]) + " - " + str(sub_header[0])
                self.table_headers.append(header_to_append)
                print ("super_header : " + str(super_header[0]) + "   sub_header: " + str(sub_header[0]))

                self.sub_headers.remove(sub_header)

    def extract_data(self):
        """

        :return:
        """

        for row in self.filtered_table:
            try:
                row_length = len(row)

                for data_index in range(0, row_length):
                    data = []
                    if '@an' in row[data_index]:
                        an_value = int(row[data_index][-1])
                        # Explain the index formula!
                        last_cell_index = ((an_value+1)*2)-1
                        for n in range(last_cell_index+1):
                            index = data_index+n
                            element = row[index]
                            if type(element) == list:
                                for list_element in element:
                                    data.append(list_element)
                                    if '@an' in list_element:
                                        list_element_index = element.index(list_element)
                                        element[list_element_index] = u'EXTRACTED'
                            elif type(element) == unicode:
                                data.append(element)
                                row[index] = u'EXTRACTED'
                        if data:
                            self.table_data.append(data)

            except:
                print("Exception during data extraction for this row : ")
                print(str(row))

    def refine_data(self):
        if self.table_data:
            self.extract_references()
            self.delete_an()
            self.define_data_type()
            self.build_rows()

    def extract_references(self):
        for cell in self.table_data:
            temp_cell = []
            cell_index = self.table_data.index(cell)
            for element in cell:
                if type(element) == unicode:
                    if 'label' in element:
                        element_index = cell.index(element)
                        temp_cell.append(cell[element_index+1])
                        cell[element_index] = 'label_extracted'
            if temp_cell:
                self.table_data[cell_index] = temp_cell

    def resolve_dictionary_in_list(self, part_of_cell):
        if type(part_of_cell) == dict:
            for key in part_of_cell:
                self.temp_list.append(key)
                self.resolve_dictionary_in_list(part_of_cell[key])
        elif type(part_of_cell) == list:
            for item in part_of_cell:
                self.temp_list.append(item)
        elif type(part_of_cell) == unicode:
            self.temp_list.append(part_of_cell)
        else:
            return

    def delete_an(self):
        for cell in self.table_data:
            for element in cell:
                if type(element) == unicode:
                    if '@an' in element:
                        element_index = cell.index(element)
                        del cell[element_index]

    def define_data_type(self):
        for cell in self.table_data:
            self.cell_data_type(cell)
        for cell in self.table_data:
            for element in cell:
                self.element_data_type(cell, element)

    def is_float(self, value):
        try:
            float(value)
            return True
        except:
            return False

    def isTemplate(self, cell):
        try:
            if 'template' in cell:
                    return True
            else:
                raise ValueError
        except ValueError:
            return False

    def build_rows(self):
        temp_row = {}
        number_of_headers = len(self.table_headers)
        index = 0
        for data in self.table_data:
            try:
                header = self.table_headers[index]
                temp_row[header] = data
                index += 1
                if index == number_of_headers:
                    self.data_rows.append(temp_row)
                    temp_row = {}
                    index = 0
            except:
                print("Exception building rows.")
                print ("index: =" + str(index))
        self.data_statistics()

    def cell_data_type(self, cell):
        cell_index = self.table_data.index(cell)
        template = self.isTemplate(cell)
        if template:
            cell = self.refine_template_cell(cell)
            name = cell[0]
            if name == u'TA':
                value = cell[1]
                value = value.replace(" ", "")
                self.table_data[cell_index] = [value]

    def element_data_type(self, cell, element):
        try:
            element_index = cell.index(element)
            cell_index = self.table_data.index(cell)
            element = element.replace(".", "")
            element = element.replace(",", ".")
            number = self.is_float(element)

            if number:
                self.table_data[cell_index][element_index] = float(element)
        except AttributeError:
            print ("This element is probably a dictionary: " + str(element))

        except:
            print("EXCEPTION during the definition of data_type")

    def data_statistics(self):
        if self.data_rows:
            print ("This data has been extracted: " + str(self.data_rows))
            number_of_cells = 0
            for row in self.data_rows:
                number_of_cells += len(row)
            print ("Found " + str(len(self.data_rows)) + " rows and " + str(number_of_cells) + " cells")

    def refine_template_cell(self, cell):
        index_content = 0
        index_name = 0
        if 'content' in cell:
            index_content = cell.index('content') + 1
        if 'name' in cell:
            index_name = cell.index('name') + 1
        if index_content and index_name:
            cell_index = self.table_data.index(cell)
            self.table_data[cell_index] = [cell[index_name], cell[index_content]]
            return cell[index_name], cell[index_content]
        else:
            return False

    def erase_table_data(self):
        """

        :return:
        """
        self.tables_list = []
