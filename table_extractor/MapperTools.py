from collections import OrderedDict
import mapping_rules
import settings
import string
import os


class MapperTools:
    """
    MapperTools has to support Mapper in its work. I moved some methods from Utilities class to there to
    understand easily how project work.
    There you will find all functions for reading mapping rules from file, updating them and all checks that are
    needed.

    There is also method to filter rows from table that summarize previous ones. (Like career rows in athlete).
    """
    def __init__(self, utils):
        self.utils = utils
        self.chapter = self.utils.chapter
        self.output = self.utils.output

    # tools to read and updating mapping rules
    def update_mapping_rules(self):
        """
        Method that:
        - read new mapping rules defined by user
        - parse these mapping rules
        - read actual dictionary and update or add all new keys
        - print new dictionary
        :return: updated dictionary
        """
        # read mapping rules wrote by user
        new_mapping_rules = self.read_mapping_rules()
        # check if user has written right properties (that are in dbpedia ontology)
        verified_mapping_rules = self.check_user_input_properties(new_mapping_rules)
        # read mapping rules of pyTableExtractor
        actual_mapping_rules = self.read_actual_mapping_rules()
        # update new mapping rules with old ones
        updated_mapping_rules = self.update_differences_between_dictionaries(actual_mapping_rules,
                                                                             verified_mapping_rules)
        # print out mapping rules obtained previously
        self.print_updated_mapping_rules(updated_mapping_rules)
        return updated_mapping_rules

    def read_mapping_rules(self):
        """
        Read mapping rules defined by user and parse it
        :return: parsed mapping rules
        """
        # Import is there for being sure that the file exists.
        import domain_settings
        new_mapping_rules = OrderedDict()
        if os.path.isfile(settings.PATH_DOMAIN_EXPLORER):
            # search for right dictionary
            for name, val in domain_settings.__dict__.iteritems():
                if settings.SECTION_NAME in name:
                    name_section = name.replace(settings.SECTION_NAME, "")
                    new_mapping_rules[name_section] = OrderedDict()
                    new_mapping_rules[name_section].update(val)
        # parse mapping rules
        parsed_mapping_rules = self.parse_mapping_rules(new_mapping_rules)
        return parsed_mapping_rules

    def parse_mapping_rules(self, new_mapping_rules):
        """
        Parse mapping rules written by user in order to create an ordinary dictionary
        :param new_mapping_rules: mapping rules read previously
        :return: parsed mapping rules
        """
        parsed_mapping_rules = OrderedDict()
        for section_key, section_dict in new_mapping_rules.items():
            for key, value in section_dict.items():
                # i need to delete all punctuation: ontology properties hasn't that type of character
                value = value.translate(None, string.punctuation).replace(" ", "")
                # Change the sectionProperty with the name of the section
                if key == settings.SECTION_NAME_PROPERTY:
                    # split sections by _tte_ character
                    sections = section_key.split(settings.CHARACTER_SEPARATOR)
                    # for each section I have to add it to dictionary
                    for section in sections:
                        # each section will have prefix to distinguish it from header that could have same name
                        parsed_mapping_rules.__setitem__(settings.SECTION_NAME + section.replace("_", " "), value)
                # some tables can report an header that is empty, so i have to delete that option (user's error on
                # writing that table)
                elif key != "":
                    sections = section_key.split(settings.CHARACTER_SEPARATOR)
                    for section in sections:
                        # output organization 1 define strict rule for each header
                        if self.output == "2":
                            parsed_mapping_rules.__setitem__(key, value)
                        else:
                            parsed_mapping_rules.__setitem__(section.replace("_", " ") + "_" + key, value)
        return parsed_mapping_rules

    def read_actual_mapping_rules(self):
        """
        Read actual mapping rules of the chapter selected
        :return: mapping rules already defined
        """
        actual_mapping_rules = OrderedDict()
        # read dictionary that is of the right language
        for name, val in mapping_rules.__dict__.iteritems():
            if self.chapter.upper() in name[-2:]:
                actual_mapping_rules = dict(val)
        return actual_mapping_rules

    def check_user_input_properties(self, new_mapping_rules):
        """
        Check if properties defined by user are defined in dbpedia ontology
        :param new_mapping_rules: mapping rules defined by user in settings file
        :return:
        """
        if settings.CHECK_USER_INPUT_PROPERTY:
            for key in new_mapping_rules:
                # don't check table's row
                query = settings.SPARQL_CHECK_IN_ONTOLOGY[0] + new_mapping_rules[key] + \
                        settings.SPARQL_CHECK_IN_ONTOLOGY[1]
                url = self.utils.url_composer(query, "dbpedia")
                # get response of request
                response = self.utils.json_answer_getter(url)['boolean']
                # if property isn't defined in ontology, i delete it
                if not response:
                    message = "Property: " + new_mapping_rules[key] +\
                           ", doesn't exist in dbpedia ontology. Please add it."
                    print message, "\n"
                    del new_mapping_rules[key]
                    self.utils.logging.warn(message)
        return new_mapping_rules

    def update_differences_between_dictionaries(self, actual_mapping_rules, new_mapping_rules):
        """
        Search for differences between old and new mapping rules
        :param actual_mapping_rules: properties dictionary already defined
        :param new_mapping_rules: properties dictionary defined by user
        :return: updated dictionary with old and new mapping rules
        """
        if new_mapping_rules:
            for key, value in new_mapping_rules.items():
                if value != "":
                    # if user add a new mapping rule
                    actual_mapping_rules.__setitem__(key, value)
                else:
                    # user deleted a property that was filled in domain_settings, so I will empty that
                    # mapping rule.
                    if key in actual_mapping_rules:
                        del actual_mapping_rules[key]
        return actual_mapping_rules

    def print_updated_mapping_rules(self, updated_mapping_rules):
        """
        Print new dictionary with all updated mapping rules
        :param updated_mapping_rules: dictionary to print
        :return: nothing
        """
        data_to_print = ""
        printed_out = 0
        for name, val in mapping_rules.__dict__.iteritems():
            if settings.MAPPING_RULE_PREFIX in name:
                # read dictionaries that aren't modified and print them
                if self.chapter.upper() in name[-2:]:
                    printed_out = 1
                    data_to_print = data_to_print + name + "=" + str(updated_mapping_rules).replace(", ", ", \n") +\
                        "\n\n\n"
                else:
                    # read old dictionary and replace it with new one
                    data_to_print = data_to_print + name + "=" + str(val).replace(", ", ", \n") + "\n\n\n"
        # overwrite mapping_rules.py
        mapping_rules_file = open("mapping_rules.py", "w")
        mapping_rules_file.write(settings.COMMENT_MAPPING_RULES + "\n\n")
        # printed_out == 0 means that the dictionary didn't exists in mapping_rules.py
        if printed_out == 0:
            # Building dictionary in string form for printing out to file
            new_dict = settings.PREFIX_MAPPING_RULE + self.chapter.upper()
            dict_in_str = "={\n"
            for key, value in updated_mapping_rules.items():
                dict_in_str = dict_in_str + "'" + key + "':'" + value + "',\n"
            new_dict = new_dict + dict_in_str + "} \n"
            data_to_print = data_to_print + new_dict
        mapping_rules_file.write(data_to_print)

    # tools useful to create rdf graph

    def is_float(self, value):
        """
        Test out if a value passed as parameter is a float number
        :param value: a string you want to test
        :return: True if value is a float | False otherwise
        """
        try:
            float(value)
            return True
        except TypeError:
            return False
        except ValueError:
            return False

    def is_int(self, value):
        """
        Test out if a value passed as parameter is an integer
        :param value: a string you want to test
        :return: True if the value is an integer | False otherwise
        """
        try:
            int(value)
            return True
        except TypeError:
            return False
        except ValueError:
            return False

    def filter_table_data(self, table_data, table_section):
        """
        This method is used to delete last table's row if it represents sum or mean of previous values.
        It's useful in order to not create triples for this type of information
        :return:
        """
        table_dict = dict()
        i = 0
        for row in table_data:
            summarized = 0
            deleted = False
            for cell in row:
                value = self.extract_value_from_cell(row[cell])
                if self.is_float(value) or self.is_int(value):
                    value = float(value)
                    if cell in table_dict:
                        summed_value = float(table_dict[cell])
                        mean_value = summed_value / i
                        if (value == summed_value or str(value) == str(mean_value)) \
                                and (i > 1 or len(table_data) <= 2):
                            summarized += 1
                        else:
                            table_dict.__setitem__(cell, value + summed_value)
                    else:
                        table_dict.__setitem__(cell, value)
            if summarized >= 2:
                for key in table_data[i]:
                    actual = self.extract_value_from_cell(table_data[i][key])
                    previous = self.extract_value_from_cell(table_data[i - 1][key])
                    char_difference = self.difference_between_strings(actual, previous)
                    if not self.is_float(actual) and not self.is_float(previous) and char_difference >= 7:
                        deleted = True
            if deleted:
                print "Deleted row ", i + 1, " of table ", table_section, " because it looks like as summary row."
                for key in table_data[i]:
                    value = self.extract_value_from_cell(table_data[i][key])
                    if value != "-":
                        self.utils.data_extracted_to_map -= 1
                del table_data[i]
                self.utils.logging.info("Deleted row %d  of table %s"
                                        " because it looks like as summary row.", i + 1, table_section)
                i -= 1
            i += 1
        return table_data

    def difference_between_strings(self, a, b):
        """
        Count how many chars differs these two strings

        :param a: string
        :param b: string
        :return: number of unique chars that differs between two strings
        """
        counter = 0
        # if it's float i need to cast to string
        if type(a) == float:
            a = str(a)
        if type(b) == float:
            b = str(b)
        # get unique chars from string
        unique_chars_a = self.get_unique_chars(a)
        unique_chars_b = self.get_unique_chars(b)
        # count unique chars from first string
        for char in unique_chars_a:
            if char not in unique_chars_b:
                counter += 1

        # count unique chars from second string
        for char in unique_chars_b:
            if char not in unique_chars_a:
                counter += 1
        return counter

    def get_unique_chars(self, work_string):
        """
        Get a list of unique chars that compose a string

        :param work_string: string where to count unique chars
        :return: list of unique chars
        """
        work_string = work_string.replace(" ", "")
        unique_chars = []
        for char in work_string:
            if char not in unique_chars:
                unique_chars.append(char.lower())
        return unique_chars

    def adjust_resource(self, text):
        """
        Remove space from beginning and ending of a string.
        After that I replace other spaces with _ in order to get a resource suitable for uri
        :param text: string to process
        :return: string without blank spaces
        """
        if text.startswith(" "):
            text = text[1:]
        if text.endswith(" "):
            text = text[:-1]
        text = text.replace(" ", "_")
        return text

    def extract_value_from_cell(self, cell):
        """
        Cell can be a link and value or only a value
        :param cell: table's cell
        :return: value of cell
        """
        # take only value's cell and not possible link
        if len(cell) > 1:
            value = cell[-1]
        else:
            value = cell
        if isinstance(value, list):
            result = value[0]
        else:
            result = value
        if isinstance(result, basestring):
            return result
        else:
            return str(result)
