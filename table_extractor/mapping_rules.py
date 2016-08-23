# coding=utf-8

# Mapping rules used to map table's data, topics are used to evaluate functions with same name.

# Mapping topics is defined here to store which topics are mapped and for which wiki chapter ('en', 'it'...)
MAPPING_TOPICS = {'en': [],
                  'it': ['elections']}


# This second part is a sketch of data structures which would possibly be used in a refactoring of Mapper class
# By now MAPPING_RULES_IT isn't yet used
MAPPING_RULES_IT = {'elections': {
                            'Candidati - Presidente': {
                                'alias': ['Candidato', 'candidato', 'Candidato presidente',
                                          'Candidati - Presidente (Stato)'],
                                'cell_subject': 'row',
                                'cell_predicate': {'URIRef': 'http://dbpedia.org/property/electoralVote)'},
                                'cell_object': {}
                            },

                            'Candidati - Vicepresidente': {
                                'alias': ['Candidato Vicepresidente',
                                          'Candidato vicepresidente',
                                          'Candidati - Vicepresidente (Stato)'],
                                'cell_subject': 'row'},

                            'Partito': {
                                'alias': ['Candidati - Partito', 'Lista']},

                            'Grandi elettori - #': {
                                'alias': ['Grandi elettori - n.', 'Grandi elettori - Num.',
                                          'Grandi Elettori ottenuti', 'Voti Elettorali',
                                          'Grandi Elettori', 'Voti elettorali', 'Elettori'],
                                'cell_subject': 'row'},

                            'Voti - #': {
                                'alias': ['Voti - n.', 'Voti - Num.', 'Voti', 'Voti Popolari',
                                          'Voti popolari'],
                                'cell_subject': 'row'},

                            'Voti - %': {
                                'alias': ['?% voti', 'Percentuale', '% voti', '%', '?%', 'Voti (%)',
                                          'Voto popolare - Percentuale'],
                                'cell_subject': 'row'},


                                 }
                    }
