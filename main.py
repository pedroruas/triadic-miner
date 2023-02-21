# -*- coding: utf-8 -*-
"""
@author: pedroruas
"""

import json
import os
from Timer import Timer
from TriadicConcept import TriadicConcept
from AssociationRules import AssociationRule
from Report import Report


def triadic_miner(file_path,
                  file_name,
                  minimum_support_rules,
                  minimum_confidence_rules,
                  compute_feature_generators_for_infimum,
                  compute_concept_stability,
                  compute_separation_index,
                  save_hasse_diagram,
                  report_file_path,
                  triadic_concepts_file_path,
                  links_concepts_file_path,
                  feature_generators_file_path,
                  BCAI_implications_file_path,
                  BACI_implications_file_path,
                  BCAAR_rules_file_path,
                  BACAR_rules_file_path,
                  concept_stability_file_path,
                  separation_index_file_path,
                  hasse_diagram_file_path):

    report = Report(report_file_path, file_name)
    report.check_output_folder()

    Timer.start("Reading Triadic Concepts")
    triadic_concepts = TriadicConcept.get_triadic_concepts_from_input_file(
        file_path)
    print("Number of Triadic Concepts:", len(triadic_concepts))
    time = Timer.stop()
    report.add_module_time('Reading Triadic Concepts', time)

    Timer.start("Creating Triadic Concepts Faces")
    faces, all_extents = TriadicConcept.create_triadic_concepts_faces(
        triadic_concepts)
    time = Timer.stop()
    report.add_module_time('Creating Triadic Concepts Faces', time)

    Timer.start("Running T-iPred")
    links = TriadicConcept.T_iPred(triadic_concepts, faces, all_extents)
    print("Number of links:", len(links))
    time = Timer.stop()
    report.add_module_time('Running T-iPred', time)

    Timer.start("Computing F-Generators")
    updated_triadic_concepts = TriadicConcept.compute_f_generators_candidates(
        triadic_concepts, links, compute_feature_generators_for_infimum)
    time = Timer.stop()
    report.add_module_time('Computing F-Generators', time)

    Timer.start("Computing Formal Context")
    formal_context = TriadicConcept.compute_formal_context(
        updated_triadic_concepts)
    time = Timer.stop()
    report.add_module_time('Computing Formal Context', time)

    Timer.start("Validating Feature Generators")
    updated_triadic_concepts = TriadicConcept.compute_feature_generator_validation(
        updated_triadic_concepts, formal_context)
    time = Timer.stop()
    report.add_module_time('Validating Feature Generators', time)

    Timer.start("Computing BCAI Implications")
    BCAI_implications = AssociationRule.compute_BCAI_implications(
        updated_triadic_concepts, minimum_support_rules)
    time = Timer.stop()
    report.add_module_time('Computing BCAI Implications', time)

    Timer.start("Computing BACI Implications")
    BACI_implications = AssociationRule.compute_BACI_implications(
        updated_triadic_concepts, minimum_support_rules)
    time = Timer.stop()
    report.add_module_time('Computing BACI Implications', time)

    Timer.start("Computing BCAAR Association Rules")
    BCAAR_rules = AssociationRule.compute_BCAAR_association_rules(
        updated_triadic_concepts, minimum_support_rules,
        minimum_confidence_rules, links)
    time = Timer.stop()
    report.add_module_time('Computing BCAAR Association Rules', time)

    Timer.start("Computing BACAR Association Rules")
    BACAR_rules = AssociationRule.compute_BACAR_association_rules(
        updated_triadic_concepts, minimum_support_rules,
        minimum_confidence_rules, links)
    time = Timer.stop()
    report.add_module_time('Computing BACAR Association Rules', time)

    Timer.start("Computing Extensional Generators")
    updated_triadic_concepts = TriadicConcept.compute_extensional_generators(
        updated_triadic_concepts, links)
    time = Timer.stop()
    report.add_module_time('Computing Extensional Generators', time)

    Timer.start("Computing Extensional Implications")
    extensional_rules = AssociationRule.compute_extensional_implications(
        updated_triadic_concepts)
    time = Timer.stop()
    report.add_module_time('Computing Extensional Implications', time)

    if compute_concept_stability:
        Timer.start("Computing Concept Stability")
        updated_triadic_concepts = TriadicConcept.compute_concept_stability(
            triadic_concepts, formal_context)
        time = Timer.stop()
        report.add_module_time('Computing Concept Stability', time)

    if compute_separation_index:
        Timer.start("Computing Separation Index")
        updated_triadic_concepts = TriadicConcept.separation_index_calculation(
            updated_triadic_concepts)
        time = Timer.stop()
        report.add_module_time('Computing Separation Index', time)

    if save_hasse_diagram:
        Timer.start("Creating the Hasse Diagram")
        TriadicConcept.create_hasse_diagram(
            updated_triadic_concepts, links, hasse_diagram_file_path)
        time = Timer.stop()
        report.add_module_time('Creating the Hasse Diagram', time)

    report.save_report()
    report.save_triadic_concepts(
        updated_triadic_concepts, triadic_concepts_file_path)
    report.save_links(links, links_concepts_file_path)
    report.save_feature_generators(
        updated_triadic_concepts, feature_generators_file_path)
    report.save_BCAI_implications(
        BCAI_implications, BCAI_implications_file_path)
    report.save_BACI_implications(
        BACI_implications, BACI_implications_file_path)
    report.save_BCAAR_rules(BCAAR_rules, BCAAR_rules_file_path)
    report.save_BACAR_rules(BACAR_rules, BACAR_rules_file_path)
    if compute_concept_stability:
        report.save_concept_stability(
            updated_triadic_concepts, concept_stability_file_path)
    if compute_separation_index:
        report.save_separation_index(
            triadic_concepts, separation_index_file_path)


