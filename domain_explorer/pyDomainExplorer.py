# coding = utf-8

import ExplorerTools
import WriteSettingsFile
from table_extractor import settings
from collections import OrderedDict

# All table's section found
all_sections = OrderedDict()
# All headers found in tables analyzed
all_headers = OrderedDict()
__author__ = "Luca Virgili"

"""
pyDomainExplorer works over domain specified by user in order to get all sections and headers of tables that 
have been found.
All data will be represented in all_sections variable. 
It's a nested dictionary that has this organization: each key of all_sections represents a particular section 
and its related value is a dictionary that contains all section's headers.
Output of this script is a settings file, named "domain_settings", that user has to fill in order to map all fields 
that hasn't a clear property.

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
        analyze_uri_resource_list(uri_resource_list, actual_dictionary)
        # print report of extractor
        explorer_tools.utils.print_report()
        # write settings file
        write_sections_and_headers()
    else:
        print "No resources found. Please check arguments passed to pyDomainExplorer"


def analyze_uri_resource_list(uri_resource_list, actual_dictionary):
    """
    Analyze each resource uri's to get sections and headers of related table.
    :param uri_resource_list: list of all resource's uri
    :param actual_dictionary
    :return:
    """
    actual_resource = 0
    total_resources = len(uri_resource_list)
    for single_uri in uri_resource_list:
        print "Resource: ", single_uri
        actual_resource += 1
        explorer_tools.printProgressBar(actual_resource, total_resources)
        # update number of resources analyzed
        explorer_tools.utils.res_analyzed += 1
        get_resource_sections_and_headers(single_uri, actual_dictionary)


def get_resource_sections_and_headers(res_name, actual_dictionary):
    """
    If there are defined tables, I will analyze each of them.
    First of all I will study section's table, then I will go on headers' table.
    :param res_name: resource name that has to be analyzed
    :param actual_dictionary
    :return:
    """
    # Get all tables
    all_tables = explorer_tools.html_table_parser(res_name)
    # For each table defined
    for table in all_tables:

        # I won't get tables with only one row --> It can be an error during table's reading
        if table.n_rows > 1:
            check_if_section_is_present(table.table_section, table.headers_refined, res_name, actual_dictionary)


def check_if_section_is_present(string_to_check, headers_refined, res_name, actual_dictionary):
    """
    Check if section is already presents in all_sections dictionary.
    I do this in order to create a dictionary that group similar section.
    :param string_to_check: section name to check
    :param headers_refined: all headers of this sections (JSON object that contains properties like 'colspan', etc..)
    :param res_name: resource name that has to be analyzed
    :param actual_dictionary
    :return:
    """
    section_name = check_if_similar_section_is_present(string_to_check, res_name)
    # Check if this section was already created, if not it will create another dictionary
    check_if_headers_not_present_then_add(headers_refined, section_name, actual_dictionary)


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
            all_sections[new_key].__setitem__("exampleWiki", res_name)
    else:
        new_key = equal_key
    return new_key


def check_if_headers_not_present_then_add(headers, section_name, actual_dictionary):
    """
    Check if headers passed are already defined in the section that you are analyzing.

    :param headers: all table's headers
    :param section_name: section name to analyze
    :param actual_dictionary
    :return:
    """
    #
    for row in headers:
        header = row['th']
        # character "'" will produce a wrong output file
        header = header.replace("'", "")
        check_if_header_already_exists(header, section_name, actual_dictionary)


def check_if_header_already_exists(header, section_name, actual_dictionary):
    """
    Check if section contains this header.
    except KeyError will caught exception given by lack of a key (in this case 'header' is the key)
    :param header: single table header
    :param section_name: section name to analyze
    :param actual_dictionary
    :return:
    """
    if header not in all_sections[section_name]:
        # check if this header is already defined in actual_dictionary
        if header in actual_dictionary:
            # if it's not related to section
            header_property = actual_dictionary[header]
        elif (section_name + "_" + header) in actual_dictionary:
            # if it's associated to section (depend on verbose value)
            header_property = actual_dictionary[section_name + "_" + header]
        else:
            # check if it's already defined a property for this header
            header_property = check_if_property_exists(header)
        # delete headers that have only one character
        if len(header) > 1:
            all_sections[section_name].__setitem__(header, header_property)
            # verify if in all_headers is already defined
            if header not in all_headers:
                all_headers.__setitem__(header, header_property)
                explorer_tools.print_log_msg("info", "New header found: " + header)


def check_if_property_exists(header):
    """
    Query dbpedia endpoint in order to search if a particular property is defined.
    This method search if in dbpedia ontology there is a property that has a label (in chapter language)
    that has same name of header's table.
    This will be useful for user so that filling settings file will be easier.
    :param header: property to check
    :return:
    """
    property_to_check = ""
    # check if it's already defined
    if header in all_headers:
        property_to_check = all_headers[header]
    else:
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


def write_sections_and_headers():
    """
    Write sections and headers found. I will use WriteSettingsFile to create output file.
    :return:
    """
    WriteSettingsFile.WriteSettingsFile(all_sections, all_headers,
                                        explorer_tools)


if __name__ == "__main__":
    explorer_tools = ExplorerTools.ExplorerTools()
    start_exploration()
