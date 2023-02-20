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

    def write_header(file, title, number_identation):

        file.write('*' + '='*75 + '*\n')
        file.write('\t'*number_identation + title + '\n')
        file.write('*' + '='*75 + '*' + '\n\n')

    def save_report(self):
        self.check_output_folder()

        file = open(self.file_path, 'w', encoding='utf-8')
        Report.write_header(
            file, 'EXECUTION TIME REPORT FOR FILE: {0}'.format(self.file_name), 3)

        total_time = 0
        for module in self.module_time:
            file.write('{0} took {1} seconds\n'.format(
                module['module_name'], '{:.4f}'.format(module['time'])))
            total_time += module['time']

        file.write('\nTotal time: {0} seconds (or {1} minutes, or {2} hours)\n'.format(
            '{:.4}'.format(total_time), '{:.4}'.format(total_time/60), '{:.4}'.format(total_time/3600)))
        file.close()

    def save_triadic_concepts(self,
                              triadic_concepts,
                              triadic_concepts_file_path):

        file = open(triadic_concepts_file_path, 'w', encoding='utf-8')
        Report.write_header(file, 'TRIADIC CONCEPTS', 7)

        for concept in triadic_concepts:
            extent = concept.extent
            intent = concept.intent
            modus = concept.modus
            if extent == EMPTY_SET:
                extent = 'ø'
            extent = str(
                ', '.join([', '.join(x for x in sorted(extent))]))

            file.write('EXTENT: {0}\n'.format(extent))

            for attribute in zip(intent, modus):
                _int = str(
                    ', '.join([', '.join(x for x in sorted(attribute[0]))]))
                _mod = str(
                    ', '.join([', '.join(x for x in sorted(attribute[1]))]))
                file.write('({0} - {1})\n'.format(_int, _mod))
            file.write('\n')
        file.close()

    def save_links(self,
                   links,
                   links_concepts_file_path):

        file = open(links_concepts_file_path, 'w', encoding='utf-8')
        Report.write_header(file, 'LINKS COMPUTED BY T-iPRED', 7)

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

    def save_feature_generators(self,
                                triadic_concepts,
                                feature_generators_file_path):

        file = open(feature_generators_file_path, 'w', encoding='utf-8')
        Report.write_header(file, 'FEATURES GENERATORS', 7)

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

    def save_BCAI_implications(self,
                               BCAI_implications,
                               BCAI_implications_file_path):

        file = open(BCAI_implications_file_path, 'w', encoding='utf-8')
        Report.write_header(file, 'BCAI IMPLICATIONS', 7)

        for rule in BCAI_implications:
            left_part = str(
                ', '.join([', '.join(x for x in sorted(rule.antecedent))]))
            right_part = str(
                ', '.join([', '.join(x for x in sorted(rule.consequent))]))
            condition = str(
                ', '.join([', '.join(x for x in sorted(rule.condition))]))
            support = rule.support
            confidence = rule.confidence
            file.write('({0} -> {1}) {2} \t (support = {3}, confidence = {4})\n'.format(
                left_part, right_part, condition, support, confidence))
        file.close()

    def save_BACI_implications(self,
                               BACI_implications,
                               BACI_implications_file_path):

        file = open(BACI_implications_file_path, 'w', encoding='utf-8')
        Report.write_header(file, 'BACI IMPLICATIONS', 7)

        for rule in BACI_implications:
            left_part = str(
                ', '.join([', '.join(x for x in sorted(rule.antecedent))]))
            right_part = str(
                ', '.join([', '.join(x for x in sorted(rule.consequent))]))
            condition = str(
                ', '.join([', '.join(x for x in sorted(rule.condition))]))
            support = rule.support
            confidence = rule.confidence
            file.write('({0} -> {1}) {2} \t (support = {3}, confidence = {4})\n'.format(
                left_part, right_part, condition, support, confidence))
        file.close()

    def save_BCAAR_rules(self,
                         BCAAR_rules,
                         BCAAR_rules_file_path):

        file = open(BCAAR_rules_file_path, 'w', encoding='utf-8')
        Report.write_header(file, 'BCAAR ASSOCIATION RULES', 6)

        for rule in BCAAR_rules:
            left_part = str(
                ', '.join([', '.join(x for x in sorted(rule.antecedent))]))
            right_part = str(
                ', '.join([', '.join(x for x in sorted(rule.consequent))]))
            condition = str(
                ', '.join([', '.join(x for x in sorted(rule.condition))]))
            support = rule.support
            confidence = rule.confidence
            file.write('({0} -> {1}) {2} \t (support = {3}, confidence = {4})\n'.format(
                left_part, right_part, condition, support, confidence))
        file.close()

    def save_BACAR_rules(self,
                         BACAR_rules,
                         BACAR_rules_file_path):

        file = open(BACAR_rules_file_path, 'w', encoding='utf-8')
        Report.write_header(file, 'BACAR ASSOCIATION RULES', 6)

        for rule in BACAR_rules:
            left_part = str(
                ', '.join([', '.join(x for x in sorted(rule.antecedent))]))
            right_part = str(
                ', '.join([', '.join(x for x in sorted(rule.consequent))]))
            condition = str(
                ', '.join([', '.join(x for x in sorted(rule.condition))]))
            support = rule.support
            confidence = rule.confidence
            file.write('({0} -> {1}) {2} \t (support = {3}, confidence = {4})\n'.format(
                left_part, right_part, condition, support, confidence))
        file.close()

    def save_concept_stability(self,
                               triadic_concepts,
                               concept_stability_file_path):

        file = open(concept_stability_file_path, 'w', encoding='utf-8')
        Report.write_header(file, 'CONCEPT STABILITY', 7)

        for concept in triadic_concepts:
            extent = concept.extent
            if extent == EMPTY_SET:
                extent = 'ø'
            extent = str(
                ', '.join([', '.join(x for x in sorted(extent))]))
            file.write('EXTENT: {0}\n'.format(extent))
            stability = concept.concept_stability
            if not stability == []:
                for attribute in stability:
                    intent = str(
                        ', '.join([', '.join(x for x in sorted(attribute[0]))]))
                    modus = str(
                        ', '.join([', '.join(x for x in sorted(attribute[1]))]))
                    concept_stability = attribute[2]
                    file.write(
                        '({0} - {1}) = {2}\n'.format(intent, modus, concept_stability))
            else:
                file.write('[]\n')
            file.write('\n')
        file.close()

    def save_separation_index(self,
                              triadic_concepts,
                              separation_index_file_path):

        file = open(separation_index_file_path, 'w', encoding='utf-8')
        Report.write_header(file, 'SEPARATION INDEX', 7)

        for concept in triadic_concepts:
            extent = concept.extent
            if extent == EMPTY_SET:
                extent = 'ø'
            extent = str(
                ', '.join([', '.join(x for x in sorted(extent))]))
            file.write('EXTENT: {0}\n'.format(extent))
            separation_idx = concept.separation_index
            if not separation_idx == []:
                for attribute in separation_idx:
                    intent = str(
                        ', '.join([', '.join(x for x in sorted(attribute[0]))]))
                    modus = str(
                        ', '.join([', '.join(x for x in sorted(attribute[1]))]))
                    separation = round(attribute[2], 3)
                    file.write(
                        '({0} - {1}) = {2}\n'.format(intent, modus, separation))
            else:
                file.write('[]\n')
            file.write('\n')
        file.close()
