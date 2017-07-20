# coding = utf-8

import ExplorerTools
import WriteSettingsFile
from table_extractor import settings
from collections import OrderedDict

# All table's section found
all_sections = OrderedDict()
# All headers found in tables analyzed
all_headers = OrderedDict()
# Array that will contains resources name where it was found a particular section. It will be useful for user.
example_wikipedia_pages = []

__author__ = "Luca Virgili"

"""
pyDomainExplorer works over domain specified by user in order to get all sections and headers of tables that 
have been found.
All data will be represented in all_sections variable. 
It's a nested dictionary that has this organization: each key of all_sections represents a particular section 
and its related value is a dictionary that contains all section's headers.
Output of this script is a settings file, named "domain_settings", that user has to fill in order to map all fields that hasn't a clear
property.

"""


def start_exploration():
    """
    Start domain exploration.
    It will take resources list and give in output a settings file organized
    like a dictionary ---> "Header name":"Ontology property associated"
    :return:
    """

    # Read pyTableExtractor dictionary
    actual_dictionary = explorer_tools.read_actual_dictionary()
    # Read uri resources
    uri_resource_list = explorer_tools.get_uri_resources()
    # If resources are found
    if uri_resource_list:
        # Analyze uri list
        analyze_uri_resource_list(uri_resource_list)
        # Add properties defined in pyTableExtractor dictionary
        insert_properties_old_dictionary(actual_dictionary)
        # write settings file
        write_sections_and_headers()
    else:
        print "No resources found. Please check arguments passed to pyDomainExplorer"


def analyze_uri_resource_list(uri_resource_list):
    """
    Analyze each resource uri's to get sections and headers of related table.
    :param uri_resource_list: list of all resource's uri
    :return:
    """
    for single_uri in uri_resource_list:
        print "Resource: ", single_uri
        get_resource_sections_and_headers(single_uri)


def get_resource_sections_and_headers(res_name):
    """
    If there are defined tables, I will analyze each of them.
    First of all I will study section's table, then I will go on headers' table.
    :param res_name: resource name that has to be analyzed
    :return:
    """
    # Get all tables
    all_tables = explorer_tools.html_table_parser(res_name)
    # For each table defined
    for table in all_tables:
        # I won't get tables with only one row --> It can be an error during table's reading
        if table.n_rows > 1:
            check_if_section_is_present(table.table_section, table.headers_refined, res_name)


def check_if_section_is_present(string_to_check, headers_refined, res_name):
    """
    Check if section is already presents in all_sections dictionary.
    I do this in order to create a dictionary that group similar section.
    :param string_to_check: section name to check
    :param headers_refined: all headers of this sections (JSON object that contains properties like 'colspan', etc..)
    :param res_name: resource name that has to be analyzed
    :return:
    """
    section_name = check_if_similar_section_is_present(string_to_check, res_name)
    # Check if this section was already created, if not it will create another dictionary
    check_if_headers_not_present_then_add(headers_refined, section_name)


def check_if_similar_section_is_present(string_to_check, res_name):
    """
    Check if there are sections that are similar.
    (For example 'College' and 'College statistics' will be joint in one unique section to map)
    :param string_to_check: section name to check
    :param res_name: resource name that has to be analyzed
    :return: section name that can be:
                - already defined in all_sections dictionary.
                - same as before.
                - joint with others sections that has similar name.
    Note:
    Each section will be separated by a unique group of characters, defined in settings.py file. (now is _tte_)
    """
    # Get all sections
    keys = list(all_sections.keys())
    new_key = string_to_check
    # similar key
    similar_key = [key for key in keys if string_to_check.lower() in key.lower() or key.lower()
                   in string_to_check.lower()]
    # key that is equal to that passed
    equal_key = search_equal_key(keys, string_to_check)
    # if there isn't an equal key, I have to search on similar key
    if not equal_key:
        # if there is a similar key I have to create another key that contains current key.
        # I have also to delete previous key value in favour of the new key.
        if similar_key:
            new_key = similar_key[0] + settings.CHARACTER_SEPARATOR + string_to_check
            app_dict = dict(all_sections[similar_key[0]])
            del all_sections[similar_key[0]]
            all_sections[new_key] = OrderedDict()
            all_sections[new_key].__setitem__(settings.SECTION_NAME_PROPERTY, "")
            all_sections[new_key].update(app_dict)
        # If there isn't similar key, I simply create a new one in all_sections dictionary.
        else:
            all_sections[new_key] = OrderedDict()
            all_sections[new_key].__setitem__(settings.SECTION_NAME_PROPERTY, "")
            example_wikipedia_pages.append(res_name + settings.CHARACTER_SEPARATOR + new_key)
    else:
        new_key = equal_key
    return new_key