def main():

    with open('configs.json') as json_file:
        data = json.load(json_file)

    for input_file_path in data['input_files']:
        _, file_name = os.path.split(input_file_path)
        file_name = file_name.split(".data.out")[0]
        output_dir = data['output_dir']
        print(f'Running Triadic Miner on {input_file_path} file...\n')
        minimum_support_rules = data['minimum_support_rules']
        minimum_confidence_rules = data['minimum_confidence_rules']
        compute_feature_generators_for_infimum = data[
            'compute_feature_generators_for_infimum']
        compute_concept_stability = data['compute_concept_stability']
        compute_separation_index = data['compute_separation_index']
        save_hasse_diagram = data[
            'save_hasse_diagram']

        report_file_path = '{0}{1}.report'.format(output_dir, file_name)
        triadic_concepts_file_path = '{0}{1}.concepts'.format(
            output_dir, file_name)
        links_concepts_file_path = '{0}{1}.links'.format(output_dir, file_name)
        feature_generators_file_path = '{0}{1}.generators'.format(
            output_dir, file_name)
        BCAI_implications_file_path = '{0}{1}.BCAI_implications'.format(
            output_dir, file_name)
        BACI_implications_file_path = '{0}{1}.BACI_implications'.format(
            output_dir, file_name)
        BCAAR_rules_file_path = '{0}{1}.BCAAR_rules'.format(
            output_dir, file_name)
        BACAR_rules_file_path = '{0}{1}.BACAR_rules'.format(
            output_dir, file_name)
        concept_stability_file_path = '{0}{1}.concept_stability'.format(
            output_dir, file_name)
        separation_index_file_path = '{0}{1}.separation_index'.format(
            output_dir, file_name)
        hasse_diagram_file_path = '{0}{1}.graphml'.format(
            output_dir, file_name+'_hasse_diagram')

        triadic_miner(input_file_path,
                      file_name,
                      minimum_support_rules,
                      minimum_confidence_rules,
                      compute_feature_generators_for_infimum,
                      compute_concept_stability,
                      compute_separation_index,
                      save_hasse_diagram, report_file_path,
                      triadic_concepts_file_path,
                      links_concepts_file_path,
                      feature_generators_file_path,
                      BCAI_implications_file_path,
                      BACI_implications_file_path,
                      BCAAR_rules_file_path,
                      BACAR_rules_file_path,
                      concept_stability_file_path,
                      separation_index_file_path,
                      hasse_diagram_file_path)


if __name__ == "__main__":
    main()
