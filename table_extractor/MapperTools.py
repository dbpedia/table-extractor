from collections import OrderedDict
import mapping_rules
import settings
import string
import os


class MapperTools:

    def __init__(self, utils):
        self.utils = utils
        self.chapter = self.utils.chapter
        self.verbose = self.utils.verbose

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
        new_mapping_rules = self.read_mapping_rules()
        verified_mapping_rules = self.check_user_input_properties(new_mapping_rules)
        actual_mapping_rules = self.read_actual_mapping_rules()
        updated_mapping_rules = self.update_differences_between_dictionaries(actual_mapping_rules,
                                                                             verified_mapping_rules)
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
            for name, val in domain_settings.__dict__.iteritems():
                if settings.SECTION_NAME in name:
                    name_section = name.replace(settings.SECTION_NAME, "")
                    new_mapping_rules[name_section] = OrderedDict()
                    new_mapping_rules[name_section].update(val)
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
                    # replace _ with a space.
                    sections = section_key.split(settings.CHARACTER_SEPARATOR)
                    for section in sections:
                        parsed_mapping_rules.__setitem__(section.replace("_", " "), value)
                elif key != "":
                    sections = section_key.split(settings.CHARACTER_SEPARATOR)
                    for section in sections:
                        if self.verbose == "2":
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
                url = self.url_composer(query, "dbpedia")
                response = self.json_answer_getter(url)['boolean']
                if not response:
                    message = "Property: " + new_mapping_rules[key] +\
                           ", doesn't exist in dbpedia ontology. Please add it."
                    print message, "\n"
                    del new_mapping_rules[key]
                    self.logging.warn(message)
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
                if self.chapter.upper() in name[-2:]:
                    printed_out = 1
                    data_to_print = data_to_print + name + "=" + str(updated_mapping_rules).replace(", ", ", \n") + "\n\n\n"
                else:
                    data_to_print = data_to_print + name + "=" + str(val).replace(", ",", \n") + "\n\n\n"
        file = open("mapping_rules.py", "w")
        file.write(settings.COMMENT_MAPPING_RULES + "\n\n")
        # printed_out == 0 means that the dictionary didn't exists in mapping_rules.py
        if printed_out == 0:
            # Building dictionary in string form for printing out to file
            new_dict = settings.PREFIX_MAPPING_RULE + self.chapter.upper()
            dict_in_str = "={\n"
            for key, value in updated_mapping_rules.items():
                dict_in_str = dict_in_str + "'" + key + "':'" + value + "',\n"
            new_dict = new_dict + dict_in_str + "} \n"
            data_to_print = data_to_print + new_dict
        file.write(data_to_print)

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
        counter = 0
        if type(a) == float:
            a = str(a)
        if type(b) == float:
            b = str(b)
        unique_chars_a = self.get_unique_chars(a)
        unique_chars_b = self.get_unique_chars(b)
        for char in unique_chars_a:
            if char not in unique_chars_b:
                counter += 1

        for char in unique_chars_b:
            if char not in unique_chars_a:
                counter += 1
        return counter

    def get_unique_chars(self, string):
        string = string.replace(" ", "")
        unique_chars = []
        for char in string:
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
