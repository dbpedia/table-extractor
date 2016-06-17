

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class TableParser:
    """
    This class is used to analyze a json object (obtained from jsonpedia) in order to get data from tables.
    First it find sections and extract them. Therefore it extracts tables inside those sections.
    """
    def __init__(self):

        self.article_sections = []
        self.section_numbers = 0
        self.table_list = []

    def find_sections(self, json_object=None):
        """
        It manipulates a json object (already deserialized in a python object).
        If it find dictionaries containing a section it extract and append them to a specific list.
        :param json_object:

        :return:
        """
        if json_object == 0:
            return
        else:
            try:
                if '@type' in json_object and json_object['@type'] == 'section':
                    if 'content' in json_object:
                        json_object['content']['section_title'] = json_object['title']
                        self.article_sections.append(json_object['content'])
                        self.section_numbers += 1
                        print("Section Found")
                        return
                elif type(json_object) == dict:
                    for value in json_object.values():
                        self.find_sections(value)
                elif type(json_object) == list:
                    for value in json_object:
                        self.find_sections(value)
            except:
                print("WRONG use with: " + str(json_object))

    def find_tables(self, sec_title, json_object=None):
        """
        Once sections are found, this function find out tables and associate them with the title of section.
        :param json_object:
        :param sec_title:
        :return:
        """
        if json_object == 0:
            return
        else:
            try:
                if '@type' in json_object and json_object['@type'] == 'table':
                    if 'content' in json_object:
                        json_object['content']['section_title'] = sec_title
                        self.table_list.append(json_object['content'])
                        # add a counter of tables
                        print("Table Found")
                        return
                elif type(json_object) == dict:
                    for value in json_object.values():
                        self.find_tables(sec_title, value)
                elif type(json_object) == list:
                    for value in json_object:
                        self.find_tables(sec_title, value)
            except:
                print("WRONG use with: " + str(json_object))