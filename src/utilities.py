import urllib
import json
import time
import datetime
import lxml.html
import lxml.etree as etree
import os
import errno


__author__='papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class Utilities:
    # TODO DOCSTRINGS
    """

    """
    def __init__(self, lang):
        self.lang = lang
        self.jsonpedia_call_format = "?&procs=Extractors,Structure"
        self.jsonpedia_section_format = "?filter=@type:section&procs=Extractors,Structure"
        self.jsonpedia_tables_format = "?filter=@type:table&procs=Extractors,Structure"
        self.call_format_sparql = "&format=application%2Fsparql-results%2Bjson&debug=on"
        self.jsonpedia_base_url = "http://jsonpedia.org/annotate/resource/json/"
        self.jsonpedia_lan = lang + ":"
        self.dbpedia = None
        self.dbpedia_sparql_url = self.dbpedia_selection()
        self.html_format = "https://" + lang + ".wikipedia.org/wiki/"
        self.res_lost_jsonpedia = 0

        self.parser = etree.HTMLParser(encoding='utf-8')

        self.test_dir_existance('../Extractions')

    def test_dir_existance(self, directory):
        current_dir = self.get_current_dir()
        dir_abs_path = self.join_paths(current_dir, directory)

        if not os.path.exists(dir_abs_path):
            print('Extraction folder doesn\'t exist, creating..')
            try:
                os.makedirs(dir_abs_path)
                print('done')
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

    def get_current_dir(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        return cur_dir

    def join_paths(self, path1, path2):
        destination = os.path.join(path1, path2)
        return destination

    def dbpedia_selection(self):
        """

        :return:
        """
        if self.lang != "en":
            self.dbpedia = self.lang + ".dbpedia.org"
        else:
            self.dbpedia = "dbpedia.org"
        return "http://" + self.dbpedia + "/sparql?default-graph-uri=&query="

    def url_composer(self, query, service):
        """
        This function is used to compose a url to call some std services used by the selector,
        such as sparql endpoints or as jsonpedia rest service.
        Before returning the url composed, the method replaces
        :param query: is the string used in some rest calls. For a jsonpedia service is typically the resource name.
        :param service: type of service you request (jsonpedia, dbpedia sparql endpoint..)
        :return url: the url composed
        """
        # TODO conditions for dbpedia/jsonpedia services
        query = urllib.quote_plus(query)
        if service == 'dbpedia':
            url = self.dbpedia_sparql_url + query + self.call_format_sparql

        elif service == 'jsonpedia':
            url = self.jsonpedia_base_url + self.jsonpedia_lan + query + self.jsonpedia_call_format

        elif service == 'jsonpedia_tables':
            url = self.jsonpedia_base_url + self.jsonpedia_lan + query + self.jsonpedia_tables_format

        elif service == 'jsonpedia_sections':
            url = self.jsonpedia_base_url + self.jsonpedia_lan + query + self.jsonpedia_section_format

        elif service == 'html':
            url = self.html_format+query

        else:
            url = "ERROR"
        return url

    def json_answer_getter(self, url_passed):
        """
        json_answer_getter is a method used to call a REST service and to parse the answer in json.
        It returns a json parsed answer if everything is ok
        :param url_passed: type string,is the url to reach for a rest service
        :return json_parsed: the method returns the answer parsed in json
        """
        try:
            call = urllib.urlopen(url_passed)
            answer = call.read()
            json_parsed = json.loads(answer)
            return json_parsed
        except IOError:
            print ("Try, again, some problems due to Internet connection, url: "+url_passed)
            return "Internet problems"
        except ValueError:
            print ("Not a JSON object.")
            return "ValueE"
        except:
            print "Exception with url:" + str(url_passed)
            return "GeneralE"

    def html_answer(self, url_passed):
        try:
            call = urllib.urlopen(url_passed)
            html_document = lxml.html.parse(call, self.parser)
            return html_document
        except IOError:
            print ("Try, again, some problems due to Internet connection, url: " + url_passed)
            return "Internet problems"
        except ValueError:
            print ("Not a JSON object.")
            return "ValueE"
        except:
            print "Exception with url:" + str(url_passed)
            return "GeneralE"

    def json_object_getter(self, resource, struct='jsonpedia'):
        """
        :param resource:
        :param struct:
        :return:
        """
        jsonpedia_url = self.url_composer(resource, struct)
        json_object_state = 'try'
        while json_object_state == 'try':
            try:
                json_answer = self.json_answer_getter(jsonpedia_url)
                if type(json_answer) != str:
                    json_object_state = self.test_json_result(json_answer)
            except:
                print("Error during json_object_getter")
        print(json_object_state)
        return json_answer

    def html_object_getter(self, resource):
        html_url = self.url_composer(resource, 'html')
        answer_ok = 'try'
        while answer_ok == 'try':
            try:
                html_answer = self.html_answer(html_url)
                if type(html_answer) != str:
                    answer_ok = self.test_html_result(html_answer)
            except:
                print("Error during json_object_getter")
        print("Html document well formed..")
        return html_answer

    def test_json_result(self, json_obj):
        if 'message' in json_obj.keys():
            # TODO think about the possibility of write down problems encountered
            message = json_obj['message']
            if message == u'Invalid page metadata.':
                self.res_lost_jsonpedia += 1
                return 'Invalid page metadata'

            elif message == u'Expected DocumentElement found ParameterElement':
                self.res_lost_jsonpedia += 1
                return 'Expected DocumentElement found ParameterElement'

            elif message == u'Expected DocumentElement found ListItem':
                self.res_lost_jsonpedia += 1
                return 'Expected DocumentElement found ListItem'

            elif message == u'Expected DocumentElement found TableCell':
                self.res_lost_jsonpedia += 1
                return 'Expected DocumentElement found TableCell'

            elif len(json_obj) == 3:
                print "Problems related to JSONpedia service :" + str(json_obj) + " - RETRYING"
                return 'try'
        else:
            return 'JSON object well formed'

    def test_html_result(self, html_doc):
        """if 'message' in json_obj.keys():
            # TODO think about the possibility of write down problems encountered
            message = json_obj['message']
            if message == u'Invalid page metadata.':
                self.res_lost_jsonpedia += 1
                return 'Invalid page metadata'

            elif message == u'Expected DocumentElement found ParameterElement':
                self.res_lost_jsonpedia += 1
                return 'Expected DocumentElement found ParameterElement'

            elif message == u'Expected DocumentElement found ListItem':
                self.res_lost_jsonpedia += 1
                return 'Expected DocumentElement found ListItem'

            elif message == u'Expected DocumentElement found TableCell':
                self.res_lost_jsonpedia += 1
                return 'Expected DocumentElement found TableCell'

            elif len(json_obj) == 3:
                print "Problems related to JSONpedia service :" + str(json_obj) + " - RETRYING"
                return 'try'

        else:"""
        return 'JSON object well formed'

    def get_date(self):
        """
        It returns current YEAR_MONTH_DAY as a string
        """
        timestamp = time.time()
        date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d-%H_%M')
        return date




