import sys
__author__='papalinis - Simone Papalini - papalini.simone.an@gmail.com'




class ParamTester:
    """
    ParamTester is a class used to test and set some main variables, usually received as main script arguments.
    NOTE: an object of this class has to be created passing the system arguments vector
    Once created, a paramTester tests if there are too many arguments passed to the script.
    Therefore it tests, and set, each parameter.
    Two functions are used to retrieve the values of parameters from an outer scope
    """
    def __init__(self, argv):
        """
        Initialization of the tester. It has to set a local variable containing the arguments vector.
        Then it launches itself __param_test(self,argv) that automatically test the number of parameters passed.
        Two local variables (lang and where) are set testing corresponding arg vector's parameters.
        :param argv: it is arguments' vector passed to the script, typically is sys.argv
        """
        self.args = argv
        self.__param_test(self.args)
        self.lang = self.__lang_test_and_set(self.args)
        self.where = self.__where_test_and_set(self.args)

    def __param_test(self, argv):
        """
        __param_test(self,argv) is a function used to test if the number of arguments passed to the script is correct.
        It firstly tests if there are more than 3 arguments. If so it prints out a warning and exits programmatically.
        Then if there are less than 2 arguments passed, a warning is printed just to remind the user, he usually has to
        specify 2 parameters (language and where_clause).
        Usually none has to access this function outside the class itself.
        Raising a SystemExit exception prevents the script to go further without a clear target.
        :param argv: arguments'vector
        :return: nothing
        """
        try:
            if len(argv) > 3:
                print("WARNING -- wrong number of parameters -- it accepts only 2 parameters, usage example:\
                    it  \"?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f)\"")
                sys.exit(0)
            if len(argv) < 3:
                print("WARNING -- you are using the script with minus than 2 parameters,\
                        make sure that the first is a language encode (eg. en or it or fr..)\
                         and that the second one is a where clause \
                        usage example : it \"?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f)\"")
        except SystemExit:
            exit()
        except:
            print "Unusual Error"

    def __lang_test_and_set(self, argv):
        """
        __lang_test_and_set(self, argv) is a function used to test the correctness of language parameter and
        return it to the caller, in order to set a local variable.
        If problems are found choosing the language, a default value is used.
        In this case, the function pointed it out to the user printing a WARNING.
        DEFAULT VALUE "en"
        :param argv: arguments'vector
        :return: it returns the parameter, if correct, or the default value "en"
        """
        try:
            lang = argv[1]
            if len(lang) == 2:
                return lang
            else:
                return "en"
        except:
            print("WARNING -- The first argument should be a language code, as en or it, default en")
            return "en"

    def __where_test_and_set(self, argv):
        """
            __where_test_and_set(self, argv) is a function used to test the correctness of the where_clause parameter and
            return it to the caller, in order to set a local variable.
            If problems are found selecting the correct where_clause to use, a default value is used.
            In this case, the function pointed it out to the user printing a WARNING.
            REMEMBER: there are some particular values used to pick up default queries:
                       "all" to select all wiki pages.
                       "soccer" for soccer players.
                       "dir" for film directors.
                       "writer" for writers.
                       "act" for actors.
            DEFAULT VALUE "all"
            :param argv: arguments'vector
            :return: it returns the where clause, if correct, or the default value "all".
        """
        try:
            # TODO set useful tests for where clause
            where = argv[2]
            return where
        except:
            print("WARNING -- The second argument should be a where clause or a std definition , \
             using \"all\" as default ")
            return "all"

    def get_lang(self):
        """
        get_lang() is used to pick up the value of language set.
        Typically is used from outer scope.
        :return: lang that is the wikipedia chapter the user wants to analyze
        """
        return self.lang

    def get_where(self):
        """
            get_where() is used to pick up the value of where_clause set.
            Typically is used from outer scope.
            :return: where that is the where_clause used to target a special subset of Wiki pages.
        """
        return self.where
