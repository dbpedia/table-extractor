import logging
import sys
import os

import param_test
import selector
import utilities
import analyzer

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'

'''
The script requires 2 arguments representing:
1) 2-characters string representing the chapter of Wikipedia yuo're interested in
    (e.g. "it" for it.dbpedia.org or "en" for en.wikipedia.org)
    default value is "en"


2) a string representing default queries (soccer, writer, act, elections, all) or a where clause as:
    "?s a <http://dbpedia.org/ontology/SoccerPlayer>.?s <http://dbpedia.org/ontology/wikiPageID> ?f"
    (it's important to specify that these resources have a related wikipage)
   Default value is "all"

'''


def main():
    # First of all a test is run over the parameters passed with the script, see param_test.py
    p_tester = param_test.ParamTester(sys.argv)
    # Variables language and where_clause are set
    # default language is en
    language = p_tester.get_lang()
    # default where_clause is "all"
    where_clause = p_tester.get_where()
    topic = p_tester.get_topic()
    utils = utilities.Utilities(language)
    # logging configuration
    setup_log(topic, language, utils)
    # creating a selector object, which is used to retrieve resources of interest (it depends on the scope)
    #  from dbpedia/wikipedia/jsonpedia
    select = selector.Selector(language, where_clause, topic)

    # Collecting resources of given topic
    select.collect_resources()
    # setting the resources list filename
    res_list_filename = select.get_res_list_filename()
    # Create an Analyzer
    analyzr = analyzer.Analyzer(language, topic, res_list_filename)
    # Analyze resources given in res_list_filename
    analyzr.analyze()
    # Serialize the RDF graph created
    analyzr.serialize()


def setup_log(topic, lang, utils):
    """
    Initializes and creates log file containing info and statistics
    :param topic:
    :param lang:
    :param utils
    :return: log file name
    """
    # getting time and date
    current_date_time = utils.get_date()

    current_dir = utils.get_current_dir()
    filename = "TableExtraction_" + topic + "_" + lang + "_(" + current_date_time + ")_" + ".log"
    path_desired = utils.join_paths(current_dir, '../Extractions/'+filename)

    logging.basicConfig(filename=path_desired, filemode='w', level=logging.DEBUG,
                        format='%(levelname)-4s %(asctime)-4s %(message)s', datefmt='%m/%d %I:%M:%S %p')

    # brief stat at the beginning of log, it indicates the scope of data and wiki/dbpedia chapter
    logging.info("You're analyzing wiki tables, wiki chapter: "+lang + ", topic: " + topic)


if __name__ == "__main__":
    main()