def check_if_headers_not_present_then_add(headers, section_name):
    """
    Check if headers passed are already defined in the section that you are analyzing.

    :param headers: all table's headers
    :param section_name: section name to analyze
    :return:
    """
    #
    for row in headers:
        header = row['th']
        if len(header) > 1:
            # character "'" will produce a wrong output file
            header = header.replace("'", "")
            check_if_header_already_exists(header, section_name)


def check_if_header_already_exists(header, section_name):
    """
    Check if section contains this header.
    except KeyError will caught exception given by lack of a key (in this case 'header' is the key)
    :param header: single table header
    :param section_name: section name to analyze
    :return:
    """
    try:
        all_sections[section_name][header]
    except KeyError:
        # check if it's already defined a property for this header
        header_property = check_if_property_exists(header)
        # delete headers that have only one character
        if len(header) > 1:
            all_sections[section_name].__setitem__(header, header_property)
            # verify if in all_headers is already defined
            try:
                all_headers[header]
            except KeyError:
                all_headers.__setitem__(header, header_property)
                explorer_tools.print_log_msg("info", "New header found: " + header)


def check_if_property_exists(header):
    """
    Query dbpedia endpoint in order to search if a particular property is defined.
    This method search if in dbpedia ontology there is a property that has a label (in chapter language)
    that has same name of header's table.
    This will be useful for user so that filling settings file will be easier.
    :param header:
    :return:
    """
    property_to_check = ""
    # check if it's already defined
    try:
        property_to_check = all_headers[header]
    except KeyError:
        answer = explorer_tools.make_sparql_dbpedia("check_property", header)
        # if answer contains something useful
        if not isinstance(answer, str):
            property_found = 0
            for row in answer["results"]["bindings"]:
                # sparql results can be wikidata or dbpedia uri, i have to filter to catch only dbpedia ontology uri
                for property_type in settings.ONTOLOGY_TYPE:
                    if property_type in row["s"]["value"] and property_found == 0:
                        property_to_check = explorer_tools.get_ontology_name_from_uri(row["s"]["value"])
                        property_found = 1
    return property_to_check


def search_equal_key(array_string, string_to_check):
    """
    Method to search over a string list in order to check if a particular string is equal to
    an element of this list.

    :param array_string: string list
    :param string_to_check:  string to check if there is an equal in string list
    :return: result can be:
                - empty -> there isn't an equal key.
                - equal key found.
    """
    result = ""
    for string in array_string:
        keys = string.split(settings.CHARACTER_SEPARATOR)
        for key in keys:
            if key.lower() == string_to_check.lower():
                result = string
    return result


def insert_properties_old_dictionary(actual_dictionary):
    """
    Insert in all_sections dictionary all properties defined in pyTableExtractor dictionary, in order to
    print in settings file headers that are already defined.

    :param actual_dictionary: pyTableExtractor dictionary (mapping_rules.py)
    :return:
    """
    # loop on both dictionary
    for actual_key in actual_dictionary:
        for section_key in all_sections:
            # if it's equal I have found a section
            if actual_key == section_key:
                all_sections[section_key].__setitem__(settings.SECTION_NAME_PROPERTY, actual_dictionary[actual_key])
            else:
                # otherwise I have to analyze each header of section
                for headers_key in all_sections[section_key]:
                    # key are related to section
                    if actual_key == section_key + "_" + headers_key:
                        all_sections[section_key].__setitem__(headers_key, actual_dictionary[actual_key])
                    # it can be even defined "in" actual key, in order to facilitate user to compile settings file
                    elif headers_key in actual_key and all_sections[section_key][headers_key] == "":
                        all_sections[section_key].__setitem__(headers_key, actual_dictionary[actual_key])


def write_sections_and_headers():
    """
    Write sections and headers found. I will use WriteSettingsFile to create output file.
    :return:
    """
    WriteSettingsFile.WriteSettingsFile(all_sections, all_headers, example_wikipedia_pages,
                                        explorer_tools)


if __name__ == "__main__":
    explorer_tools = ExplorerTools.ExplorerTools()
    start_exploration()
