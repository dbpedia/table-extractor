import settings_domain_explorer as settings
from collections import OrderedDict
import sys
import rdflib
from table_extractor import Utilities, HtmlTableParser, mapping_rules

# All table's section found
all_sections = OrderedDict()
# All headers table found
all_headers = OrderedDict()

__author__ = "Luca Virgili"

"""
pyDomainExplorer is used for searching over the defined domain all headers and section table.
Headers and sections are organized in two dictionaries.
The script query dbpedia for asking if there's a property named like header.
"""

"""
Start the domain exploration.
"""


def start_exploration(chapter, topic):
    # Prepare query SPARQL
    actual_dictionary = read_actual_dictionary(chapter)
    utils = Utilities.Utilities(chapter, topic)
    uri_resource_list = get_uri_resources(utils, topic)
    if uri_resource_list:
        analyze_uri_resource_list(uri_resource_list, utils, chapter, topic, actual_dictionary)
        write_sections_and_headers(chapter, topic)


"""
Write file domain_settings.py that contains all headers and sections found
"""


def write_sections_and_headers(chapter,topic):
    domain_explored_file = file(settings.FILE_PATH_DOMAIN_EXPLORED, 'w')
    domain_explored_file.write("DOMAIN_EXPLORED='" + topic + "' \n")
    domain_explored_file.write("CHAPTER='" + chapter + "' \n\n")
    domain_explored_file.write("SECTIONS={ \n")
    print_dictionary_on_file(domain_explored_file, all_sections)
    domain_explored_file.write("} \n\n")
    domain_explored_file.write("HEADERS={ \n")
    print_dictionary_on_file(domain_explored_file, all_headers)
    domain_explored_file.write("}")
    domain_explored_file.close()

"""
Write dictionary in a file
"""


def print_dictionary_on_file(file, dict):
    for key, value in dict.items():
        file.write("'" + key +"':'" + value +"'" + ", \n")

"""
For each resource found in the domain, I get section and headers
"""


def analyze_uri_resource_list(uri_resource_list, utils, chapter, topic, actual_dictionary):
    graph = rdflib.Graph()
    for single_uri in uri_resource_list:
        res_name = get_resource_name_from_uri(single_uri, utils)
        get_resource_sections_and_headers(chapter, topic, graph, res_name, utils, actual_dictionary)
        print res_name

"""
Analyze tables and get headers and sections
"""


def get_resource_sections_and_headers(chapter, topic, graph, res_name, utils, actual_dictionary):
    html_doc_tree = utils.html_object_getter(res_name)
    if html_doc_tree:
        html_parser = HtmlTableParser.HtmlTableParser(html_doc_tree, chapter, graph,
                                                      topic, res_name, utils)
        if html_parser.tables:
            html_parser.analyze_tables()
            for table in html_parser.all_tables:
                if table.n_rows > 1:
                    check_if_section_not_present_then_add(table.table_section, actual_dictionary)
                    check_if_headers_not_present_then_add(table.headers_refined, actual_dictionary, utils)

"""
Check if section is present in the dictionary of pyTableExtractor
"""


def check_if_section_not_present_then_add(string_to_check, actual_dictionary):
    try:
        key = (actual_dictionary[string_to_check])
    except KeyError:
        check_if_similar_section(string_to_check)

"""
Check if there is a property in ontology that has the same header's name.
"""


def check_if_headers_not_present_then_add(headers, actual_dictionary, utils):
    for row in headers:
        try:
            key = (actual_dictionary[row['th']])
        except KeyError:
            if len(row['th']) > 1:
                check_if_property_exists(row['th'], utils)


"""
Query dbpedia for searching a particular property.
"""


def check_if_property_exists(header, utils):
    try:
        key = all_headers[header]
    except KeyError:
        query = settings.SPARQL_CHECK_PROPERTY[0] + header.lower() + settings.SPARQL_CHECK_PROPERTY[1]
        utils.chapter = "en"
        utils.dbpedia_sparql_url = utils.dbpedia_selection()
        url = utils.url_composer(query, "dbpedia")
        answer = utils.json_answer_getter(url)
        value = ""
        if not isinstance(answer, basestring):
            for row in answer["results"]["bindings"]:
                value = "dbo:" + header.lower()
        all_headers.__setitem__(header, value)


"""
Check if there are headers that are similar. (For example 'College' and 'College statistics' will be join in one unique
header to map)
"""


def check_if_similar_section(string_to_check):
    keys = list(all_sections.keys())
    similar_key = [key for key in keys if string_to_check.lower() in key.lower() or key.lower() in string_to_check.lower()]
    if similar_key:
        equal_key = [key for key in similar_key[0].split(">") if string_to_check.lower() == key.lower()]
        if not equal_key:
            new_key = similar_key[0] + ">" + string_to_check
            del all_sections[similar_key[0]]
            all_sections.__setitem__(new_key, "")
    else:
        all_sections.__setitem__(string_to_check, "")

"""
Get uri of all domain's resources.
"""


def get_uri_resources(utils, topic):
    query = settings.SPARQL_GET_RESOURCES[0] + topic + settings.SPARQL_GET_RESOURCES[1]
    # Metto in inglese per rifarmi all'ontology e scaricare le risorse
    utils.chapter = "en"
    utils.dbpedia_sparql_url = utils.dbpedia_selection()
    url = utils.url_composer(query, "dbpedia")
    answer = utils.json_answer_getter(url)
    uri_resource_list = []

    # Compose resource list with all the class uri
    for value in answer["results"]["bindings"]:
        uri_resource_list.append(value["s"]["value"])
    return uri_resource_list

"""
Check args passed by user
"""


def check_args_passed(list):
    result = 0
    if len(list) < 4:
        result = 1
    return result

"""
Get the resource name from uri.
"""


def get_resource_name_from_uri(uri, utils):
    res_name = uri.replace("http://" + utils.dbpedia + "/resource/", "")
    res_name = res_name.encode('utf-8')
    return res_name

"""
Read the dictionary of pyTableExtractor. The script will update this dictionary with information given by user
"""


def read_actual_dictionary(chapter):
    dictionary = OrderedDict()
    dictionary_name = settings.PREFIX_MAPPING_RULE + chapter.upper()
    for name, val in mapping_rules.__dict__.iteritems():  # iterate through every module's attributes
        if name == dictionary_name:
            dictionary = val
    return dictionary

if __name__ == "__main__":
    arg = sys.argv
    check = check_args_passed(sys.argv)
    if check == 0:
        start_exploration(arg[2], arg[4])
    else:
        print "Insert correct value for argv"
