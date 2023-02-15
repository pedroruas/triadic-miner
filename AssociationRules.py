# -*- coding: utf-8 -*-
"""
@author: pedroruas
"""

from tqdm import tqdm
from dataclasses import dataclass, field

EMPTY_SET = set([])

@dataclass(slots=True, order=True)
class AssociationRule:
    """Class that represents a association rule (including implications).
        The folowing rules are beeing computed:
            - Biedermann Conditional Attribute Association Rule (BCAAR)
            - Biedermann Attributional Condition Association Rule (BACAR)
            - Biedermann Conditional Attribute Implication (BCAI)
            - Biedermann Attributional Condition Implication (BACI)
    """
    antecedent: list[list] = field(default_factory=list)
    consequent: list[list] = field(default_factory=list)
    condition: list[list] = field(default_factory=list)
    support: float = field(default_factory=float)
    confidence: float = field(default_factory=float)
    current_concept_extent: set = field(default_factory=set)
    predecessor_concept_extent: set = field(default_factory=set)
    
    
    def __str__(self):
        antecedent = str(', '.join([', '.join(x for x in sorted(self.antecedent))]))
        consequent = str(', '.join([', '.join(x for x in sorted(self.consequent))]))
        condition = str(', '.join([', '.join(x for x in sorted(self.condition))]))
        current_concept_extent = str(', '.join([', '.join(x for x in sorted(self.current_concept_extent))]))
        predecessor_concept_extent = self.predecessor_concept_extent
        if predecessor_concept_extent != None:
            predecessor_concept_extent = str(', '.join([', '.join(x for x in sorted(self.predecessor_concept_extent))]))
        
        return f'({antecedent} -> {consequent}) {condition}\t(sup: {self.support}, conf: {self.confidence})\nConcept extent: {current_concept_extent}\nPredecessor concept: {predecessor_concept_extent}'
    
    def compute_BCAI_implications(triadic_concepts):
        
        BCAI_implications = []
        _max_cardinality = max(concept.extent_size for concept in triadic_concepts)
        
        def cast_to_list(item):
            if isinstance(item, str):
                return [item]
            return item
        
        for concept in tqdm(triadic_concepts):
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
                            rule = AssociationRule(antecedent= intent_generator,
                                                   consequent= implication,
                                                   condition= modus_generator,
                                                   support= support,
                                                   confidence= 1.0,
                                                   current_concept_extent=extent,
                                                   predecessor_concept_extent=None)
                            if rule not in BCAI_implications:
                                BCAI_implications.append(rule)
            
        return BCAI_implications
    
    def compute_BACI_implications(triadic_concepts):
        
        BACI_implications = []
        _max_cardinality = max(concept.extent_size for concept in triadic_concepts)
        
        def cast_to_list(item):
            if isinstance(item, str):
                return [item]
            return item
        
        for concept in tqdm(triadic_concepts):
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
                            rule = AssociationRule(antecedent= modus_generator,
                                                   consequent= implication,
                                                   condition= intent_generator,
                                                   support= support,
                                                   confidence= 1.0,
                                                   current_concept_extent=extent,
                                                   predecessor_concept_extent=None)
                            if rule not in BACI_implications:
                                BACI_implications.append(rule)
                
        return BACI_implications
    
    def compute_BCAAR_association_rules(triadic_concepts, links):
        
        _max_cardinality = max(concept.extent_size for concept in triadic_concepts)
        rules_BCAAR = []
        
        def cast_to_list(item):
            if isinstance(item, str):
                return [item]
            return item
        
        for link in tqdm(links):
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
                        
                        if ((set(target_intent_A2).issubset(set(source_intent_B2)) and set(source_modus_B3).issubset(set(target_modus_A3))) and (set(U2).issubset(set(source_intent_B2)) and set(U3).issubset(set(source_modus_B3)))):
                            
                            support = len(source_B1) / _max_cardinality
                            confidence = len(source_B1) / len(target_A1)
                            
                            if set(source_intent_B2)-set(target_intent_A2) != EMPTY_SET:
                                rule = AssociationRule(antecedent= source_intent_B2,
                                                   consequent= target_intent_A2,
                                                   condition= list(U3),
                                                   support= support,
                                                   confidence= confidence,
                                                   current_concept_extent=source_concept,
                                                   predecessor_concept_extent=target_concept)
                                if rule not in rules_BCAAR:
                                    rules_BCAAR.append(rule)
        
        return rules_BCAAR
    
    def compute_BACAR_association_rules(triadic_concepts, links):
        
        _max_cardinality = max(concept.extent_size for concept in triadic_concepts)
        rules_BACAR = []
        
        def cast_to_list(item):
            if isinstance(item, str):
                return [item]
            return item
        
        for link in tqdm(links):

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
                        
                        if ((set(target_modus_A3).issubset(set(source_modus_B3)) and set(source_intent_B2).issubset(set(target_intent_A2))) and (set(U3).issubset(set(source_modus_B3)) and set(U2).issubset(set(source_intent_B2)))):
                            
                            support = len(source_B1) / _max_cardinality
                            confidence = len(source_B1) / len(target_A1)
                            
                            if set(source_modus_B3)-set(target_modus_A3) != EMPTY_SET:
                                
                                rule = AssociationRule(antecedent= source_intent_B2,
                                                   consequent= target_intent_A2,
                                                   condition= list(U3),
                                                   support= support,
                                                   confidence= confidence,
                                                   current_concept_extent=source_concept,
                                                   predecessor_concept_extent=target_concept)
                                if rule not in rules_BACAR:
                                    rules_BACAR.append(rule)
        
        return rules_BACAR