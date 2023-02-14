# -*- coding: utf-8 -*-
"""
@author: pedroruas
"""

import json
import os
from Timer import Timer
from TriadicConcept import TriadicConcept


def mine(file_path, compute_minimality_for_infimum):
    Timer.start("Reading triadic concepts")
    triadic_concepts = TriadicConcept.get_triadic_concepts_from_input_file(
        file_path)
    print("Number of Triadic Concepts:", len(triadic_concepts))
    time = Timer.stop()
  
    Timer.start("Creating triadic concepts faces")
    faces, all_extents = TriadicConcept.create_triadic_concepts_faces(
        triadic_concepts)
    time = Timer.stop()
    
    Timer.start("Running T-iPred")
    links = TriadicConcept.T_iPred(triadic_concepts, faces, all_extents)
    print("Number of links:", len(links))
    time = Timer.stop()
    
    Timer.start("Computing F-Generators")
    updated_triadic_concepts = TriadicConcept.compute_f_generators_candidates(triadic_concepts, links, compute_minimality_for_infimum)
    time = Timer.stop()
    
    Timer.start("Computing Formal Context")
    formal_context = TriadicConcept.compute_formal_context(updated_triadic_concepts)
    time = Timer.stop()
    
    Timer.start("Validating Feature Generators")
    updated_triadic_concepts = TriadicConcept.compute_feature_generator_validation(updated_triadic_concepts, formal_context)
    time = Timer.stop()
    
    print("FEATURE GENERATORS VALIDATION")
    for c in updated_triadic_concepts:
        print(c)
        print()
    

def main():
    with open('configs.json') as json_file:
        data = json.load(json_file)

    for input_file_path in data['input_files']:
        _, file_name = os.path.split(input_file_path)
        output_dir = data['output_dir']
        print(f'Running Triadic Miner on {input_file_path} file...')
        compute_minimality_for_infimum = data[
            'compute_feature_generators_minimality_test_for_infimum']
        print()
        
        mine(input_file_path, compute_minimality_for_infimum)


if __name__ == "__main__":
    main()
