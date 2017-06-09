import settings_domain_explorer as settings
from collections import OrderedDict
import sys
import rdflib
from table_extractor import Utilities, HtmlTableParser, mapping_rules

# All table's section found
all_sections = OrderedDict()
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


def write_sections_and_headers(chapter, topic):
    domain_explored_file = file(settings.FILE_PATH_DOMAIN_EXPLORED, 'w')
    domain_explored_file.write(settings.DOMAIN_TITLE + "='" + topic + "' \n")
    domain_explored_file.write(settings.CHAPTER + "='" + chapter + "' \n\n")
    for key, dict in all_sections.items():
        domain_explored_file.write(settings.SECTION_NAME + key.replace(" ", "_").replace("-","_") + "={\n")
        print_dictionary_on_file(domain_explored_file, dict)
        domain_explored_file.write("} \n\n")
    domain_explored_file.close()

"""
Write dictionary in a file
"""


def print_dictionary_on_file(file, dict):
    for key, value in dict.items():
        file.write("'" + key + "':'" + value + "'" + ", \n")

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
                    check_if_section_is_present(table.table_section, actual_dictionary, utils, table.headers_refined)

"""
Check if section is present in the dictionary of pyTableExtractor
"""


def check_if_section_is_present(string_to_check, actual_dictionary, utils, headers_refined):
    section_name = string_to_check
    try:
        # Section already in mapping_rules.py, but i have to update all_sections
        key = (actual_dictionary[string_to_check])
        try:
            all_sections[string_to_check]
        except:
            all_sections[string_to_check] = OrderedDict()
            all_sections[string_to_check].__setitem__(settings.SECTION_NAME_PROPERTY,"")
    except KeyError:
        section_name = check_if_similar_section_is_present(string_to_check, utils)
    # Check if this section was already created, if not it will create another dictionary
    check_if_headers_not_present_then_add(headers_refined, actual_dictionary, utils, section_name)

"""
Check if there is a property in ontology that has the same header's name.
"""


def check_if_headers_not_present_then_add(headers, actual_dictionary, utils, section_name):
    for row in headers:
        header = row['th']
        header = header.replace("'", ":")
        try:
            actual_dictionary[header]
        except KeyError:
            check_if_header_already_exists(header, utils, section_name)


"""
Query dbpedia for searching a particular property.
"""


def check_if_header_already_exists(header, utils,section_name):
    try:
        all_sections[section_name][header]
    except KeyError:
        header_property = check_if_propery_exists(utils, header)
        all_sections[section_name].__setitem__(header, header_property)
        all_headers.__setitem__(header, header_property)


def check_if_propery_exists(utils, header):
    property = ""
    try:
        property = all_headers[header]
    except KeyError:
        answer = make_sparql_dbpedia("check_property", utils, header)
        if not isinstance(answer, basestring):
            for row in answer["results"]["bindings"]:
                property = "dbo:" + header.lower()
    return property

"""
Function for making a dbpedia sparql query
"""


def make_sparql_dbpedia(service,utils, data):
    utils.chapter = "en"
    utils.dbpedia_sparql_url = utils.dbpedia_selection()
    query = ""
    if service == "check_property":
        query = settings.SPARQL_CHECK_PROPERTY[0] + data.lower() + settings.SPARQL_CHECK_PROPERTY[1]
    elif service == "resources":
        query = settings.SPARQL_GET_RESOURCES[0] + data + settings.SPARQL_GET_RESOURCES[1]
    url = utils.url_composer(query, "dbpedia")
    answer = utils.json_answer_getter(url)
    return answer

"""
Check if there are headers that are similar. (For example 'College' and 'College statistics' will be join in one unique
header to map)
"""


def check_if_similar_section_is_present(string_to_check, utils):
    keys = list(all_sections.keys())
    new_key = string_to_check
    similar_key = [key for key in keys if string_to_check.lower() in key.lower() or key.lower() in string_to_check.lower()]
    equal_key = search_equal_key(keys, string_to_check)
    if not equal_key:
        if similar_key:
            new_key = similar_key[0] + settings.CHARACTER_SEPARATOR + string_to_check
            app_dict = dict(all_sections[similar_key[0]])
            del all_sections[similar_key[0]]
            all_sections[new_key] = OrderedDict()
            all_sections[new_key].__setitem__(settings.SECTION_NAME_PROPERTY, "")
            all_sections[new_key].update(app_dict)
        else:
            all_sections[new_key] = OrderedDict()
            all_sections[new_key].__setitem__(settings.SECTION_NAME_PROPERTY, "")
    else:
        new_key = equal_key

    print "Tocca: ", string_to_check, " Simili: ", similar_key, " Uguali: ",equal_key," nuova: ", new_key, "tutte le chiavi: ", keys
    return new_key

"""
Check if an array string contains a particular word
"""


def search_equal_key(array_string, string_to_check):
    result = ""
    for string in array_string:
        keys = string.split(settings.CHARACTER_SEPARATOR)
        found = 0
        for key in keys:
            if key.lower() == string_to_check.lower():
                found = 1
        if found == 1:
            result = string
    return result

"""
Get uri of all domain's resources.
"""


def get_uri_resources(utils, topic):
    # Metto in inglese per rifarmi all'ontology e scaricare le risorse
    answer = make_sparql_dbpedia("resources", utils, topic)
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
            dictionary = dict(val)
    return dictionary

if __name__ == "__main__":
    arg = sys.argv
    check = check_args_passed(sys.argv)
    if check == 0:
        start_exploration(arg[2], arg[4])
    else:
        print "Insert correct value for argv"
