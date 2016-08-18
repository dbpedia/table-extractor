
import ParamTester
import Selector
import Utilities
import Analyzer

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
    # arguments = parse_arguments()
    # First of all a test is run over the parameters passed with the script, see ParamTester.py
    p_tester = ParamTester.ParamTester()
    # Variables language and where_clause are set
    # default language is en
    language = p_tester.lang
    # default where_clause is "all"
    where_clause = p_tester.where
    topic = p_tester.topic
    single_res = p_tester.single_res
    mode = p_tester.mode

    utils = Utilities.Utilities(language, topic)

    res_list_filename = None
    if not single_res:
        # creating a selector object, which is used to retrieve resources of interest (it depends on the scope)
        #  from dbpedia/wikipedia/jsonpedia
        selector = Selector.Selector(language, where_clause, topic, utils)
        # Collecting resources of given topic
        selector.collect_resources()
        # setting the resources list filename
        res_list_filename = selector.get_res_list_filename()

    # Create an Analyzer
    analyzer = Analyzer.Analyzer(language, topic, utils, mode, res_list_filename, single_res)
    # Analyze resources given in res_list_filename
    analyzer.analyze()
    # Serialize the RDF graph created
    analyzer.serialize()
    # Print final report for the current extraction, then exits
    utils.print_report()

if __name__ == "__main__":
    main()
