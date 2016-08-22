#!/usr/bin/env python2.7
# coding=utf-8

import ParamTester
import Selector
import Utilities
import Analyzer

__author__ = 'papalinis - Simone Papalini - papalini.simone.an@gmail.com'


def main():
    """
    The Table Extractor is a 2016 GSoC project; here you have the [first project idea]
     (wiki.dbpedia.org/ideas/idea/59/the-table-extractor/), assigned to Simone Papalini(s.papalini) and developed for
     DBpedia Spotlight organization.

    Note: Python 2.7, RDFlib, lxml are strictly required, so please install them in your environment.

    LICENSE: GNU GENERAL PUBLIC LICENSE. This is a OPEN SOURCE project.
     Feel free to download the project, use it, enhance functionalities, add your creativity to the project,
     but please SHARE your efforts with the rest of the World.
     Refer to [License file](https://github.com/dbpedia/table-extractor/blob/master/LICENSE)

    CONTACTS: feel free to e-mail me at: papalini.simone.an@gmail.com

    pyTableExtractor is a Python script used to carve out data from tables tou can find in wiki pages and to compose a
     RDF data set (.ttl file) with them.
    Please refer to project's Readme, [Github project page](https://github.com/dbpedia/table-extractor) and [2016 GSoC
     progress page](https://github.com/dbpedia/extraction-framework/wiki/GSoC_2016_Progress_Simone) to understand script's
     usage, purposes and options.

    pyTableExtractor.py represents the classical usage of classes and modules for this project;
     This script shows how you can easily recall modules and classes in order to:

     - Test parameters  (ParamTester.py)
     - Select a set of wikipedia pages/dbpedia resources you want to analyze (Selector.collect_resources())
     - Analyze tables you can find in selected resources' pages (Analyzer.analyze()) once they were collected with Selector.
     - Serialize the mapping result in order to make a RDF dataset (Analyzer.serialize())
     - Print a final report to have metrics to measure efficiency and effectiveness of algorithm and
       to have an help writing down new mapping rules. (Utilities.print_report())

    Once you have called pyTableExtractor with correct parameters (see DocStrings of ParamTester.py for help), just relax
    and wait for the script to serialize a RDF data set (Turtle format) and to report results in a log file.

    """

    # First of all a test is run over the parameters passed to the script, see ParamTester.py
    p_tester = ParamTester.ParamTester()

    # The following values are used by the other classes and set from ParamTester attributes :

    # language is a 2 letter string used to select the right wiki/dbpedia chapter and language to use mapping data cells
    language = p_tester.lang  # default: 'en'

    """
    where_clause is a string representing a piece of a SELECT SPARQL query.
       It is used to collect resources of a certain scope (Eg all the resources representing actors)
    """
    where_clause = p_tester.where  # default: "?s a <http://dbpedia.org/ontology/Election>"

    """
    topic is a string representing the scope of interest, used to collect resources and to choose the right mapping
     rules for data extracted from tables found in those resources.
    """
    topic = p_tester.topic  # default:"elections"

    """
    single_res is a string containing the name of a wiki page (the same of dbpedia in most cases)
      NOTE: single_res is not always set, and it is used only in the case a user want to analyze a single wiki page.
    """
    single_res = p_tester.single_res  # no default value

    # mode is a string and could be 'html' or 'json'. User can choose to use the Json or the Html parser with this value
    mode = p_tester.mode  # default: 'html'

    """
    Instancing a Utilities object using correct language and topic.
       Utilities would be used from other classes for different purposes (Internet connection, object testing,
       get time and date..) and to print a final report.
    """
    utils = Utilities.Utilities(language, topic)

    """
    res_list_filename is created but not set. In fact, if a user want to test a single resource, there isn't a
       list of resources to collect.
    """
    res_list_filename = None

    # Test if the user chose a single resource
    if not single_res:
        """
        if not, a Selector object is created, in order to retrieve resources of interest(it depends on the topic chosen)
          from dbpedia/wikipedia/jsonpedia.
        Note: a selector need 4 parameters, language, where_clause, topic chosen and the instance of utilities mainly
                 for a statistic purpose.
        """
        selector = Selector.Selector(language, where_clause, topic, utils)

        # Collecting resources of given topic using collect_resources().
        selector.collect_resources()
        """
        Retrieve the resources list's filename which the selector has just created (a .txt file you can find in
            /Resource lists/)
        """
        res_list_filename = selector.res_list_file

    """
    Now we want to analyze the set of resources (or the single one) we just retrieved, so an analyzer is created.
    Parameters passed: language, topic, utilities object, mode,  list filename and the name of the single resource.
    Note: the last two parameters (res_list_filename and single_res) are actually mutual exclusive, so in both cases,
         one of them is None.
    """
    analyzer = Analyzer.Analyzer(language, topic, utils, mode, res_list_filename, single_res)

    """
    To actually analyze the wiki pages and tables in them, you have to call the analyze() method.
    Note: Once analyze has started, it carves out tables from every single resource passed to the Analyzer, and then
        trying to apply mapping rules to every single data cells of those tables. See Mapper class to get an idea of the
        decision algorithm for the mapping.
    """
    analyzer.analyze()

    """
    At last, you surely want to serialize the RDF graph obtained with serialize() method.
    You can find the .ttl file containing the graph serialized in /Extractions/ along with
         the corresponding log file.
    """
    analyzer.serialize()

    # Finally, print a report for the current extraction, then exits.
    utils.print_report()

if __name__ == "__main__":
    main()
