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
    feature_generator_candidates: list[list] = field(default_factory=list)
    
    def __post_init__(self):
        self.sort_index = self.extent_size

    def __str__(self):
        return f'Extent: {self.extent}\nIntent: {self.intent}\nModus: {self.modus}\nExtent size: {self.extent_size}\nFeature Generators Candidates: {self.feature_generator_candidates}\nFeature Generators: {self.feature_generator}'

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
        border_max = 0
        # border <- the very first element with the smallest EXTENT cardinality
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
        # CREATING THE CONTEXT (K1,K2xK3,Y) FOR EACH CONCEPT EXTENT

        # print(" - K1K2 FUNCTION"*10)
        # print("INTENT: ", intent)
        # print("MODUS: ", modus)
        intent = [list(x) for x in intent]
        modus = [list(x) for x in modus]
        # print("INTENT: ", intent)
        # print("MODUS: ", modus)
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
            # print(context)
            for intent_item, modus_item in zip(intent, modus):
                context.loc[intent_item, modus_item] = True
        # print(context)
        return context

    def f_generator(key, links_dict, triadic_concepts):

        def compute_face_kth_successor(target_intent, target_modus):
            for intent_item, modus_item in zip(target_intent, target_modus):
                for x in intent_item:
                    for y in modus_item:
                        # print("TO REMOVE INCIDENCE: ", x, y)
                        try:
                            if str(y) in context.columns and str(x) in context.index:
                                context.loc[x, y] = False
                                # print("INCIDENCE REMOVED")
                                # print(context)
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

        val = links_dict[key]

        for value in val:
            target = frozenset(value)
            source = frozenset(key)
            # print(triadic_concepts)
            current_concept = triadic_concepts[triadic_concepts.index(
                set(source))]
            successor_concept = triadic_concepts[triadic_concepts.index(
                set(target))]
            current_concept_extent = triadic_concepts[triadic_concepts.index(
                set(source))].extent
            # current_concept = data_unique.loc[data_unique['Extent'] == set(source)]
            # successor_concept = data_unique.loc[data_unique['Extent'] == set(target)]

            if source not in feature_generator:
                source_intent = current_concept.intent
                source_modus = current_concept.modus
                target_intent = successor_concept.intent
                target_modus = successor_concept.modus
                # print(" - INSIDE FUNCTION")
                # print("SOURCE TC: ", source, source_intent, source_modus)
                # print("TARGET TC: ", target, target_intent, target_modus)
                context = TriadicConcept.getContext_K1K2(
                    source_intent, source_modus)
                # print("CONTEXT K1K2 CREATED: ")
                # print(context)

                # COMPUTING THE FACE OF A CONCEPT W.R.T. THE K-TH SUCCESSOR
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
                # print(" - INSIDE FUNCTION ELSE")
                # print("SOURCE TC: ", source, source_intent, source_modus)
                # print("TARGET TC: ", target, target_intent, target_modus)
                context = TriadicConcept.getContext_K1K2(
                    source_intent, source_modus)
                target_intent = successor_concept.intent
                target_modus = successor_concept.modus
                G = t_generator[source]

                # COMPUTING THE FACE OF A CONCEPT W.R.T. THE K-TH SUCCESSOR
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
            # print("CONTEXT K1K2 UPDATED: ")
            # print(context)
            feature_generator.update({source: context})
            context = pd.DataFrame()
            G = []
            G1 = []
            F = []
            U3 = []

        # print("RES" *100)
        #     print("\nSOURCE: ", source, source_intent, source_modus)
        #     print("TARGET: ", target, target_intent, target_modus)
        #     print("t_generator: ")
        #     print(t_generator[source])
        # print("-"*15)
        # for k, v in t_generator.items():
        #     print(k)
        #     print(v)
        #     print()
        # for k, v in feature_generator.items():
        #     print(k)
        #     print(v)
        #     print()
        # print("#"*50)
        # current_concept.feature_generator = t_generator[source]
        # return source, t_generator[source]
        # print("TRIADIC CONCEPT: ", current_concept)
        # print("t_generator KEYS SIZE: ", len(t_generator.keys()))
        # print("t_generator VALUES SIZE: ", len(t_generator.values()))
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
