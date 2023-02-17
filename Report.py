# -*- coding: utf-8 -*-
"""
@author: pedroruas
"""

import os

EMPTY_SET = set([])


class Report():

    def __init__(self, file_path, file_name):
        self.file_path = file_path
        self.file_name = file_name
        self.module_time = []
        self.sections = []

    def add_module_time(self, title, time):
        self.module_time.append({'module_name': title, 'time': time})

    def check_output_folder(self):
        if not os.path.isdir(self.file_path.split('/')[0]):
            os.mkdir(self.file_path.split('/')[0])

    def save_report(self):
        self.check_output_folder()

        file = open(self.file_path, 'w', encoding='utf-8')
        file.write(
            'EXECUTION REPORT FOR FILE: {0}\n\n\n'.format(self.file_name))

        total_time = 0
        for module in self.module_time:
            file.write('{0} took {1} seconds\n'.format(
                module['module_name'], '{:.4f}'.format(module['time'])))
            total_time += module['time']

        file.write('\nTotal time: {0} seconds (or {1} minutes, or {2} hours)\n'.format(
            '{:.4}'.format(total_time), '{:.4}'.format(total_time/60), '{:.4}'.format(total_time/3600)))
        file.close()

    def write_header(file, title):

        file.write('*' + '='*75 + '*\n')
        file.write('\t'*7 + title + '\n')
        file.write('*' + '='*75 + '*' + '\n\n')

    def save_links(self, links, links_concepts_file_path):
        
        file = open(links_concepts_file_path, 'w', encoding='utf-8')
        Report.write_header(file, 'LINKS COMPUTED BY T-iPRED')

        for link in links:
            concept, target = link[1], link[0]
            if concept == EMPTY_SET:
                concept = 'ø'
            concept = str(
                ', '.join([', '.join(x for x in sorted(concept))]))
            target = str(
                ', '.join([', '.join(x for x in sorted(target))]))
            file.write(str(concept + ' --> ' + target + '\n'))
        file.close()

    def save_feature_generators(self, triadic_concepts, feature_generators_file_path):

        file = open(feature_generators_file_path, 'w', encoding='utf-8')
        file.write
        Report.write_header(file, 'FEATURES GENERATORS')

        for concept in triadic_concepts:
            extent = concept.extent
            generators = concept.feature_generator_minimal
            if extent == EMPTY_SET:
                extent = 'ø'
            extent = str(
                ', '.join([', '.join(x for x in sorted(extent))]))
            file.write('EXTENT: {0}\n'.format(extent))
            if generators != []:
                for gen in generators:
                    intent = str(
                        ', '.join([', '.join(x for x in sorted(gen[0]))]))
                    modus = str(
                        ', '.join([', '.join(x for x in sorted(gen[1]))]))
                    file.write('({0} - {1})\n'.format(intent, modus))
            else:
                file.write('[]\n')
            file.write('\n\n')
        file.close()
