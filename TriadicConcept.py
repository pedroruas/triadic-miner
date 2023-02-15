# -*- coding: utf-8 -*-
"""
@author: pedroruas
"""

import os
from tqdm import tqdm
import pandas as pd
from dataclasses import dataclass, field
import threading
from multiprocessing.pool import ThreadPool
import multiprocessing
from itertools import repeat
from concepts import Definition, Context

EMPTY_SET = set([])
PROCESSES = 8  # Amount of threads to be used while computing and validating Feature-Generators
compute_minimality_for_infimum = False


@dataclass(slots=True, order=True)
class TriadicConcept:
    """Class that represents a triadic concept (extent, intent, modus)."""
    sort_index: int = field(init=False, repr=False)
    extent: set
    intent: set
    modus: set
    extent_size: int
    feature_generator: list[list] = field(default_factory=list)
    feature_generator_minimal: list[list] = field(default_factory=list)
    feature_generator_candidates: list[list] = field(default_factory=list)
    BCAI_implications: list[list] = field(default_factory=list)
    BACI_implications: list[list] = field(default_factory=list)
    BCAAR_associarion_rules: list[list] = field(default_factory=list)
    BACAR_associarion_rules: list[list] = field(default_factory=list)
    
    def __post_init__(self):
        self.sort_index = self.extent_size

    def __str__(self):
        return f'Extent: {self.extent}\nIntent: {self.intent}\nModus: {self.modus}\nExtent size: {self.extent_size}\nFeature Generators Candidates: {self.feature_generator_candidates}\nFeature Generators: {self.feature_generator}\nFeature Generators Minimal: {self.feature_generator_minimal}\nBCAI Implications: {self.BCAI_implications}\nBACI Implications: {self.BACI_implications}\nBCAAR Associarion Rules: {self.BCAAR_associarion_rules}\nBACAR Associarion Rules: {self.BACAR_associarion_rules}'
    
    def __eq__(self, other):
        if other == self.extent:
            return True
        return False

    def get_triadic_concepts_from_input_file(file_path):
        """Function that reads the triadic concepts computed by Data Peeler 
        and transforms them in objects of the class TriadicConcept

        Args:
                file_path (string): path to the input file

        Returns:
                list: returns a list of TriadicConcept objects
        """
        triadic_concepts = []
        with open(file_path, 'r') as reader:
            for row in reader:
                line = row.rstrip('\n').split(" ")
                if line[0] == 'ø':
                    line[0] = frozenset(EMPTY_SET)
                    triadic_concepts.append(TriadicConcept(line[0],
                                            set(line[1].split(',')),
                                            set(line[2].split(',')),
                                            len(line[0])))
                else:
                    triadic_concepts.append(TriadicConcept(set(line[0].split(',')),
                                            set(line[1].split(',')),
                                            set(line[2].split(',')),
                                            len(set(line[0].split(',')))))

        unique_triadic_concepts_extents = []
        for concept in triadic_concepts:
            if concept.extent not in unique_triadic_concepts_extents:
                unique_triadic_concepts_extents.append(concept.extent)

        unique_triadic_concepts = []
        for unique_extent in unique_triadic_concepts_extents:
            list_intent = []
            list_modus = []
            for concept in triadic_concepts:
                if concept.extent == unique_extent:
                    list_intent.append(concept.intent)
                    list_modus.append(concept.modus)
            unique_triadic_concepts.append(TriadicConcept(
                unique_extent, list_intent, list_modus, len(unique_extent)))
        return sorted(unique_triadic_concepts, key=lambda x: x.extent_size, reverse=False)

    def create_triadic_concepts_faces(triadic_concepts):
        faces = {}
        all_extents = set()
        for concept in triadic_concepts:
            faces.update({frozenset(concept.extent): set({})})
            all_extents = all_extents | set({frozenset(concept.extent)})

        return faces, all_extents

    def T_iPred(triadic_concepts, faces, all_extents):
        """Function that calculates the links between Triadic Concepts

        Args:
                triadic_concepts (list): list of TriadicConcept objects

        Returns:
                list: returns a list with the links between Triadic Concepts
        """
        links = []
        border_max = 0 # border <- the very first element with the smallest EXTENT cardinality
        border = triadic_concepts[0].extent

        for concept in tqdm(triadic_concepts[1:]):
            Ci = set(concept.extent)
            if len(Ci) > 1:
                flag = True
            list_candidate = []
            candidate_set = set({})
            for element in border:
                aux = frozenset(Ci) & set(element)
                if aux != EMPTY_SET:
                    candidate_set = candidate_set | set(frozenset({aux}))
                else:
                    candidate_set = candidate_set | set(aux)
            discarded = candidate_set - all_extents
            candidate_set = candidate_set - discarded
            if candidate_set != EMPTY_SET:
                for element in candidate_set:
                    if element not in list_candidate:
                        list_candidate.append(element)
            else:
                list_candidate.append(frozenset(EMPTY_SET))
            for element in list_candidate:
                try:
                    c = faces[frozenset(element)] & Ci
                    c_belongs_discarded = False
                    for c_elem in discarded:
                        if c | element == c_elem:
                            c_belongs_discarded = True

                    if c == EMPTY_SET or c_belongs_discarded:
                        new_link = Ci, element
                        links.append(new_link)
                        faces[frozenset(element)] = faces[frozenset(
                            element)] | (Ci - frozenset(element))
                        border = border - frozenset({element})
                        flag = True
                except:
                    raise
            if flag:
                border = border | (frozenset({frozenset(Ci)}))
            else:
                border = frozenset({frozenset(Ci)}) | set(border)
            flag = False
            if len(border) > border_max:
                border_max = len(border)

        return links

    def list_of_links_to_dict(links):
        links_dic = {}
        for item in links:
            aux = []
            target, source = item
            if source not in links_dic:
                aux.append(target)
                links_dic.update({source: aux})
            else:
                aux = list(links_dic[source])
                aux.append(target)
                links_dic.update({source: aux})

        return links_dic

    def getContext_K1K2(intent, modus):
        
        intent = [list(x) for x in intent]
        modus = [list(x) for x in modus]

        if len(intent) < 2:
            context = pd.DataFrame(index=intent, columns=modus)
            context = context.fillna(True)
        else:
            intent_aux = [y for x in intent for y in x]
            intent_aux = list(set(intent_aux))
            modus_aux = [y for x in modus for y in x]
            modus_aux = list(set(modus_aux))
            context = pd.DataFrame(index=list(
                intent_aux), columns=list(modus_aux))
            context = context.fillna(False)
            for intent_item, modus_item in zip(intent, modus):
                context.loc[intent_item, modus_item] = True
        return context

    def f_generator(concept, links_dict, triadic_concepts):

        def compute_face_kth_successor(target_intent, target_modus):
            for intent_item, modus_item in zip(target_intent, target_modus):
                for x in intent_item:
                    for y in modus_item:
                        try:
                            if str(y) in context.columns and str(x) in context.index:
                                context.loc[x, y] = False
                        except:
                            raise
            return context

        G = []
        G1 = []
        U3 = []
        F = []
        feature_generator = {}
        t_generator = {}
        dic_G = {}

        successors_concepts = links_dict[concept]

        for successor in successors_concepts:
            target = frozenset(successor)
            source = frozenset(concept)
            current_concept = triadic_concepts[triadic_concepts.index(
                set(source))]
            successor_concept = triadic_concepts[triadic_concepts.index(
                set(target))]
            current_concept_extent = triadic_concepts[triadic_concepts.index(
                set(source))].extent

            if source not in feature_generator:
                source_intent = current_concept.intent
                source_modus = current_concept.modus
                target_intent = successor_concept.intent
                target_modus = successor_concept.modus
                context = TriadicConcept.getContext_K1K2(
                    source_intent, source_modus)

                context = compute_face_kth_successor(
                    target_intent, target_modus)

                for i, row in context.iterrows():
                    for j, column in row.items():
                        _intent = "".join([i for i in i])
                        _modus = "".join([j for j in j])
                        try:
                            if column:
                                if [_intent, _modus] not in G:
                                    G.append([_intent, _modus])
                        except:
                            raise

                dic_G.update({source: G})
                t_generator.update({source: G})

            else:
                source_intent = current_concept.intent
                source_modus = current_concept.modus
                context = TriadicConcept.getContext_K1K2(
                    source_intent, source_modus)
                target_intent = successor_concept.intent
                target_modus = successor_concept.modus
                G = t_generator[source]

                context = compute_face_kth_successor(
                    target_intent, target_modus)

                for i, row in context.iterrows():
                    for j, column in row.items():
                        _intent = "".join([i for i in i])
                        _modus = "".join([j for j in j])
                        try:
                            if column:
                                if _modus not in U3:
                                    U3.append(_modus)
                        except:
                            raise
                    if [_intent, U3] not in F and U3 != []:
                        if [_intent, U3] not in F:
                            F.append([_intent, U3])
                    U3 = []

                G1 = list(G)
                p = len(F)
                for g in G:
                    i = 0
                    j = 0
                    while i == 0 and j < p:
                        for f in F:
                            j += 1
                            UF2, UF3 = f
                            UG2, UG3 = g

                            if isinstance(UF2, str):
                                UF2 = [UF2]
                            if isinstance(UF3, str):
                                UF3 = [UF3]
                            if isinstance(UG2, str):
                                UG2 = [UG2]
                            if isinstance(UG3, str):
                                UG3 = [UG3]

                            if set(UF2) & set(UG2) != EMPTY_SET and set(UF3) & set(UG3) != EMPTY_SET:
                                i = 2
                                break

                            elif set(UF2) & set(UG2) == EMPTY_SET and set(UF3) & set(UG3) != EMPTY_SET:
                                if i == 0:
                                    i = 1
                                for e in UF2:
                                    e = [e]
                                    if [list(set(UG2) | set(e)), UG3] not in G1:
                                        G1.append(
                                            [list(set(UG2) | set(e)), UG3])

                            elif set(UF2) & set(UG2) != EMPTY_SET and set(UF3) & set(UG3) == EMPTY_SET:
                                if i == 0:
                                    i = 1
                                for e in UF3:
                                    e = [e]
                                    if [UG2, list(set(UG3) | set(e))] not in G1:
                                        G1.append(
                                            [UG2, list(set(UG3) | set(e))])
                    if i == 1:
                        if g in G1:
                            G1.remove(g)
                t_generator.update({source: G1})
            feature_generator.update({source: context})
            context = pd.DataFrame()
            G = []
            G1 = []
            F = []
            U3 = []

        updadet_triadic_concept = triadic_concepts[triadic_concepts.index(
            current_concept_extent)].feature_generator_candidates = t_generator
        
        return updadet_triadic_concept

    def compute_f_generators_candidates(triadic_concepts, links, compute_minimality_for_infimum):

        def compute_f_generators_supremum(triadic_concepts):
            triadic_concepts = sorted(
                triadic_concepts, key=lambda x: x.extent_size, reverse=False)
            G = []
            supremum = triadic_concepts[-1].extent
            current_concept = triadic_concepts[triadic_concepts.index(
                set(supremum))]
            target_intent = current_concept.intent
            target_modus = current_concept.modus
            context = TriadicConcept.getContext_K1K2(
                target_intent, target_modus)
            for i, row in context.iterrows():
                for j, column in row.items():
                    if i != "ø" and j != "ø":
                        _intent = "".join([i for i in i])
                        _modus = "".join([j for j in j])
                        try:
                            if column:
                                if [_intent, _modus] not in G:
                                    G.append([_intent, _modus])
                        except:
                            raise
            updated_triadic_concept = triadic_concepts[triadic_concepts.index(
                supremum)].feature_generator_candidates = G
            return updated_triadic_concept

        updated_triadic_concepts = []
        links_dict = TriadicConcept.list_of_links_to_dict(links)
        ext_uniques = list(links_dict.keys())
        if not compute_minimality_for_infimum:
            ext_uniques = list(links_dict.keys())
            if EMPTY_SET in ext_uniques:
                ext_uniques.remove(EMPTY_SET)
                
        pool = ThreadPool(PROCESSES)
        for result in pool.starmap(TriadicConcept.f_generator, zip(ext_uniques, repeat(
                links_dict), repeat(triadic_concepts))):
            updated_triadic_concepts.append(result)
        pool.close()
        for concept in updated_triadic_concepts:
            triadic_concepts[triadic_concepts.index(
                set([x for x in concept.keys()][0]))].feature_generator_candidates = [*concept.values()][0]

        compute_f_generators_supremum(triadic_concepts)

        return triadic_concepts

    def compute_formal_context(triadic_concepts):
        formal_context = Definition()
        for concept in triadic_concepts:
            extent = [x for x in concept.extent]
            intent = [x for x in concept.intent]
            modus = [x for x in concept.modus]
            permutation = [(x, y) for x, y in zip(intent, modus)]
            if extent != []:
                for combination in permutation:
                    adds = [(e, i, m) for e in extent for i in combination[0]
                            for m in combination[1]]
                    for to_add in adds:
                        _extent, _intent, _modus = to_add
                        if _intent != 'ø' and _modus != 'ø':
                            formal_context.add_object(
                                str(_extent), [(str(_intent) + " " + str(_modus))])

        return Context(*formal_context)

    def validade_feature_generator_candidates(concept_extent, triadic_concepts, formal_context):
        
        final_t_generator = []
        f_gens = triadic_concepts[triadic_concepts.index(
                set(concept_extent))].feature_generator_candidates
        
        def attributes_in_properties(attributes, formal_context):
                for attribute in attributes:
                    if attribute not in formal_context.properties:
                        return False
                return True
        
        def check_if_generator_belongs_to_extent(extent, generator, formal_context):
            if not attributes_in_properties(generator, formal_context):
                return False
            extent_check = set(formal_context.extension(generator))
            if extent_check != extent:
                return False
            else:
                return True
            
        for generator in f_gens:
            to_check = []
            to_add = []
            if isinstance(generator[0],str) and isinstance(generator[1],str):
                to_check = [generator[0] + " " + generator[1]]
                if check_if_generator_belongs_to_extent(concept_extent, to_check, formal_context) and generator not in final_t_generator:
                    final_t_generator.extend([generator])
            else:
                to_check = []
                for intent in generator[0]:
                    for modus in generator[1]:
                        to_check.extend([intent + " " + modus])
                if check_if_generator_belongs_to_extent(concept_extent, to_check, formal_context) and generator not in final_t_generator:
                            final_t_generator.extend([generator])
        
        updadet_triadic_concept = triadic_concepts[triadic_concepts.index(
            concept_extent)].feature_generator = final_t_generator
        
        return concept_extent, updadet_triadic_concept
    
    def compute_minimality_feature_generators(concept_extent, triadic_concepts):
        f_gens = triadic_concepts[triadic_concepts.index(
                set(concept_extent))].feature_generator
        f_gens_to_check = f_gens[::-1].copy()
        f_gens_final = f_gens.copy()
        
        def cast_to_list(item):
            if isinstance(item, str):
                return [item]
            return item
        
        while len(f_gens_to_check) != 0:
            generator_to_check = f_gens_to_check.pop()
            for generator in f_gens:
                if generator != generator_to_check and generator in f_gens_final and generator_to_check in f_gens_final:
                    intent_gen, modus_gen = generator
                    intent_gen_check, modus_gen_check = generator_to_check
                    
                    intent_gen = cast_to_list(intent_gen)
                    modus_gen = cast_to_list(modus_gen)
                    intent_gen_check = cast_to_list(intent_gen_check)
                    modus_gen_check = cast_to_list(modus_gen_check)
                
                    if set(intent_gen_check).issubset(set(intent_gen)) and set(modus_gen_check).issubset(set(modus_gen)):
                        if generator in f_gens_final:
                            f_gens_final.remove(generator)
        
        updadet_triadic_concept = triadic_concepts[triadic_concepts.index(
            concept_extent)].feature_generator_minimal = f_gens_final
        
        return concept_extent, updadet_triadic_concept
    
    def compute_feature_generator_validation(triadic_concepts, formal_context):
        
        ext_uniques = [concept.extent for concept in triadic_concepts]
        
        pool = ThreadPool(PROCESSES)
        for result in pool.starmap(TriadicConcept.validade_feature_generator_candidates, zip(ext_uniques, repeat(triadic_concepts), repeat(formal_context))):
            triadic_concepts[triadic_concepts.index(set(result[0]))].feature_generator = result[1]
        pool.close()
        
        pool = ThreadPool(PROCESSES)
        for result in pool.starmap(TriadicConcept.compute_minimality_feature_generators, zip(ext_uniques, repeat(triadic_concepts))):
            triadic_concepts[triadic_concepts.index(set(result[0]))].feature_generator_minimal = result[1]
        pool.close()
        
        return triadic_concepts
    
    def compute_BCAI_implications(triadic_concepts):
        all_BCAI_implications = []
        _max_cardinality = max(concept.extent_size for concept in triadic_concepts)
        
        def cast_to_list(item):
            if isinstance(item, str):
                return [item]
            return item
        
        for concept in triadic_concepts:
            rules = []
            extent, intent, modus = concept.extent, concept.intent, concept.modus
            intent = cast_to_list(intent)
            modus = cast_to_list(modus)
            for generator in concept.feature_generator_minimal:
                intent_generator, modus_generator = generator[0], generator[1]
                intent_generator = cast_to_list(intent_generator)
                modus_generator = cast_to_list(modus_generator)
                
                concept_intent_modus = zip(intent, modus)
                concept_intent_modus = sorted(concept_intent_modus, key=lambda x: (len(x[0])), reverse=True)
                for item in concept_intent_modus:
                    _intent, _modus = item
                    if set(intent_generator).issubset(set(_intent)) and set(modus_generator).issubset(set(_modus)):
                        implication = set(_intent) - set(intent_generator)
                        if implication != EMPTY_SET:
                            implication = list(implication)
                            support = concept.extent_size / _max_cardinality
                            rule = [intent_generator, implication, modus_generator, [support]]
                            if rule not in rules:
                                rules.append(rule)
                                all_BCAI_implications.append(rule)
            
            triadic_concepts[triadic_concepts.index(
            extent)].BCAI_implications = rules
                
        return triadic_concepts, all_BCAI_implications
    
    def compute_BACI_implications(triadic_concepts):
        
        all_BACI_implications = []
        _max_cardinality = max(concept.extent_size for concept in triadic_concepts)
        
        def cast_to_list(item):
            if isinstance(item, str):
                return [item]
            return item
        
        for concept in triadic_concepts:
            rules = []
            extent, intent, modus = concept.extent, concept.intent, concept.modus
            intent = cast_to_list(intent)
            modus = cast_to_list(modus)
            for generator in concept.feature_generator_minimal:
                intent_generator, modus_generator = generator[0], generator[1]
                intent_generator = cast_to_list(intent_generator)
                modus_generator = cast_to_list(modus_generator)
                
                concept_intent_modus = zip(intent, modus)
                concept_intent_modus = sorted(concept_intent_modus, key=lambda x: (len(x[1])), reverse=True)
                for item in concept_intent_modus:
                    _intent, _modus = item
                    if set(intent_generator).issubset(set(_intent)) and set(modus_generator).issubset(set(_modus)):
                        implication = set(_modus) - set(modus_generator)
                        if implication != EMPTY_SET:
                            implication = list(implication)
                            support = concept.extent_size / _max_cardinality
                            rule = [modus_generator, implication, intent_generator, [support]]
                            if rule not in rules:
                                rules.append(rule)
                                all_BACI_implications.append(rule)
            
            triadic_concepts[triadic_concepts.index(
            extent)].BACI_implications = rules
                
        return triadic_concepts, all_BACI_implications
    
    def compute_BCAAR_association_rules(triadic_concepts, links):
        
        _max_cardinality = max(concept.extent_size for concept in triadic_concepts)
        all_rules_BCAAR = []
        
        def cast_to_list(item):
            if isinstance(item, str):
                return [item]
            return item
        
        for link in links:
            rules_BCAAR = []
            target_A1, source_B1 = link
            generators_A1 = triadic_concepts[triadic_concepts.index(
                set(target_A1))].feature_generator_minimal
            for generator in generators_A1:
                U2 = generator[0]
                U3 = generator[1]
                U2 = cast_to_list(U2)
                U3 = cast_to_list(U3)
                
                list_pair_Intent_Modus_A2_A3 = []
                list_pair_Intent_Modus_B2_B3 = []
                
                source_concept = triadic_concepts[triadic_concepts.index(
                set(source_B1))].extent
                source_intent_B2 = triadic_concepts[triadic_concepts.index(
                set(source_B1))].intent
                source_modus_B3 = triadic_concepts[triadic_concepts.index(
                set(source_B1))].modus
                
                target_concept = triadic_concepts[triadic_concepts.index(
                set(target_A1))].extent
                target_intent_A2 = triadic_concepts[triadic_concepts.index(
                set(target_A1))].intent
                target_modus_A3 = triadic_concepts[triadic_concepts.index(
                set(target_A1))].modus
                pair_Intent_Modus_B2_B3 = zip(source_intent_B2, source_modus_B3)
                pair_Intent_Modus_A2_A3 = zip(target_intent_A2, target_modus_A3)
                pair_Intent_Modus_B2_B3 = sorted(
                    pair_Intent_Modus_B2_B3, key=lambda x: (len(x[0])), reverse=True)
                pair_Intent_Modus_A2_A3 = sorted(
                    pair_Intent_Modus_A2_A3, key=lambda x: (len(x[0])), reverse=True)
                
                if list_pair_Intent_Modus_A2_A3 == []:
                    for item in pair_Intent_Modus_A2_A3:
                        if list_pair_Intent_Modus_A2_A3 == [] and set(U2).issubset(set(item[0])) and set(U3).issubset(set(item[1])):
                            list_pair_Intent_Modus_A2_A3.append(item)
                        else:
                            if list_pair_Intent_Modus_A2_A3 != []:
                                size_item_A = len(
                                    list_pair_Intent_Modus_A2_A3[0][0])
                                if size_item_A == len(item[0]) and set(U2).issubset(set(item[0])) and set(U3).issubset(set(item[1])):
                                    list_pair_Intent_Modus_A2_A3.append(item)
                                elif size_item_A > len(item[0]):
                                    break
                if list_pair_Intent_Modus_B2_B3 == []:
                    for item in pair_Intent_Modus_B2_B3:
                        if list_pair_Intent_Modus_B2_B3 == [] and set(U2).issubset(set(item[0])) and set(U3).issubset(set(item[1])):
                            list_pair_Intent_Modus_B2_B3.append(item)
                        else:
                            if list_pair_Intent_Modus_B2_B3 != []:
                                size_item_B = len(
                                    list_pair_Intent_Modus_B2_B3[0][0])
                                if size_item_B == len(item[0]) and set(U2).issubset(set(item[0])) and set(U3).issubset(set(item[1])):
                                    list_pair_Intent_Modus_B2_B3.append(item)
                                elif size_item_B > len(item[0]):
                                    break
                
                for pair_Intent_Modus_A2_A3 in list_pair_Intent_Modus_A2_A3:
                    
                    target_intent_A2, target_modus_A3 = pair_Intent_Modus_A2_A3
                    target_intent_A2 = cast_to_list(target_intent_A2)
                    target_modus_A3 = cast_to_list(target_modus_A3)

                    for pair_Intent_Modus_B2_B3 in list_pair_Intent_Modus_B2_B3:
                        source_intent_B2, source_modus_B3 = pair_Intent_Modus_B2_B3
                        
                        source_intent_B2 = cast_to_list(source_intent_B2)
                        source_modus_B3 = cast_to_list(source_modus_B3)
                        
                        # IF STATMENT FOR BCAAR RULES
                        if ((set(target_intent_A2).issubset(set(source_intent_B2)) and set(source_modus_B3).issubset(set(target_modus_A3))) and (set(U2).issubset(set(source_intent_B2)) and set(U3).issubset(set(source_modus_B3)))):
                            
                            support = len(source_B1) / _max_cardinality
                            confidence = len(source_B1) / len(target_A1)
                            
                            if set(source_intent_B2)-set(target_intent_A2) != EMPTY_SET:
                                rule = [list(U2), list(
                                        set(set(source_intent_B2)-set(target_intent_A2))), list(U3), support, confidence, [source_concept, target_concept]]
                                if rule not in rules_BCAAR:
                                    rules_BCAAR.append(rule)
                                    all_rules_BCAAR.append(rule)
        
            triadic_concepts[triadic_concepts.index(
            source_concept)].BCAAR_associarion_rules = rules_BCAAR
        
        return triadic_concepts, all_rules_BCAAR
    
    def compute_BACAR_association_rules(triadic_concepts, links):
        
        _max_cardinality = max(concept.extent_size for concept in triadic_concepts)
        all_rules_BACAR = []
        
        def cast_to_list(item):
            if isinstance(item, str):
                return [item]
            return item
        
        for link in links:
            
            rules_BACAR = []
            target_A1, source_B1 = link
            generators_A1 = triadic_concepts[triadic_concepts.index(
                set(target_A1))].feature_generator_minimal
            for generator in generators_A1:
                U2 = generator[0]
                U3 = generator[1]
                U2 = cast_to_list(U2)
                U3 = cast_to_list(U3)
                
                list_pair_Intent_Modus_A2_A3 = []
                list_pair_Intent_Modus_B2_B3 = []
                
                source_concept = triadic_concepts[triadic_concepts.index(
                set(source_B1))].extent
                source_intent_B2 = triadic_concepts[triadic_concepts.index(
                set(source_B1))].intent
                source_modus_B3 = triadic_concepts[triadic_concepts.index(
                set(source_B1))].modus
                target_concept = triadic_concepts[triadic_concepts.index(
                set(target_A1))].extent
                target_intent_A2 = triadic_concepts[triadic_concepts.index(
                set(target_A1))].intent
                target_modus_A3 = triadic_concepts[triadic_concepts.index(
                set(target_A1))].modus
                
                pair_Intent_Modus_B2_B3 = zip(source_intent_B2, source_modus_B3)
                pair_Intent_Modus_A2_A3 = zip(target_intent_A2, target_modus_A3)
                
                pair_Intent_Modus_B2_B3 = sorted(
                    pair_Intent_Modus_B2_B3, key=lambda x: (len(x[1])), reverse=True)
                pair_Intent_Modus_A2_A3 = sorted(
                    pair_Intent_Modus_A2_A3, key=lambda x: (len(x[1])), reverse=True)
                
                if list_pair_Intent_Modus_A2_A3 == []:
                    for item in pair_Intent_Modus_A2_A3:
                        if list_pair_Intent_Modus_A2_A3 == [] and set(U2).issubset(set(item[0])) and set(U3).issubset(set(item[1])):
                            list_pair_Intent_Modus_A2_A3.append(item)
                        else:
                            if list_pair_Intent_Modus_A2_A3 != []:
                                size_item_A = len(
                                    list_pair_Intent_Modus_A2_A3[0][1])
                                if size_item_A == len(item[1]) and set(U2).issubset(set(item[0])) and set(U3).issubset(set(item[1])):
                                    list_pair_Intent_Modus_A2_A3.append(item)
                                elif size_item_A > len(item[1]):
                                    break
                if list_pair_Intent_Modus_B2_B3 == []:
                    for item in pair_Intent_Modus_B2_B3:
                        if list_pair_Intent_Modus_B2_B3 == [] and set(U2).issubset(set(item[0])) and set(U3).issubset(set(item[1])):
                            list_pair_Intent_Modus_B2_B3.append(item)
                        else:
                            if list_pair_Intent_Modus_B2_B3 != []:
                                size_item_B = len(
                                    list_pair_Intent_Modus_B2_B3[0][1])
                                if size_item_B == len(item[1]) and set(U2).issubset(set(item[0])) and set(U3).issubset(set(item[1])):
                                    list_pair_Intent_Modus_B2_B3.append(item)
                                elif size_item_B > len(item[1]):
                                    break
                
                for pair_Intent_Modus_A2_A3 in list_pair_Intent_Modus_A2_A3:
                    
                    target_intent_A2, target_modus_A3 = pair_Intent_Modus_A2_A3
                    target_intent_A2 = cast_to_list(target_intent_A2)
                    target_modus_A3 = cast_to_list(target_modus_A3)

                    for pair_Intent_Modus_B2_B3 in list_pair_Intent_Modus_B2_B3:
                        source_intent_B2, source_modus_B3 = pair_Intent_Modus_B2_B3
                        
                        source_intent_B2 = cast_to_list(source_intent_B2)
                        source_modus_B3 = cast_to_list(source_modus_B3)
                        
                        # IF STATMENT FOR BACAR RULES
                        if ((set(target_modus_A3).issubset(set(source_modus_B3)) and set(source_intent_B2).issubset(set(target_intent_A2))) and (set(U3).issubset(set(source_modus_B3)) and set(U2).issubset(set(source_intent_B2)))):
                            
                            support = len(source_B1) / _max_cardinality
                            confidence = len(source_B1) / len(target_A1)
                            
                            if set(source_modus_B3)-set(target_modus_A3) != EMPTY_SET:
                                
                                rule = [list(U3), list(set(source_modus_B3)-set(target_modus_A3)), list(U2), support, confidence, [source_concept, target_concept]]
                                
                                if rule not in rules_BACAR:
                                    rules_BACAR.append(rule)
                                    all_rules_BACAR.append(rule)
                                    
            triadic_concepts[triadic_concepts.index(
            source_concept)].BACAR_associarion_rules = rules_BACAR
        

        return triadic_concepts, all_rules_BACAR