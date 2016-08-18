import lxml.html as html
import re

import Mapper
import Table

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class HtmlTableParser:
    def __init__(self, html_doc_tree, chapter, graph, topic, resource, utils):


        self.doc_tree = html_doc_tree
        self.chapter = chapter
        self.graph = graph
        self.topic = topic
        self.resource = resource
        self.utils = utils
        self.logging = self.utils.logging

        self.tables = []
        self.current_html_table = None

        self.headers_not_mapped = {}

        # statistics regarding a resource
        self.tables_num = 0
        self.tables_analyzed = 0
        # Errors or problems regarding a table
        self.headers_not_resolved = 0
        # no headers found
        self.no_headers = 0
        # no data extracted
        self.no_data = 0

        # statistics regarding a table
        self.rows_num = 0
        self.headers_found_num = 0
        self.cell_per_row = 0
        self.rows_extracted_num = 0
        self.data_extracted_num = 0

        # As HtmlTableParsed is correctly initialized, we want to find tables
        self.find_wiki_table()

    def find_wiki_table(self):
        self.tables = self.doc_tree.findall('//table[@class=\'wikitable\']')
        sortable_tables = self.doc_tree.findall('//table[@class=\'wikitable sortable\']')
        for sort_table in sortable_tables:
            self.tables.append(sort_table)
        if len(self.tables):
            self.tables_num += len(self.tables)
            # Adding tables number to the total, used to print a final report
            self.utils.tot_tables += self.tables_num
            self.print_html(self.tables)
        else:
            print("No tables found for this resource.")
            self.logging.info("No Tables found for this resource.")


    def print_html(self, etree):
        for element in etree:
            print(html.tostring(element, pretty_print=True))

    def analyze_tables(self):
        for html_table in self.tables:
            self.tables_analyzed += 1

            self.rows_num = 0
            self.headers_found_num = 0
            self.rows_extracted_num = 0
            self.data_extracted_num = 0

            self.current_html_table = html_table
            tab = Table.Table()
            # TODO review this part
            tab.n_rows = self.count_elements(self.current_html_table)
            self.rows_num = tab.n_rows

            tab.table_attributes = html_table.attrib
            tab.table_section = self.find_table_section()
            self.logging.info("Table under section: %s" % tab.table_section)
            self.set_class(tab)
            self.find_headers(tab)

            # TODO make a decision
            # self.check_miss_subheaders(tab)

            if tab.headers:
                self.logging.info("Headers Found")
                self.refine_headers(tab)

                self.extract_data(tab)
                self.refine_data(tab)
                if tab.data_refined:
                    tab.count_data_cells_and_rows()
                    self.logging.info("Rows extracted: %d" % tab.data_refined_rows)
                    self.logging.info("Data extracted for this table: %d" % tab.cells_refined)
                    # update data cells extracted in order to make a final report
                    self.utils.data_extracted += tab.cells_refined
                    self.utils.rows_extracted += tab.data_refined_rows

                    mapper = Mapper.Mapper(self.chapter, self.graph, self.topic, self.resource,
                                             tab.data_refined, 'html', self.utils, tab.table_section)
                    mapper.map()

                    # Compose headers not mapped for this resource
                    for header in mapper.headers_not_mapped:
                        if header not in self.headers_not_mapped:
                            # Compose a list  with the name of the current resource [0] and with values in [1]
                            support_list = [self.resource, mapper.headers_not_mapped[header]]
                            '''
                            result Eg in self.headers_not_mapped = {'header1': ['resource1',[value0,value1...]], \
                                                                'header2': ['resource2',[value0, value1, value2...]]...}
                            '''
                            self.headers_not_mapped[header] = support_list
                else:
                    self.logging.debug("e3 - UNABLE TO EXTRACT DATA - resource: %s" % self.resource)
                    print("e3 UNABLE TO EXTRACT DATA")
                    self.no_data += 1
            else:
                self.logging.debug(
                    " e2 Unable to find headers - resource: " + str(self.resource))
                print("e2 UNABLE TO FIND HEADERS")
                self.no_headers += 1

        # Adding statistics values and errors to the extraction errors, in order to print a final report
        self.utils.tot_tables_analyzed += self.tables_analyzed
        self.utils.headers_errors += self.no_headers
        self.utils.not_resolved_header_errors += self.headers_not_resolved
        self.utils.data_extraction_errors += self.no_data

    def find_table_section(self):
        section_text = ""
        siblings = self.current_html_table.itersiblings(preceding=True)
        for sibling in siblings:
            if 'h' in sibling.tag:
                children = sibling.iterchildren()
                for child in children:
                    if 'id' in child.attrib:
                        h_text = child.text
                        if h_text:
                            section_text = h_text
                        else:
                            iter_text = child.itertext()
                            for text in iter_text:
                                section_text += text
                        section_text = section_text.encode('utf-8')
                        return section_text
        return self.resource

    def count_elements(self, wrapper):
        """
        :param wrapper:
        :return:
        """
        num_of_elems = 0
        for element in wrapper:
            num_of_elems += 1
        return num_of_elems

    def set_class(self, tab):
        if 'class' in self.current_html_table.attrib:
            tab.table_class = self.current_html_table.attrib['class']

    def find_headers(self, tab):
        try:
            for row in self.current_html_table:
                html_headers = row.findall('th')
                if html_headers:
                    self.set_header(row, tab)
        except:
            self.logging.warning("Error Finding the headers, resource: %s" % self.resource)

    def set_header(self, row, tab):
        # TODO refactor this function
        html_headers = row.findall('th')
        html_data = row.findall('td')
        headers = []
        if html_headers and not html_data:
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
        row = self.current_html_table.find('tr[' + str(row_index + 1) + ']')
        td_html = row.findall('td')
        th_html = row.findall('th')
        if td_html and not th_html:
            headers = self.compose_tab_headers(td_html)
            if headers:
                tab.headers.append(headers)

    def remove_row(self, tr_index):
        row = self.current_html_table.find('tr[' + str(tr_index) + ']')
        self.current_html_table.remove(row)
        print(html.tostring(self.current_html_table, pretty_print=True))

    def compose_tab_headers(self, html_headers):
        # TODO split in multiple simple functions
        headers = []
        for elem in html_headers:
            header_cell = {}

            current_text = ""
            text_iterator = elem.itertext()
            for text in text_iterator:
                # WYSIWYG
                current_text += text
            if '\n' in current_text:
                current_text = current_text.replace("\n", " ")

            attributes = elem.attrib
            if 'rowspan' in attributes:
                header_cell['rowspan'] = int(attributes['rowspan'])
            if 'colspan' in attributes:
                header_cell['colspan'] = attributes['colspan']
            else:
                header_cell['colspan'] = 1
            # TODO review this part to carve out anchors
            if current_text:
                header_cell['th'] = current_text
            else:
                header_cell['th'] = ''
                self.logging.debug("Header not resolved")
                self.headers_not_resolved += 1
            headers.append(header_cell)
        if headers:
            return headers

    def refine_headers(self, tab):

        self.expand_colspan_cells(tab.headers)

        self.resolve_rowspan(tab.headers)

        self.remove_html_encode_errors(tab.headers, u'\xa0')

        self.remove_citations(tab)

        self.print_headers(tab)

        self.associate_super_and_sub_headers(tab)

        self.encode_headers(tab)
        print("Headers refined")

    def print_headers(self, tab):
        print("These are the headers found: ")
        for row in tab.headers:
            for th in row:
                print(th['th'])

    def resolve_rowspan(self, rows):
        try:
            for row in rows:
                row_index = rows.index(row)
                for cell in row:
                    cell_index = row.index(cell)
                    if 'rowspan' in cell and cell['rowspan'] > 1:
                        cell['rowspan'] -= 1
                        cell_copy = dict(cell)
                        cell_copy['th'] = ""
                        rows[row_index+1].insert(cell_index, cell_copy)
        except:
            print("Error resolving rowspan")

    def remove_html_encode_errors(self, headers, error):
        for row in headers:
            for header in row:
                header['th'] = header['th'].replace(error, u'')

    def remove_citations(self, tab):
        """
        Method used to remove citations from the headers. Eg in some wiki table, users use to explain the headers
        they chose using citations to refer to other web pages or to a simple text explanation.
        Take a look at https://it.wikipedia.org/wiki/Elezioni_politiche_italiane_del_1968 :
        in the first table you can find as last header "Segretario [1]". After remove_citations(), the new string would
        be "Segretario".
        It is useful to remove citations as they are used only in few tables, otherwise you can't find them in others.
        So, if you have designed mapping rules for the header Segretario, all data under Segretario[1] wouldn't be
        mapped without remove_citation().
        :param tab: Table class instance containing the table which headers have to be refined from citations
        :return: nothing
        """
        for row in tab.headers:
            for header in row:
                try:
                    citations = re.findall(r'\[\d+\]', header['th'])
                    if citations:
                        for citation in citations:
                            header['th'] = header['th'].replace(citation, '')
                except TypeError:
                    print("TypeError searching for citations")

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
                        if sub['th']:
                            composition = {'th': sup['th'] + " - " + sub['th'], 'colspan': sub['colspan']}
                        else:
                            composition = {'th': sup['th'], 'colspan': sub['colspan']}
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

    def encode_data(self, tab):
        for row in tab.data_refined:
            for key in row.keys():
                for data in row[key]:
                    if type(data) == unicode:
                        data = data.encode('ascii', 'replace')

    def extract_data(self, tab):
        for row in self.current_html_table:
            data_in_row = row.findall('td')
            if data_in_row:
                table_data = row.iterchildren()
                data_row = []
                for cell in table_data:
                    data_cell = []
                    anchors = self.find_anchors(cell)
                    if anchors:
                        for anc in anchors:
                            if anc:
                                data_cell.append(anc)

                    td = self.find_td_text(cell)
                    if td:
                        data_cell.append(td)

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
        cell_text = ""
        text_iterator = cell.itertext()
        for text in text_iterator:
            # WYSIWYG
            cell_text += text
        if type(cell_text) == unicode:
            if u'\xa0' in cell_text:
                cell_text = cell_text.replace(u'\xa0', u' ')
        if cell_text:
            data_cell['td'] = cell_text
        else:
            data_cell = None

        return data_cell

    # TODO refactor this function
    '''
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
    '''
    def refine_data(self, tab):
        print("Refining data ...")
        try:
            self.delete_useless_rows(tab, 'Totale')
            self.expand_colspan_cells(tab.data)
            self.resolve_data_type(tab)
            self.join_data_and_headers(tab)
            self.encode_data(tab)
            print ("done")
            self.logging.info("Data refined")
        except:
            self.logging.debug("Exception refining data")

    def delete_useless_rows(self, tab, tag):
        for row in tab.data:
            for cell in row:
                for element in cell:
                    if 'td' in element and element['td'] == tag:
                        tab.data.remove(row)

    def expand_colspan_cells(self, rows):
        try:
            for row in rows:
                for cell in row:
                    for element in cell:
                        colspan = 0
                        if 'colspan' in element:
                            if type(element) == str:
                                colspan = int(cell['colspan'])
                            elif type(element) == dict:
                                colspan = int(element['colspan'])
                            if colspan > 1:
                                cell_index = row.index(cell)
                                if type(element) == str:
                                    cell['colspan'] = 1
                                elif type(element) == dict:
                                    element['colspan'] = 1
                                for index in range(0, colspan - 1):
                                    row.insert(cell_index, cell)
        except TypeError:
            print("TypeError trying to expand colspan cells")
        except ValueError:
            print("ValueError trying to expand colspan cells")

    def resolve_data_type(self, tab):
        for row in tab.data:
            temp_row = []
            for cell in row:
                temp_cell = []
                for element in cell:
                    data = []
                    if 'a' in element:
                        data = element['a'].replace(' ', '_')
                    elif 'td' in element:
                        data = element['td']
                        # data = element['td'].replace(' ', '_')
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
                        self.logging.debug("Exception building rows. \n index = %s" % index)
                        print("Exception building rows.")
                        print ("index: =" + str(index))
                if temp_row:
                    tab.data_refined.append(temp_row)

