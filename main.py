# -*- coding: utf-8 -*-
"""
@author: pedroruas
"""

import json
import os
from Timer import Timer
import timeit
from TriadicConcept import TriadicConcept
from AssociationRules import AssociationRule


def triadic_miner(file_path, compute_minimality_for_infimum, compute_concept_stability, save_hasse_diagram, file_name):
    Timer.start("Reading triadic concepts")
    triadic_concepts = TriadicConcept.get_triadic_concepts_from_input_file(
        file_path)
    print("Number of Triadic Concepts:", len(triadic_concepts))
    Timer.stop()
    
    Timer.start("Creating triadic concepts faces")
    faces, all_extents = TriadicConcept.create_triadic_concepts_faces(
        triadic_concepts)
    Timer.stop()
    
    Timer.start("Running T-iPred")
    links = TriadicConcept.T_iPred(triadic_concepts, faces, all_extents)
    print("Number of links:", len(links))
    Timer.stop()
    
    Timer.start("Computing F-Generators")
    updated_triadic_concepts = TriadicConcept.compute_f_generators_candidates(triadic_concepts, links, compute_minimality_for_infimum)
    Timer.stop()
    
    Timer.start("Computing Formal Context")
    formal_context = TriadicConcept.compute_formal_context(updated_triadic_concepts)
    Timer.stop()
    # print(formal_context)
    
    Timer.start("Validating Feature Generators")
    updated_triadic_concepts = TriadicConcept.compute_feature_generator_validation(updated_triadic_concepts, formal_context)
    Timer.stop()
        
    Timer.start("Computing BCAI Implications")
    BCAI_implications = AssociationRule.compute_BCAI_implications(updated_triadic_concepts)
    Timer.stop()
    
    Timer.start("Computing BACI Implications")
    BACI_implications = AssociationRule.compute_BACI_implications(updated_triadic_concepts)
    Timer.stop()
    
    Timer.start("Computing BCAAR Association Rules")
    BCAAR_rules = AssociationRule.compute_BCAAR_association_rules(updated_triadic_concepts, links)
    Timer.stop()
    
    Timer.start("Computing BACAR Association Rules")
    BACAR_rules = AssociationRule.compute_BACAR_association_rules(updated_triadic_concepts, links)
    Timer.stop()
    
    if compute_concept_stability:
        Timer.start("Computing Concept Stability")
        updated_triadic_concepts = TriadicConcept.compute_concept_stability(triadic_concepts, formal_context)
        Timer.stop()
    
    if save_hasse_diagram:
        Timer.start("Creating the Hasse Diagram")
        TriadicConcept.create_hasse_diagram(updated_triadic_concepts, links, file_name)
        time = Timer.stop()
    
    # print("TRIADIC CONCEPTS")
    # for c in updated_triadic_concepts:
    #     print(c)
    #     print()
    # print()
        
    # print("BCAI IMPLICATIONS")    
    # for rule in BCAI_implications:
    #     print(rule)
    #     print()
    # print()
        
    # print("BACI IMPLICATIONS")     
    # for rule in BACI_implications:
    #     print(rule)
    #     print()
    # print()
    
    # print("BCAAR RULES")    
    # for rule in BCAAR_rules:
    #     print(rule)
    #     print()
    # print()
    
    # print("BACAR RULES")    
    # for rule in BACAR_rules:
    #     print(rule)
    #     print()

def main():
    with open('configs.json') as json_file:
        data = json.load(json_file)

    for input_file_path in data['input_files']:
        _, file_name = os.path.split(input_file_path)
        file_name = file_name.split(".data.out")[0]
        output_dir = data['output_dir']
        print(f'Running Triadic Miner on {input_file_path} file...')
        compute_minimality_for_infimum = data[
            'compute_feature_generators_minimality_test_for_infimum']
        compute_concept_stability = data['compute_concept_stability']
        save_hasse_diagram = data[
            'save_hasse_diagram']
        print()
        
        start_time = timeit.default_timer()
        triadic_miner(input_file_path, compute_minimality_for_infimum, compute_concept_stability , save_hasse_diagram, file_name)
        end_time = timeit.default_timer()
        print("TOTAL TIME:  %0.4f SECONDS" % float(end_time - start_time))


if __name__ == "__main__":
    main()
