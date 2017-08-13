# coding=utf-8

import lxml.html as html
import re
import string
import Mapper
import Table

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class HtmlTableParser:
    """
    HtmlTableParser is a class used to analyze the tables for a preselected resource.

    It reconstructs the structure for every table, retrieving the headers and refining them.
    Then data cells are extracted and refined.
    Finally every cell is joined with the corresponding header composing a data structure which a Mapper object
     would use to build RDF triples.

    Public methods:
        -analyze_tables() # used to start the analysis of tables and the extraction of rdf triples

    Properties:
        -tables_num # number of tables for this resource
        -tables_analyzed # number of tables actually analyzed
        -no_headers # number of tables which headers could not be found
        -headers_not_resolved # number of time it is impossible to resolve the text of a header
        -no_data # number of data cells found

    """

    def __init__(self, html_doc_tree, chapter, graph, topic, resource, utils, mapping = False):
        """
        HtmlTableParser is a class used to analyze the tables for a preselected resource.

        Then data cells are extracted and refined.
        Finally every cell is joined with the corresponding header composing a data structure which a Mapper object
            would use to build RDF triples.
        After the creation of a HtmlTableParser please call the analyze_tables() method to start the analysis.

        :param html_doc_tree: is a lxml.etree._ElementTree object containing a html representation of the wiki page
        :param chapter: (str) a two alpha-characters string representing the chapter of wikipedia user chose.
        :param graph: a RDFlib graph
        :param topic: (str) a string representing the common topic of the resources considered.
        :param resource: (str) the resource selected
        :param utils: (Utilities object) utilities object used to access common log and to set statistics values used to
                print a final report.
        """

        self.doc_tree = html_doc_tree
        self.chapter = chapter
        self.graph = graph
        self.topic = topic
        self.resource = resource
        self.utils = utils
        self.logging = self.utils.logging
        self.mapping = mapping
        # list of tables in html
        self.tables = []
        self.current_html_table = None
        self.all_tables = []
        # statistics regarding a resource
        self.tables_num = 0  # number of tables
        self.tables_analyzed = 0  # number of tables analyzed

        # Errors or problems regarding a table
        # This value is used to count the times parser cannot find the text inside a header cell
        self.headers_not_resolved = 0
        # This value is used to count the times parser cannot find headers for the current table
        self.no_headers = 0
        # This value is used to count the times parser cannot find data cells for the current table
        self.no_data = 0

        # This value is used to count resource's triples.
        self.reification_index = 1

        # statistics regarding a table
        self.headers_found_num = 0  # counts header cells found
        self.rows_extracted_num = 0  # counts the extracted data rows
        self.data_extracted_num = 0  # counts the extracted data cells

        self.utils.logging.info("Analyzing resource: " + self.resource)
        # As HtmlTableParsed is correctly initialized, we find tables with find_wiki_tables()
        self.find_wiki_tables()

    def find_wiki_tables(self):
        """
        Find and set(in a list) tables from a lxml.etree._ElementTree object containing the whole wiki page.

        It uses XPath syntax (reference https://www.w3.org/TR/xpath/) to find and isolate tables of particular classes.
        In fact, the tables we want to analyze are the classical and the sortable wikitable (reference at
        https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Accessibility/Data_tables_tutorials)
        The method use lxml.etree._ElementTree.findall() method to actually retrieve tables.
        :return: nothing
        """
        # class='wikitable' are added to self.tables (list)
        self.tables = self.doc_tree.findall('//table[@class=\'wikitable\']')

        # now class = 'wikitable sortable' tables are found
        sortable_tables = self.doc_tree.findall('//table[@class=\'wikitable sortable\']')
        # now class = 'wikitable collapsible' tables are found
        collapsible_tables = self.doc_tree.findall('//table[@class=\'wikitable sortable collapsible\']')
        # Adding sortable tables to the tables list
        for sort_table in sortable_tables:
            self.tables.append(sort_table)
        # Adding collapsible tables to the tables list
        for collaps_table in collapsible_tables:
            self.tables.append(collaps_table)
        # If at least a table is found
        if self.tables:
            # count the number of tables and add it to the total count
            self.tables_num += len(self.tables)
            # Adding tables number to the total, used to print a final report
            self.utils.tot_tables += self.tables_num

        # if no tables are found
        else:

            print("No tables found for this resource.")
            self.logging.info("No Tables found for this resource.")

    def analyze_tables(self):
        """
        Method used to analyze tables structure, compose a simple data structure containing data cells and the
         corresponding headers and give it to a Mapper object.

        Principal method of a HtmlTableParser object, it finds out headers and data, refines them, and finally join
         each others in order to be mapped by a Mapper object.

        :return:nothing
        """
        # Iterates over tables list
        for html_table in self.tables:

            # Update the analyzed table count
            self.tables_analyzed += 1

            # Instantiating statistics for this table
            self.headers_found_num = 0
            self.rows_extracted_num = 0
            self.data_extracted_num = 0

            # set as a class attribute the current html table
            self.current_html_table = html_table

            # create a Table object to contain data structures and statistics for a table
            tab = Table.Table()
            # set tab.n_rows as a result of count_rows()
            tab.n_rows = self.count_rows()
            # set other table properties, such as table attributes
            tab.table_attributes = html_table.attrib
            # find out the table section using find_table_section()
            tab.table_section = self.find_table_section()
            print "Section found: ", tab.table_section
            self.logging.info("Table under section: %s" % tab.table_section)

            # find headers for this table
            self.find_headers(tab)

            # Chose to not use this method as it resolves users' made errors but create problems with correctly
            #  written table
            # self.check_miss_subheaders(tab)

            # if headers have been found
            if tab.headers:
                self.logging.info("Headers Found")

                # Refine headers found
                self.refine_headers(tab)

                # Once the headers are refined, start to extract data cells
                self.extract_data(tab)

                # Refine data cells found
                self.refine_data(tab)

                # If data are correctly refined
                if tab.data_refined:
                    # Count data cells and data rows using table.count_data_cells_and_rows()
                    tab.count_data_cells_and_rows()
                    self.logging.info("Rows extracted: %d" % tab.data_refined_rows)
                    self.logging.info("Data extracted for this table: %d" % tab.cells_refined)

                    # update data cells extracted in order to <make a final report
                    self.utils.data_extracted += tab.cells_refined
                    self.utils.rows_extracted += tab.data_refined_rows
                    # Start the mapping process
                    self.all_tables.append(tab)
                    if self.mapping:
                        # Create a MAPPER object in order to map data extracted
                        mapper = Mapper.Mapper(self.chapter, self.graph, self.topic, self.resource, tab.data_refined,
                                               self.utils, self.reification_index, tab.table_section, )
                        mapper.map()
                        self.reification_index = mapper.reification_index

                # If no data have been found for this table report this condition with tag E3
                else:
                    self.logging.debug("E3 - UNABLE TO EXTRACT DATA - resource: %s" % self.resource)
                    print("E3 UNABLE TO EXTRACT DATA")
                    # Update the count of tables with this condition (no data found)
                    self.no_data += 1

            # if no headers have been found report this critical condition with the tag E2
            else:
                self.logging.debug(
                    " E2 Unable to find headers - resource: " + str(self.resource))
                print("E2 UNABLE TO FIND HEADERS")
                # Update the count of tables with this condition (no headers found)
                self.no_headers += 1

        print "Resource analysis completed \n\n"
        # Adding statistics values and errors to the extraction errors, in order to print a final report
        self.utils.tot_tables_analyzed += self.tables_analyzed
        self.utils.headers_errors += self.no_headers
        self.utils.not_resolved_header_errors += self.headers_not_resolved
        self.utils.data_extraction_errors += self.no_data

    def find_table_section(self):
        """
        Method used to find under which section a table resides. Section means every heading tag (<h>) as in wiki pages
        sections are defined by those tag.
        For tables which are at the very top of the page, and that don't have an actual section, the title of the page
         is set as the section
        :return (str) section_text: if a section is found it returns his text, otherwise it returns the page's title
        """

        section_text = ""
        # creating an iterator containing preceding siblings of the current table's tag
        siblings = self.current_html_table.itersiblings(preceding=True)

        for sibling in siblings:
            # test if this sibling is a heading
            if 'h' in sibling.tag:
                # if so iterate over the children of the heading
                children = sibling.iterchildren()
                for child in children:
                    """
                    If you check any wiki page you can find the real tag containing the heading's text is
                    that with a id in his attributes
                    """
                    if 'id' in child.attrib:
                        # taking the text of this heading
                        h_text = child.text
                        if h_text:
                            section_text = h_text
                        # This block is used because in some cases there are more than one level of tag inside the <h>
                        else:
                            iter_text = child.itertext()
                            for text in iter_text:
                                # need only first item
                                if not section_text:
                                    section_text += text

                        # encode in utf-8 the section text
                        section_text = self.utils.delete_accented_characters(section_text)
                        section_text = section_text.encode('utf-8')
                        section_text = section_text.translate(None, string.punctuation)
                        return section_text

        # if a <h> tag was not found return the page's title
        string.punctuation = string.punctuation.replace("_", "")
        self.resource = self.utils.delete_accented_characters(self.resource)
        self.resource = self.resource.encode('utf-8')
        self.resource = self.resource.translate(None, string.punctuation)
        return self.resource

    def count_rows(self):
        """
        Simply count rows in a html table
        :return num_of_rows: number or rows found
        """
        num_of_rows = 0
        for row in self.current_html_table:
            num_of_rows += 1
        return num_of_rows

    def find_headers(self, tab):
        """
         This method find headers rows, call compose_tab_headers to have a data structure
          Eg.{'colspan': '3', 'th': 'Candidati'} to add to the tab.headers list
        :param tab: is a Table object at which add the headers found
        :return: nothing
        """
        try:
            # for every the table's row
            started_data = 0    # variable for checking if we started reading data, so we can't find other headers
            # used to delete header that are in last row.
            for row in self.current_html_table:
                # find header cell
                html_header_row = row.findall('th')
                # find also data cell in the same row
                html_data = row.findall('td')
                header_row = ""
                # we consider as a table header rows, only those ones with no data cells
                # we will use this case only if the tables if well formed.
                # It won't read the last row as header.
                if html_header_row and not html_data and started_data == 0:
                    # headers are composed in the form of a dictionary Eg. {'colspan': '3', 'th': 'Candidati'}
                    header_row = self.compose_tab_headers(html_header_row)
                # another particular case where headers are in columns instead of being in a row.
                elif html_data and html_header_row:
                    # headers are composed in the form of a dictionary Eg. {'colspan': '3', 'td': 'Candidati'}
                    header_row = self.compose_tab_headers(html_header_row)
                    # variable that will be useful for mapper class. In this way we can distinct
                    # different table types.
                    tab.vertical_table = 1
                elif html_data:
                    started_data = 1
                # if headers are found append them to the tab.headers list
                if header_row:
                    tab.headers.append(header_row)
        except:
            self.logging.warning("Error Finding the headers, resource: %s" % self.resource)

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

    def compose_tab_headers(self, headers_row):
        """
         Method used to create a dictionary containing a header cell text along with his attributes.
         It compose a list of dictionaries as [{'colspan': '3', 'th': 'Candidati'},
          {'colspan': 1, 'th': 'Grandi elettori'}]
        compose_tab_header use a WYSIWYG approach as the header cell extracted is what you can see as text at the wiki
         page.
        :param headers_row: a row of headers.
        :return: a list containing dictionaries of table header cells
        """
        headers = []
        for cell in headers_row:
            # create an empty dictionary which would contain the header cell
            header_cell = {}
            # create a string which would contain header cell text
            current_text = ""

            # iterating over the text of the cell
            text_iterator = cell.itertext()
            for text in text_iterator:
                # adding all the text pieces
                current_text += text

            # deleting newline tag
            if '\n' in current_text:
                current_text = current_text.replace("\n", " ")

            # taking cell's attributes
            attributes = cell.attrib
            # adding rowspan attribute to the dictionary
            if 'rowspan' in attributes:
                header_cell['rowspan'] = int(attributes['rowspan'])
            # adding colspan attribute to the dictionary
            if 'colspan' in attributes:
                header_cell['colspan'] = attributes['colspan']
            else:
                # if there is not a colspan attribute, set the dictionary's colspan to 1
                header_cell['colspan'] = 1

            # adding the text found to the header_cell
            if current_text:
                header_cell['th'] = current_text

            # if no text has been found
            else:
                # Add an empty string as text for header_cell.
                # It's important to not delete empty cells to preserve table's structure
                header_cell['th'] = ''
                # States the impossibility to find text for this cell
                self.logging.debug("Header not resolved")
                # Add this header to the not resolved one count
                self.headers_not_resolved += 1

            # Append this cell to the headers list then continues for other cells
            header_cell['th'] = header_cell['th'].replace("'", ".")
            headers.append(header_cell)

        # Once every row has been tested, return headers
        if headers:
            return headers

    def refine_headers(self, tab):
        """
        Method used to refine headers rows and cell, in order to have clean text cells.

        A lot of method are called here to refine headers.

        Typically you have to firstly expands cells with colspan > 1 and rowspan > 1 in order to make a homogeneous
        structure.
        Then it is useful to correct errors here: encode_errors, part of text you don't want (as citations).
        Finally header rows are joined together in order to build up a single cells row from all the header rows.
            This is useful to let the mapping phase be as easiest as possible: you have to map cells using the headers
            in cascade.
            So Eg. refer to https://en.wikipedia.org/wiki/Channel_Tunnel , the final header cells we want
            to have is something like "Year","Passengers transported... - by Eurostar(actual ticket sales)",
            "Passengers transported... - by Eurotunnel Passenger Shuttles(estimated, millions)",
            "Passengers transported... - Total(estimated, millions)" with a WYSIWYG approach.

        :param tab: Table object used to store tables structures
        :return: nothing
        """

        # Expand cells with a colspan > 1
        self.expand_colspan_cells(tab.headers)

        # Expand cells with a rowspan attribute > 1
        self.resolve_rowspan(tab.headers)

        # Remove text encoding errors. Eg here we delete u'\xa0' == html'&nbsp'
        self.remove_html_encode_errors(tab.headers, u'\xa0')

        # Remove possible citations in the text of headers. They are noisy and useless for mapping purpose.
        self.remove_citations(tab)

        # Print in the console headers to have a visual feedback of which are header cells found and refined
        # self.print_headers(tab)

        # We want to make a single header's row, associating every header row with the next one.
        if tab.vertical_table == 0:
            self.associate_super_and_sub_headers(tab)
        else:
            # don't have to associate header with super header, because it is a table where each row has: header - data
            for element in tab.headers:
                tab.headers_refined.append(element[0])
        # Finally encode headers
        self.encode_headers(tab)

    def print_headers(self, tab):
        """
        Method used to print in the console the header cells found and refined before make a single row from all the
         header's rows.

        :param tab: Table object containing the headers to print out
        :return:
        """
        print("These are the headers found: ")
        # Iterate over table headers
        for row in tab.headers:
            # Iterate over header cells
            for th_cell in row:
                # Print text for that header
                print(th_cell['th'])

    def resolve_rowspan(self, rows):
        """
        Method used to resolve problems with cells with a rowspan attribute > 1.

        Similarly to the colspan attribute, a rowspan > 1 indicates a cell spread over more than one row.
        It is very important to replicate the considered cell over the rows (for 'rowspan' times) in order to respect
         the actual table's structure.
        Eg. refer to https://en.wikipedia.org/wiki/Channel_Tunnel. The first table has as first header a "Year" cell
        with a rowspan > 1

        :param rows: a list of table's headers rows
        :return: nothing
        """
        try:
            # Iterating over rows
            for row in rows:
                # Calculate the index of the current row inside the rows list
                row_index = rows.index(row)
                # Iterate over cells in the current row
                for cell in row:
                    # Calculate the index of this cell inside the current row
                    cell_index = row.index(cell)
                    # If cell have a 'rowspan' attribute and this is > 1
                    if 'rowspan' in cell and cell['rowspan'] > 1:
                        # decrease rowspan by 1 so that in the next row the same cell would have a rowspan = "rowspan-1"
                        cell['rowspan'] -= 1
                        # copy the considered cell
                        cell_copy = dict(cell)
                        # for the rowspan of headers is important to set the new header cell text to an empty string
                        cell_copy['th'] = ""
                        # Insert the copied cell in the next row and continue with cells and rows iteration
                        rows[row_index+1].insert(cell_index, cell_copy)
        except:
            print("Error resolving rowspan")

    def remove_html_encode_errors(self, headers, error):
        """
        Use this method to remove html special characters (Eg. &nbps), encoding errors or other unicode text.

        Simply pass headers rows to the method and the error, as a unicode string, you want to correct

        :param headers: rows list of headers
        :param error: unicode string you want to delete from header cells
        :return: nothing
        """
        # Iterates over headers
        for row in headers:
            # Iterate over header cells
            for header in row:
                # Replace 'error' with u'' in the text of this header cell
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
        # Iterate over header rows
        for row in tab.headers:
            # Iterates over header cells
            for header in row:
                try:
                    # Try to find citations with a regex that match header text with:  [unspecified_number_of_digits]
                    citations = re.findall(r'\[\d+\]', header['th'])
                    # If at least a citation is found
                    if citations:
                        # Iterates over citations as it is a list of citations
                        for citation in citations:
                            # Delete citation string from the header cell's text
                            header['th'] = header['th'].replace(citation, '')
                except TypeError:
                    print("TypeError searching for citations")

    def associate_super_and_sub_headers(self, tab):
        """
        Method used to build a single header row from the refined header's rows.

        It takes two cells (same index) at a time from consecutive header's rows.
        Then melt them in a single cell aggregating first cell's text with the second one.

        :param tab: Table object containing headers
        :return:
        """
        try:
            # make a copy of table headers
            headers_copy = tab.headers
            # Iterates for a 'rows number' times
            for iteration in range(0, len(headers_copy) - 1):

                # Set super and sub header row (in every iteration they are melted so we'll have 1 row from 2 of them)
                # Super header is the first row
                super_headers = headers_copy[0]
                # Sub header is the second row
                sub_headers = headers_copy[1]

                # Removing super and sub header from the header's rows copy
                headers_copy.remove(super_headers)
                headers_copy.remove(sub_headers)

                # create a temporary header row
                temp_header = []

                # for every cell in super_header row
                for sup in super_headers:

                    # set the correct colspan for this cell
                    colspan = int(sup['colspan'])

                    # Melt the superior cell with a number of subsequent header's row equal to the colspan attribute
                    for n_of_sub_related in range(0, colspan):

                        # Set sub cell as the first cell in sub_headers list
                        sub = sub_headers[0]
                        # If sub cell has text
                        if sub['th']:
                            # If even the superior cell has text
                            if sup['th']:
                                # Melt sup and sub cells as a unique header cell with a joined text
                                composition = {'th': sup['th'] + " - " + sub['th'], 'colspan': sub['colspan']}
                            else:
                                # If sup cell hasn't text, avoid the dash to be inserted as it is useless.
                                composition = {'th': sub['th'], 'colspan': sub['colspan']}
                        else:
                            # If sub cell hasn't text, simply make a collage of sup text and sub colspan.
                            composition = {'th': sup['th'], 'colspan': sub['colspan']}

                        # Append the dictionary created (composition) to the temporary_headers list
                        temp_header.append(composition)
                        # Remove sub cell from the list of sub_headers
                        sub_headers.remove(sub)

                # Insert the row created (temp_header) in the headers_copy at first place, so that the iteration could
                # continue
                headers_copy.insert(0, temp_header)

            # Once iteration is finished, append every cell of last remaining header row in tab.headers_refined list.
            for element in headers_copy[0]:
                tab.headers_refined.append(element)

        except:
            print("Error gathering sub and super headers.. resource: " + str(self.resource))

    def encode_headers(self, tab):
        """
        Method used to encode headers in ascii.

        :param tab: Table object containing headers
        :return:
        """

        for header in tab.headers_refined:
            header['th'] = header['th'].encode('ascii', 'replace')
            if "?" in header['th']:
                header['th'] = header['th'].replace("?", ".")

    def encode_data(self, tab):
        """
        Encode data in ascii
        :param tab: Table object
        :return: nothing
        """
        # Iterates over rows in tab.data_refined
        for row in tab.data_refined:
            # Iterates over the headers
            for key in row.keys():
                # Iterates over data ( row= {'header': [data], 'header':[data],...})
                for data in row[key]:
                    if type(data) == unicode:
                        data = data.encode('ascii', 'replace')

    def extract_data(self, tab):
        """
        Method to extract data cells from a table.

        It iterates over table's row, finding out simple text and even anchors' text (useful to make a correct mapping)
        It composes data_rows a list containing rows of data (each cell is a list of string values)
        :param tab: Table object containing data
        :return: nothing
        """
        # Iterates over the rows of table
        for row in self.current_html_table:
            # Find if there are data cells
            data_in_row = row.findall('td')

            # If so iterates over children tags (data cells) of current row
            if data_in_row:
                table_data = row.iterchildren()

                # Create an empty list which will contain data cells (a row of cells)
                data_row = []

                # Iterates over cells in this row
                for cell in table_data:
                    # Create an empty list in order to contain text value and anchors' text and href attribute
                    data_cell = []

                    # Call find_anchors to compose a list of anchors contained in this data cell
                    anchors = self.find_anchors(cell)

                    # if anchors is not an empty list
                    if anchors:
                        # Iterates over anchors and append data for each anchor to the cell's list of data
                        for anc in anchors:
                            if anc:
                                data_cell.append(anc)

                    # Call find_td_text to compose a dictionary containing text of this cell
                    td = self.find_td_text(cell)

                    # If some text has been found
                    if td:
                        # Append the dictionary containing the text to cell's list
                        data_cell.append(td)

                    # At last, if neither anchors or text has been found, append {'td': '-'}  in order to mark an empty
                    # cell
                    if not data_cell:
                        data_cell.append({'td': '-'})

                    # Append the list for this cell to the data's row
                    data_row.append(data_cell)

                # Once iteration over row is finished, append it to tab.data list
                tab.data.append(data_row)

    def find_anchors(self, cell):
        """
        Method used to find and extract anchors inside a given cell, returning a list of them.

        :param cell: a cell which anchors you want to extract
        :return data: a list of anchors found
        """
        # Find every anchor tag inside the cell
        anchors = cell.findall('a')

        # Create a list which would contain anchors' text
        data = []
        # Iterates over anchors list
        for anchor in anchors:
            # Creating a dictionary which would contain data for a single anchor
            anchor_data = {}

            # Extract anchor's attribute
            attributes = anchor.attrib

            # Extract text for this attribute
            text = anchor.text
            # If there is text
            if text:
                # Add the text in the dictionary at 'text' key
                anchor_data['text'] = text

            # If there is a 'class''s attribute for this anchor and this is equal to 'new'
            # It means that this anchor doesn't point to a wiki page that already exists
            if 'class' in attributes and attributes['class'] == 'new':
                # So take the text of anchor
                anchor_data['a'] = text
            # Else if there is a 'title' between attributes, it means that this anchor points to a existing wiki page
            elif 'title' in attributes:
                anchor_data['a'] = attributes['title']

            # Then append the dictionary to the list of anchor's data
            data.append(anchor_data)

        # At last, returns list of anchor's data
        return data

    def find_td_text(self, cell):
        """
        Method used to carve out attributes and text of a data cell.

        :param cell: (lxml.etree._element) cell which text and attributes you want to extract
        :return data_cell: a dictionary containing text and attributes for this cell
        """
        # Create the dict to contain data
        data_cell = {}

        # Extract attributes for this cell
        attributes = cell.attrib
        # Iterates over attributes
        for attrib in attributes:
            # Add attributes to the data_cell dictionary
            data_cell[attrib] = attributes[attrib]

        # Create cell_text empty string
        cell_text = ""
        # Create a iterator for the cell's text
        text_iterator = cell.itertext()
        # Iterates over text in the iterator
        for text in text_iterator:
            # Add every part of text found
            cell_text += text

        # replace some encode errors
        if type(cell_text) == unicode:
            if u'\xa0' in cell_text:
                cell_text = cell_text.replace(u'\xa0', u' ')

        # Adding the cell text to the cell's data dictionary
        if cell_text:
            data_cell['td'] = cell_text
        # If no text has been found, empties data_cell
        else:
            data_cell = None

        # Returns data_cell dictionary
        return data_cell

    '''
     # Using a WYSIWYG approach, this method is useless
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
        """
        Refine data rows using different methods over table.data rows.

        :param tab: Table object containing data rows we want to refine
        :return: nothing
        """
        try:
            # Delete row we don't want to consider
            self.delete_useless_rows(tab, 'Totale')

            # Expand cells with a colspan > 1
            self.expand_colspan_cells(tab.data)

            # Refine data values
            self.resolve_data_type(tab)

            # Join data cell with corresponding header cell
            self.join_data_and_headers(tab)

            # Encode data
            self.encode_data(tab)
            self.logging.info("Data refined")
        except:
            self.logging.debug("Exception refining data")

    def delete_useless_rows(self, tab, tag):
        """
        Method used to delete useless row containing such tag

        :param tab: Table object containing data you want to refine
        :param tag: (str) contains text you want to search in order to delete specified rows
        :return: nothing
        """
        # Iterates over rows in table.data
        for row in tab.data:
            # Iterates over cells in a row
            for cell in row:
                # Iterates over (element) keys of a cell's dictionary
                for element in cell:
                    # If the text of this element equals tag
                    if 'td' in element and element['td'] == tag:
                        # Remove row selected
                        tab.data.remove(row)

    def expand_colspan_cells(self, rows):
        """
        Method used to replicate cells with a colspan > 1.

        This technique is useful to preserve table's structure when header or data cells are graphically spread over
          more than one column.

        :param rows: a list containing the rows you want to test and refine
        :return: nothing
        """
        try:
            # for every row in rows
            for row in rows:
                # for every cell in that row
                for cell in row:
                    # as cells are dictionaries, iterate over dict keys
                    for element in cell:
                        # set colspan to 0
                        colspan = 0
                        # if 'colspan' is a key for this cell dict
                        if 'colspan' in element:

                            # if the element type is a string, use an integer cast over the value of cell['colspan']
                            if type(element) == str:
                                colspan = int(cell['colspan'])

                            # if the element's type is dictionary set the colspan to int(element['colspan]) as
                            # element is a dictionary itself
                            elif type(element) == dict:
                                colspan = int(element['colspan'])

                            # Finally if colspan found is > 1
                            if colspan > 1:
                                # store row's index of the current cell
                                cell_index = row.index(cell)

                                # restore a single colspan attribute for the current cell before replicate the cell
                                if type(element) == str:
                                    cell['colspan'] = 1
                                elif type(element) == dict:
                                    element['colspan'] = 1

                                # Replicate cell in the correct position (cell_index is used) for 'colspan' times
                                for index in range(0, colspan - 1):
                                    row.insert(cell_index, cell)
        except TypeError:
            print("TypeError trying to expand colspan cells")
        except ValueError:
            print("ValueError trying to expand colspan cells")

    def resolve_data_type(self, tab):
        """
        Refine data cells in order to make it simple to associate them with the respective header cells.


        :param tab: Table object containing data of interest
        :return: nothing
        """
        # Iterates over rows in tab.data
        for row in tab.data:
            # create a temporary row (list)
            temp_row = []
            # Iterates over cells in a row
            for cell in row:
                # create a temporary cell (list) which would contains data for this cell
                temp_cell = []

                # Iterates over dictionaries in cell (remember cell is a list of dictionaries)
                for element in cell:
                    # Create a list that would contains data refined
                    data = []

                    # If the dictionary contains anchor's data
                    if 'a' in element:
                        # use the value of 'a' as data and replace spaces with underscores
                        data = element['a'].replace(' ', '_')

                    # If the dictionary is simple text
                    elif 'td' in element:
                        # simply use the 'td' value as data
                        data = element['td']

                        # test if data is a float number
                        number = self.is_float(data)
                        if number:
                            # so use a float cast of the data
                            data = float(data)

                    # Append data to the temporary cell if data exists, or if it is equal to 0.0
                    if data or data == 0.0:
                        temp_cell.append(data)

                # If there is some values in temp_cell append it to the temporary row
                if temp_cell:
                    temp_row.append(temp_cell)

            # If there are some usable cells in temp_row, append it to table.data_filtered list
            if temp_row:
                tab.data_filtered.append(temp_row)

    def is_float(self, value):
        """
        Test out if a value passed as parameter is a float number
        :param value: a string you want to test
        :return: True | False
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    def join_data_and_headers(self, tab):
        """
        Method used to join a data cell with the corresponding header cell, making possible the mapping process.

        Once this method is used a single dictionary (for every row of data cell) is created containing data as a value
        and the corresponding header as key.
         Eg if data_cell =  ['Franklin_D._Roosevelt', 'New_York_(stato)', 'Franklin D. Roosevelt, NY']
         and the corresponding header is 'Candidati - Presidente'
         the resulting cell is {'Candidati - Presidente': ['Franklin_D._Roosevelt', 'New_York_(stato)',
                                                            'Franklin D. Roosevelt, NY']}

        :param tab: Table object
        :return: nothing
        """
        # Create a temporary row (dictionary which will contain 'header':values)
        temp_row = {}

        if tab.headers:
            # Count number of table's headers
            number_of_headers = len(tab.headers[0])

            # Iterates over tab.data_filtered (remember it is a list of rows)
            for row in tab.data_filtered:
                # create a index
                index = 0
                # Iterates over data cells
                for data in row:

                    try:
                        # getting the header as index cell of the first row
                        header = tab.headers[0][index]['th']
                        # Adding 'header': data to the temporary row
                        temp_row[header] = data
                        # Increase the index
                        index += 1
                        # When index is equal to headers' count, append the dictionary(temp_row) composed to
                        #  table.data_refined
                        if index == number_of_headers:
                            tab.data_refined.append(temp_row)
                            # Remember to reset temp_row and index
                            temp_row = {}
                            index = 0
                    except:
                        self.logging.debug("Exception building rows. \n index = %s" % index)
                        print("Exception building rows.")
                        print ("index: =" + str(index))

                # If temporary row has some data, append it to
                if temp_row:
                    tab.data_refined.append(temp_row)

    def print_table(self, tab):
        print "section ", tab.table_section, " vertical table: ", tab.vertical_table
        for value in self.current_html_table:
            str = ""
            for x in value.itertext():
                str = str + x
            print str.replace("\n", " ")

