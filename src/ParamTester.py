import sys
import argparse

import settings

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class ParamTester:
    """
    ParamTester is a class used to test and set some main variables, usually received as main script arguments.
    NOTE: an object of this class has to be created passing the system arguments vector
    Once created, a paramTester tests if there are too many arguments passed to the script.
    Therefore it tests, and set, each parameter.
    Two functions are used to retrieve the values of parameters from an outer scope
    """
    def __init__(self):
        """
        Initialization of the tester. It has to set a local variable containing the arguments vector.
        Then it launches itself parse_arguments that automatically test the number of parameters passed.
        Two local variables (lang and where) are set testing corresponding arg vector's parameters.
        """
        self.single_res = None
        self.topic = None
        self.where = None

        self.args = self.parse_arguments()

        self.where = self.set_where_clause()
        self.lang = self.set_chapter()
        self.mode = self.set_mode()

    def parse_arguments(self):

        # initialize script parameters
        parser = argparse.ArgumentParser(description=settings.GENERAL_DESCRIPTION)

        m_e_group = parser.add_mutually_exclusive_group()

        m_e_group.add_argument('-s', '--single', type=lambda s: unicode(s, sys.getfilesystemencoding()),
                               help=settings.SINGLE_HELP)

        m_e_group.add_argument('-t', '--topic', type=str,
                               help=settings.TOPIC_HELP,
                               choices=settings.TOPIC_CHOICES)

        m_e_group.add_argument('-w', '--where', type=lambda s: unicode(s, sys.getfilesystemencoding()),
                               help=settings.WHERE_HELP)

        parser.add_argument('-c', '--chapter', type=str, default=settings.CHAPTER_DEFAULT,
                            help=settings.CHAPTER_HELP)

        parser.add_argument('-m', '--mode',
                            help=settings.MODE_HELP,
                            type=str, choices=settings.MODE_CHOICES, default=settings.MODE_DEFAULT)

        args = parser.parse_args()
        return args

    def set_where_clause(self):
        # TODO check out if it works for 'all'
        """
        This method sets the topic of interest, if possible.
        :return:
        """
        where_clause = ""

        if self.args.topic:
            for topic in settings.TOPIC_SPARQL:
                if self.args.topic == topic:
                    where_clause = settings.TOPIC_SPARQL[topic]
                    where_clause += settings.wiki_page
                    self.topic = topic

        elif self.args.single:
            self.topic = "single_resource"
            where_clause = "Not a where clause"
            self.single_res = self.args.single

        elif self.args.where:
            where_clause = self.args.where
            self.topic = "custom"

        else:
            where_clause = settings.wiki_page
            self.topic = "all_pages"

        return where_clause

    def set_mode(self):
        if self.args.mode:
            for mode in settings.MODE:
                if mode == self.args.mode:
                    return settings.MODE[mode]
        else:
            return settings.MODE_DEFAULT

    def set_chapter(self):
        if self.args.chapter:
            if len(self.args.chapter) < 3:
                return self.args.chapter
            else:
                return settings.CHAPTER_DEFAULT

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

    def get_topic(self):
        """
        get_topic() is used to pick up the value of topic.


        :return: self.topic, the scope of the resources targeted
        """
        return self.topic
