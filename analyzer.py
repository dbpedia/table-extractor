import utilities
import sys
import tableParser

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class Analyzer:
    # TODO DOCSTRINGS
    """

    """
    def __init__(self, chapter, topic, filename):
        self.chapter = chapter
        self.topic = topic
        self.filename = filename
        self.analyzed = 0
        # composing a list of resources from the file (filename) passed
        self.res_list = self.open_file()
        self.utils = utilities.Utilities(self.chapter)
        self.lines_to_read = True
        self.last_json_object = None
        # instancing a iterator
        try:
            self.res_iterator = iter(self.res_list)
        except TypeError:
            print "Check the file's existence "
            sys.exit(0)

    def open_file(self):
        """

        :return:
        """
        try:
            file_opened = open(self.filename, 'r')
            return file_opened.readlines()
        except IOError:
            print "IOError opening the file: "+str(self.filename)

    def analyze(self):
        """

        :return:
        """
        while self.lines_to_read:
            try:
                resource = self.res_iterator.next()
                resource = resource.replace("\n", "")
                print("Analyzing "+str(resource))
                self.last_json_object = self.utils.json_object_getter(resource, 'jsonpedia_sections')
                print (str(self.last_json_object))
                # instancing table parser module to analyze the structure of table
                t_parser = tableParser.TableParser()
                t_parser.find_sections(self.last_json_object['result'])
                for section in t_parser.article_sections:
                    t_parser.find_tables(section['section_title'],section)






                # poi direi funzione che va ad associare ad ogni tabella i metadati adeguati
                # poi si passa il tutto a d un "risolutore" che va ad analizzare i dati applicando regole
            except StopIteration:
                self.lines_to_read = False
                print (" End Of File reached")


    def get_filename(self):
        """

        :return:
        """
        return self.filename

