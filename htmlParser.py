import lxml.html as html
from lxml.etree import _Element
import logging

import table
import mapper

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class HtmlParser:
    def __init__(self, html_doc_tree, chapter, graph, topic, resource):

        self.doc_tree = html_doc_tree
        self.chapter = chapter
        self.graph = graph
        self.topic = topic
        self.resource = resource

        self.tables = []
        self.find_wiki_table()
        self.rows_num = 0
        self.last_html_table = None

    def find_wiki_table(self):
        self.tables = self.doc_tree.findall('//table[@class=\'wikitable\']')
        self.print_html(self.tables)

    def print_html(self, etree):
        for element in etree:
            print(html.tostring(element, pretty_print=True))

    def analyze_tables(self):
        for html_table in self.tables:
            self.last_html_table = html_table
            tab = table.Table()
            tab.n_rows = self.count_elements(self.last_html_table)
            tab.table_attributes = html_table.attrib
            self.find_headers(tab)
            self.check_miss_subheaders(tab)
            if tab.headers:
                print("Resource : " + self.resource + "Headers Found")
                print("These are the headers found: ")
                for row in tab.headers:
                    for th in row:
                        print(th['th'])
                self.associate_super_and_sub_headers(tab)
                self.encode_headers(tab)
                self.extract_data(tab)
                self.refine_data(tab)
                if tab.data_refined:
                    map_tool = mapper.Mapper(self.chapter, self.graph, self.topic, self.resource,
                                             tab.data_refined, 'html')
                    map_tool.map()
                else:
                    logging.debug("e3 - UNABLE TO EXTRACT DATA - resource: " + str(self.resource))
                    print("e3 UNABLE TO EXTRACT DATA")
            else:
                logging.debug(
                    " e2 Unable to find headers - resource: " + str(self.resource))
                print("e2 UNABLE TO FIND HEADERS")

    def count_elements(self, wrapper):
        """
        :param wrapper:
        :return:
        """
        num_of_elems = 0
        for element in wrapper:
            num_of_elems += 1
        return num_of_elems

    def find_headers(self, tab):
        try:
            for row in self.last_html_table:
                html_headers = row.findall('th')
                if html_headers:
                    self.set_header(row, tab)
        except:
            logging.warning("Error Finding the headers, resource: " + str(self.resource))

    def set_header(self, row, tab):
        # TODO refactor this function
        html_headers = row.findall('th')
        headers = []
        if html_headers:
            headers = self.compose_tab_headers(html_headers)
        if headers:
            tab.headers.append(headers)

    def check_miss_subheaders(self, tab):
        """

        :param tab:
        :return:
        """
        if tab.headers:
            last_header = tab.headers[len(tab.headers) - 1]
            header_error = False
            for th in last_header:
                if 'colspan' in th:
                    if th['colspan'] > 1:
                        header_error = True
            if header_error:
                print ("Some headers are missing, trying to reconstruct sub headers")
                self.set_new_header(len(tab.headers), tab)
                self.remove_row(len(tab.headers))
        else:
            try:
                self.set_new_header(0, tab)
                self.remove_row(1)
            except:
                print("Something wrong setting a new header...")

    def set_new_header(self, row_index, tab):
        row = self.last_html_table.find('tr[' + str(row_index + 1) + ']')
        html = row.findall('td')
        if html:
            headers = self.compose_tab_headers(html)
            if headers:
                tab.headers.append(headers)

    def remove_row(self, tr_index):
        row = self.last_html_table.find('tr[' + str(tr_index) + ']')
        self.last_html_table.remove(row)

        print(html.tostring(self.last_html_table, pretty_print=True))

    def compose_tab_headers(self, html_headers):
        headers = []
        for elem in html_headers:
            header_cell = {}
            attributes = elem.attrib
            if 'colspan' in attributes:
                header_cell['colspan'] = attributes['colspan']
            else:
                header_cell['colspan'] = 1
            if elem.text:
                header_cell['th'] = elem.text
            else:
                anchor = self.find_anchors(elem)
                if anchor:
                    # WYSIWYG
                    header_cell['th'] = anchor[0]['text']
                else:
                    header_cell['th'] = 'Header_Not_Resolved'
                    logging.debug("Header not resolved")
            headers.append(header_cell)
        if headers:
            return headers

    def associate_super_and_sub_headers(self, tab):
        try:
            headers_copy = tab.headers
            for iteration in range(0, len(headers_copy) - 1):
                super_headers = headers_copy[0]
                sub_headers = headers_copy[1]
                headers_copy.remove(super_headers)
                headers_copy.remove(sub_headers)
                temp_header = []
                for sup in super_headers:
                    colspan = int(sup['colspan'])
                    for n_of_sub_related in range(0, colspan):
                        sub = sub_headers[0]
                        composition = {'th': sup['th'] + " - " + sub['th'], 'colspan': sub['colspan']}
                        temp_header.append(composition)
                        sub_headers.remove(sub)
                headers_copy.insert(0, temp_header)
            for element in headers_copy[0]:
                tab.headers_refined.append(element)
            print "New headers:"
            for header in tab.headers_refined:
                print(header['th'])
        except:
            print("Error gathering sub and super headers.. resource: " + str(self.resource))

    def encode_headers(self, tab):
        for header in tab.headers_refined:
            header['th'] = header['th'].encode('ascii', 'replace')

    def extract_data(self, tab):
        for row in self.last_html_table:
            table_data = row.findall('td')
            if table_data:
                data_row = []
                for cell in table_data:
                    data_cell = []
                    td = self.find_td_text(cell)
                    if td:
                        data_cell.append(td)
                    anchors = self.find_anchors(cell)
                    if anchors:
                        for anc in anchors:
                            if anc:
                                data_cell.append(anc)
                    if not data_cell:
                        data_cell.append({'td': '-'})
                    data_row.append(data_cell)

                tab.data.append(data_row)

    def find_anchors(self, cell):
        anchors = cell.findall('a')
        data = []
        for anchor in anchors:
            anchor_data = {}
            attributes = anchor.attrib
            text = anchor.text
            if text:
                anchor_data['text'] = text
            if 'class' in attributes and attributes['class'] == 'new':
                anchor_data['a'] = text
            elif 'title' in attributes:
                anchor_data['a'] = attributes['title']
            data.append(anchor_data)
        return data

    def find_td_text(self, cell):
        data_cell = {}
        attributes = cell.attrib
        for attrib in attributes:
            data_cell[attrib] = attributes[attrib]
        text = cell.text
        if text:
            text = text.replace(",", ".")
            data_cell['td'] = unicode(text)
        else:
            b = self.resolve_sub_tag(cell, 'b')
            if b:
                data_cell['td'] = unicode(b)
            span = self.resolve_sub_tag(cell, 'span')
            if span:
                data_cell['td'] = span

        return data_cell

    def resolve_sub_tag(self, cell, tag):
        sub_tag = cell.find(tag)
        if type(sub_tag) == _Element:
            text = sub_tag.text
            if tag == 'span':
                attributes = sub_tag.attrib
                if 'style' in attributes and attributes['style'] == 'white-space:nowrap; display:inline-block':
                    text = text.replace(" ", "")
            if text:
                return text
            else:
                anchor = self.find_anchors(sub_tag)
                if anchor:
                    return anchor[0]['a']
        else:
            return None

    def refine_data(self, tab):
        print("Refining data ...")
        self.delete_useless_rows(tab)
        self.expand_colspan_cells(tab)
        self.resolve_data_type(tab)
        self.join_data_and_headers(tab)
        print ("done")

    def delete_useless_rows(self, tab):
        for row in tab.data:
            for cell in row:
                for element in cell:
                    if 'td' in element and element['td'] == 'Totale':
                        tab.data.remove(row)

    def expand_colspan_cells(self, tab):
        for row in tab.data:
            for cell in row:
                for element in cell:
                    if 'colspan' in element:
                        colspan = int(element['colspan'])
                        if colspan > 1:
                            cell_index = row.index(cell)
                            element['colspan'] = 1
                            for index in range(0, colspan - 1):
                                row.insert(cell_index, cell)

    def resolve_data_type(self, tab):
        for row in tab.data:
            temp_row = []
            for cell in row:
                temp_cell = []
                for element in cell:
                    data = []
                    if 'a' in element:
                        data = element['a'].replace(' ', '_')
                        data = unicode(data)
                    elif 'td' in element:
                        data = element['td'].replace(' ', '_')
                        data = data.encode('utf-8')
                        # data = data.replace('.', '')
                        number = self.is_float(data)
                        if number:
                            data = float(data)
                    if data or data == 0.0:
                        temp_cell.append(data)
                if temp_cell:
                    temp_row.append(temp_cell)
            if temp_row:
                tab.data_filtered.append(temp_row)

    def is_float(self, value):
        try:
            float(value)
            return True
        except:
            return False

    def join_data_and_headers(self, tab):
        temp_row = {}
        if tab.headers:
            number_of_headers = len(tab.headers[0])

            for row in tab.data_filtered:
                index = 0
                for data in row:
                    try:
                        header = tab.headers[0][index]['th']
                        temp_row[header] = data
                        index += 1
                        if index == number_of_headers:
                            tab.data_refined.append(temp_row)
                            temp_row = {}
                            index = 0
                    except:
                        print("Exception building rows.")
                        print ("index: =" + str(index))
                if temp_row:
                    tab.data_refined.append(temp_row)
