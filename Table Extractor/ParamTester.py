# coding=utf-8

import sys
import argparse

import settings

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class ParamTester:
    """
    ParamTester:
    A class to test out parameters passed to the script (pyTableExtractor.py).
    ParamTester is a class which uses argparse module to parse arguments.
    It defines 5 optional attributes, defined optional as there are default values.

        NOTE: the first three arguments (topic, where_clause, single_res) are added in a MUTUAL EXCLUSIVE GROUP.
           In fact, in order to select a set of wiki pages to analyze, a user can choose a TOPIC
           (Eg wiki pages regarding Actors) or a custom WHERE_CLAUSE
           (Eg. "?s a <http://dbpedia.org/ontology/SoccerPlayer>" in order to select all soccer players pages), or a
           SINGLE_RES (Eg. "Elezioni_presidenziali_negli_Stati_Uniti_d'America_del_1888" which is a real page name).
           If none of these three arguments is chosen, with set_where_clause() is set a default TOPIC.
           See TOPIC_DEFAULT in settings.py to know what is this default topic.

        -t| --topic [str], DEFAULT: 'elections'
          topic is a string representing a topic the user can choose from.
          With this parameter is possible to pick up a corresponding where_clause to select a set of resources.
          Afterwards (see Mapper class) topic is used to choose a set of mapping rules to apply over data extracted from
          that set.
          See settings.py to add new topics and customize old ones.
          (Eg. 'elections' for elections, 'actors' for movies actors, 'directors' for film directors, 'all' to catch up
           all wiki pages (NOT recommended))

        -w| --where_clause [str], NO DEFAULT VALUE;
          where_clause represents SPARQL query used to collect resources from the specified (lang parameter) dbpedia
          SPARQL endpoint.
          It is a where clause of a SELECT SPARQL query(reference at
           https://www.w3.org/TR/rdf-sparql-query/#WritingSimpleQueries).
          This argument is intended to be used as a customized query, in fact you can use your where_clause:
          (Eg. "?s a <http://dbpedia.org/ontology/Actor>" can be used to select all actors,
               "?s a <http://dbpedia.org/ontology/Election>" to select all pages regarding electoral results)
          IMPORTANT NOTE: You can use all variables you want, BUT ?s must be the variable you are searching for,
          please do not use other variables as the query searches for ?s to get a result:
           prototype of the SPARQl query used:SELECT ?s as ?res WHERE {where_clause_containing_?s}

        -s | --single [str], NO DEFAULT VALUE;
          single_res is a string representing the name wiki page, in order to let the extractor work just on a single
           resource. If it set, DO NOT use --topic or --where_clause as they are used to find resources.
          Please use underscores instead of spaces --->"Elezioni_presidenziali_negli_Stati_Uniti_d'America_del_2008"
          to analyze https://it.wikipedia.org/wiki/Elezioni_presidenziali_negli_Stati_Uniti_d'America_del_2008
           and NOT "Elezioni presidenziali negli Stati Uniti d'America del 2008".

        -c | --chapter [str], DEFAULT: 'en'
          chapter is definitely the language of wikipedia (and dbpedia) you want to analyze.
          Use a two lowercase character string.
          This parameter is useful to select resources and wiki pages from the right wiki/dbpedia chapter.
          (Eg. 'en' stands for en.wikipedia.org and dbpedia.org,'it' for it.wikipedia.org and it.dbpedia.org and so on)

        -m | --mode [str], DEFAULT: 'html';
         As the Extractor has a Html Parser and a sketch of a Json one, you can choose one or the other with mode
          parameter. It is possible to choose between 'html' | 'h' and 'json' |'j'. Please consider that Json Parser
           has been abandoned in favor of Html Parser, after a lot of problems has encountered.
    """

    def __init__(self):
        """
        Initialization of the tester. The name of parameters are defined and set to None
         Note: lang stands for chapter.
        """
        self.single_res = None
        self.topic = None
        self.where = None
        self.lang = None
        self.mode = None

        # self.args will contain the arguments parsed by parse_arguments()
        self.args = self.parse_arguments()

        """set_where_clause() is used to set the where_clause which will be used by selector to retrieve a list of
           resources.
           NOTE: self.topic is set inside set_where_clause() """
        self.where = self.set_where_clause()

        # set_chapter() is used to set reference chapter (so en.wikipedia.org or it.wikipedia.org..)
        self.lang = self.set_chapter()

        self.mode = self.set_mode()

    def parse_arguments(self):

        # initialize a argparse.ArgumentParser with a general description coming from settings.GENERAL_DESCRIPTION
        parser = argparse.ArgumentParser(description=settings.GENERAL_DESCRIPTION)

        # A mutual exclusive group is used to contain --single or --topic or --where parameters.
        m_e_group = parser.add_mutually_exclusive_group()

        # -s|--single unicode string representing a single wiki page you want to analyze.
        m_e_group.add_argument('-s', '--single', type=lambda s: unicode(s, sys.getfilesystemencoding()),
                               help=settings.SINGLE_HELP)

        """-t|--topic string representing a topic or a scope. This scope is used to select a list of resources and
           particular mapping rules during the mapping moment."""
        m_e_group.add_argument('-t', '--topic', type=str, help=settings.TOPIC_HELP, choices=settings.TOPIC_CHOICES)

        # -w |--where string representing a custom where_clause. Please use ?s as the variable you are searching for.
        m_e_group.add_argument('-w', '--where', type=lambda s: unicode(s, sys.getfilesystemencoding()),
                               help=settings.WHERE_HELP)

        """ -c |--chapter 2 characters string representing the language, or better the wikipedia and dbpedia chapter,
           you choose. It is used to collect the resources from the right service, and to choose right mapping rules."""
        parser.add_argument('-c', '--chapter', type=str, default=settings.CHAPTER_DEFAULT, help=settings.CHAPTER_HELP)

        """ -m | --mode is a string representing the type of Parser the user want to use.
          You can choose between 'html'('h') an 'json' ('j') Parser.
         NOTE: It is suggested to use the Html Parser instead the Json one as the development of the last one has been
         left behind due to major problems."""
        parser.add_argument('-m', '--mode', help=settings.MODE_HELP, type=str,
                            choices=settings.MODE_CHOICES, default=settings.MODE_DEFAULT)

        # parsing actual arguments and return them to the caller.
        args = parser.parse_args()

        return args

    def set_where_clause(self):

        """
        This method is used to set where_clause and even topic attributes.
        It can discern if the user has chosen a custom where_clause, a single_res, or a topic and set correct topic and
        where clause as the case.

        :return where_clause used to set the SPARQL query to recover a resources' list from dbpedia.
         If it is the actual case, the method sets the class' where_clause, as defined in
         settings.py and the topic.

        """
        where_clause = ""

        """ It first test out the if user chose a topic with -t option and if this topic is already defined between those
          you can find at settings.py. If the response is True, it sets where_clause as that defined in
          settings.TOPIC_SPARQL_WHERE_CLAUSE[topic]"""
        if self.args.topic:
            for topic in settings.TOPIC_SPARQL_WHERE_CLAUSE:
                # test if the parameter is equal to one of the topic defined in settings.TOPIC_SPARQL_WHERE_CLAUSE
                if self.args.topic == topic:
                    # set the where_clause to one defined in TOPIC_SPARQL_WHERE_CLAUSE[topic]
                    where_clause = settings.TOPIC_SPARQL_WHERE_CLAUSE[topic]
                    """ adding to where_clause ". ?s <http://dbpedia.org/ontology/wikiPageID> ?f" that guarantees that
                        resources we extract are actual wiki pages"""
                    where_clause += settings.WIKI_PAGE
                    # setting the object topic to the topic user selected
                    self.topic = topic
            
            # if user passed wrong topic (or one not yet defined) self.topic would be a None object
            if not self.topic:
                # if so, states the situation to the user, enlisting which topics are defined
                print("Please choose a defined topic from:")
                for topic in settings.TOPIC_SPARQL_WHERE_CLAUSE:
                    print ("- %s" % topic)
                # then states that the script will continue using the default topic.
                print("The script will continue using default topic (%s)." % settings.TOPIC_DEFAULT)

        elif self.args.single:
            """ if the user didn't choose a topic but a single resource (-s option), the method set object's topic
            as 'single_resource', where_clause to a string == 'Not a where clause' and object's single_res attribute to
            one passed to the script; before that, it refines the string user passed, trying to correct little errors.
            see refine_single_res() for that. """

            self.topic = "single_resource"
            where_clause = "Not a where clause"
            # call the refine method to ensure that the string passed has underscores instead of spaces.
            self.refine_single_res()
            self.single_res = self.args.single

        elif self.args.where:
            """ if -w option has been used, the args.where is set with a custom sparql where_clause, so the method set
            where_clause to the one passed as an argument and the topic as 'custom' """

            where_clause = self.args.where
            self.topic = "custom"
        
        """if no option (-t|-s|-w) is used, self.topic is equal to None. So set the DEFAULT TOPIC and corresponding
           WHERE_CLAUSE"""
        if not self.topic:
            self.topic = settings.TOPIC_DEFAULT
            where_clause = settings.TOPIC_SPARQL_WHERE_CLAUSE[self.topic]

        # finally returns where_clause
        return where_clause

    def refine_single_res(self):
        """
         method used to refine the single_res string (if used -s option)
        :return:
        """
        # simply set args.single as the same string where spaces are replaced by underscores
        self.args.single = self.args.single.replace(" ", "_")

    def set_chapter(self):
        """
        method used to refine string passed as a -c option and to return it if it is a 2 alpha-characters string,
         or to return the default chapter string as defined in settings.CHAPTER_DEFAULT
        :return: self.args.chapter if user use -c option | settings.CHAPTER_DEFAULT else.
        """
        if self.args.chapter:
            if self.args.chapter.isalpha() and len(self.args.chapter) == 2:
                return self.args.chapter.lower()
            else:
                return settings.CHAPTER_DEFAULT

    def set_mode(self):
        """
        Method which returns the mode ('html' or 'json') that will be used to choose which parser would be adopted by
        the Extractor.
        :return: mode chosen by the user with -m option if it is defined in settings.py or
         the default mode (settings.MODE_DEFAULT)
        """
        if self.args.mode:  # if -m option is used
            # test if the mode passed as an argument is defined in settings.MODE
            for mode in settings.MODE:
                if mode == self.args.mode:
                    return settings.MODE[mode]
        else:
            return settings.MODE_DEFAULT


