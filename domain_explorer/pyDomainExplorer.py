# coding = utf-8

import sys
import rdflib
import ExplorerTools
from table_extractor import settings
from collections import OrderedDict

# All table's section found
all_sections = OrderedDict()
all_headers = OrderedDict()
example_wikipedia_pages = []
__author__ = "Luca Virgili"

"""
pyDomainExplorer is used for searching over the defined domain all headers and section table.
Headers and sections are organized in two dictionaries.
The script query dbpedia for asking if there's a property named like header.
"""

"""
Start the domain exploration. It will take resources list and give in output a settings file organized like
a dictionary ---> "Header name":"Property associated"
"""


def start_exploration(chapter, topic, verbose):
    # Prepare query SPARQL
    actual_dictionary = explorer_tools.read_actual_dictionary()
    uri_resource_list = explorer_tools.get_uri_resources()
    if uri_resource_list:
        analyze_uri_resource_list(uri_resource_list, chapter, topic)
        insert_propertiers_old_dictionary(actual_dictionary)
        write_sections_and_headers(chapter, topic, verbose)


"""
Write file domain_settings.py that contains all headers and sections found
:param chapter
:param topic
:param verbose
"""


def write_sections_and_headers(chapter, topic, verbose):
    domain_explored_file = file(settings.FILE_PATH_DOMAIN_EXPLORED, 'w')
    domain_explored_file.write(settings.CODING_DOMAIN + "\n")
    domain_explored_file.write(settings.DOMAIN_TITLE + "='" + topic + "' \n")
    domain_explored_file.write(settings.CHAPTER + "='" + chapter + "' \n")
    domain_explored_file.write(settings.RESEARCH_TYPE + "='" + explorer_tools.research_type + "' \n")
    domain_explored_file.write(settings.RESOURCE_FILE + "='" + explorer_tools.get_res_list_file() + "' \n\n")
    domain_explored_file.write(settings.MAIN_PROPERTY + "='" + "' \n\n")
    for key, dict in all_sections.items():
        wikipedia_example = explorer_tools.replace_accents(get_example_wikipedia_pages(key))
        domain_explored_file.write(settings.COMMENT_FOR_EXAMPLE_PAGE + wikipedia_example + "\n")
        key = explorer_tools.replace_accents(key.replace(" ", "_").replace("-", "_"))
        domain_explored_file.write(settings.SECTION_NAME + key + "={\n")
        explorer_tools.print_dictionary_on_file(domain_explored_file, dict, verbose, all_headers)
        domain_explored_file.write("} \n\n")
    domain_explored_file.close()


def get_example_wikipedia_pages(section):
    # each element in example_wikipedia_pages --> [0] page name where there is section name    [1]section name
    for element in example_wikipedia_pages:
        section_page = element.split(settings.CHARACTER_SEPARATOR)
        if section_page[1] in section:
            return section_page[0]

"""
For each resource found in the domain, I get section and headers
"""


def analyze_uri_resource_list(uri_resource_list, chapter, topic):
    graph = rdflib.Graph()
    for single_uri in uri_resource_list:
        res_name = explorer_tools.get_resource_name_from_uri(single_uri)
        get_resource_sections_and_headers(chapter, topic, graph, res_name)
        print res_name

"""
Analyze tables and get headers and sections
"""


def get_resource_sections_and_headers(chapter, topic, graph, res_name):
    html_doc_tree = explorer_tools.html_object_getter(res_name)
    if html_doc_tree:
        html_parser = explorer_tools.html_table_parser(html_doc_tree, chapter, graph, topic, res_name)

        if html_parser.tables:
            html_parser.analyze_tables()
            for table in html_parser.all_tables:
                if table.n_rows > 1:
                    check_if_section_is_present(table.table_section, table.headers_refined, res_name)

"""
Check if section is present in the dictionary of pyTableExtractor
"""


def check_if_section_is_present(string_to_check, headers_refined, res_name):
    section_name = check_if_similar_section_is_present(string_to_check, res_name)
    # Check if this section was already created, if not it will create another dictionary
    check_if_headers_not_present_then_add(headers_refined, section_name)

"""
Check if there is a property in ontology that has the same header's name.
"""


def check_if_headers_not_present_then_add(headers, section_name):
    for row in headers:
        header = row['th']
        header = header.replace("'", ":")
        check_if_header_already_exists(header, section_name)


"""
Check if header has already been read.
"""


def check_if_header_already_exists(header, section_name):
    try:
        all_sections[section_name][header]
    except KeyError:
        header_property = check_if_property_exists(header)
        # delete headers that have only one character
        if len(header) > 1:
            all_sections[section_name].__setitem__(header, header_property)
            all_headers.__setitem__(header, header_property)

"""
Query dbpedia for searching a particular property.
"""


def check_if_property_exists(header):
    property = ""
    try:
        property = all_headers[header]
    except KeyError:
        answer = explorer_tools.make_sparql_dbpedia("check_property", header)
        if not isinstance(answer, basestring):
            property_found = 0
            for row in answer["results"]["bindings"]:
                # sparql results can be wikidata or dbpedia uri, i have to filter to catch only dbpedia ontology uri
                if "ontology" in row["s"]["value"] and property_found == 0:
                    # i can't put a resource that can be a disambiguation or property --> I need ontology elements
                    if not "disambiguation" in row["s"]["value"]:
                        property = explorer_tools.get_ontology_name_from_uri(row["s"]["value"])
                        property_found = 1
    return property


"""
Check if there are headers that are similar. (For example 'College' and 'College statistics' will be join in one unique
header to map)
"""


def check_if_similar_section_is_present(string_to_check, res_name):
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
            example_wikipedia_pages.append(res_name + settings.CHARACTER_SEPARATOR + new_key)
    else:
        new_key = equal_key
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
When a I found a new key that's not present in the old dictionary, I will add it.
"""


def insert_propertiers_old_dictionary(actual_dictionary):
    for actual_key in actual_dictionary:
        for section_key in all_sections:
            if actual_key == section_key:
                all_sections[section_key].__setitem__(settings.SECTION_NAME_PROPERTY, actual_dictionary[actual_key])
            else:
                for headers_key in all_sections[section_key]:
                    if actual_key == headers_key:
                        all_sections[section_key].__setitem__(headers_key, actual_dictionary[actual_key])

if __name__ == "__main__":
    arg = sys.argv
    explorer_tools = ExplorerTools.ExplorerTools()
    start_exploration(explorer_tools.chapter, explorer_tools.topic, explorer_tools.verbose)
