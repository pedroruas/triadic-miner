# -*- coding: utf-8 -*-
"""
@author: pedroruas
"""

from tqdm import tqdm
import pandas as pd
from dataclasses import dataclass, field
from multiprocessing.pool import ThreadPool
from itertools import repeat
from concepts import Definition, Context
import pyyed
from itertools import chain, combinations


EMPTY_SET = set([])
PROCESSES = 8  # Amount of threads to be used in multithreading


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
    extensional_generator_candidates: list[list] = field(default_factory=list)
    extensional_generator_minimal: list[list] = field(default_factory=list)
    concept_stability: list[list] = field(default_factory=list)
    separation_index: list[list] = field(default_factory=list)
    triadic_relevance_index: list[list] = field(default_factory=list)

    def __post_init__(self):
        self.sort_index = self.extent_size

    def __str__(self):

        return f"Extent: {self.extent}\
                \nIntent: {self.intent}\
                \nModus: {self.modus}\
                \nExtent size: {self.extent_size}\
                \nFeature Generators Candidates:{self.feature_generator_candidates}\
                \nFeature Generators: {self.feature_generator}\
                \nFeature Generators Minimal: {self.feature_generator_minimal}\
                \nExtensional Generator Candidates: {self.extensional_generator_candidates}\
                \nExtensional Generator Minimal: {self.extensional_generator_minimal}\
                \nConcept Stability: {self.concept_stability}\
                \nSeparation Index: {self.separation_index}\
                \nTriadic Relevance Index: {self.triadic_relevance_index}"

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
        return sorted(unique_triadic_concepts,
                      key=lambda x: x.extent_size,
                      reverse=False)

    def create_triadic_concepts_faces(triadic_concepts):
        """Takes the list of TriadicConcepts and returns the initialized Faces
        and the the set of all unique extents

        Args:
            triadic_concepts (list): list of objects of the class
            TriadicConcept

        Returns:
            faces (dict): is a dictionary with the initial faces of each
            unique extents
            all_extents (set): is a set with all the unique extents
        """

        faces = {}
        all_extents = set()
        for concept in triadic_concepts:
            faces.update({frozenset(concept.extent): set({})})
            all_extents = all_extents | set({frozenset(concept.extent)})

        return faces, all_extents

    def T_iPred(triadic_concepts, faces, all_extents):
        """Takes the list of triadic concepts, the initial Faces and the
        unique extents of triadic concepts and calculates the links between
        triadic concepts.

        Args:
                triadic_concepts (list): list of TriadicConcept objects
                faces (dict): initial data structure to calculate the Faces
                all_extents (set): a set with all unique extents in
                triadic_concepts

        Returns:
                links (list): returns a list with the links between
                Triadic Concepts
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
        """Takes the links between all the concepts and returns a dict with
        all the successors associated with each Triadic Concept extent.

        Args:
            links (list): list with the links between Triadic Concepts

        Returns:
            links_dic (dict): returns a dict where an extent is the key,
            and the values are the successors' extent
        """

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
        """Takes the intent and the modus associated with a Triadic Concept
        and creates a formal context using a pandas Dataframe to represent it.

        Args:
            intent (list): list of intents associated with a Triadic Concept
            modus (list): list of modus associated with a Triadic Concept

        Returns:
            context (pandas Dataframe): returns a Dataframe annotated
            with the incidences (boolean)
        """

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
        """Takes the concept, links_dict and triadic_concepts to compute the
        Feature Generators Candidates for all Triadic Concepts extent in the
        list triadic_concepts.
        This function is executed using a MapReduce approach
        based on multithreading.

        Args:
            concept (TriadicConcept): an object of the class TriadicConcept
            links_dict (dict): a dict where an extent is the key, and the
            values are the successors' extent
            triadic_concepts (list): list of all Triadic Concepts
        """

        def compute_face_kth_successor(target_intent, target_modus):
            """Takes the intent and modus part of a Triadic Concept that is a
            successor, and removes the shared features (by removing incidences
            from the context) from the current concept.

            Args:
                target_intent (list): list of intents associated with a
                Triadic Concept
                target_modus (list): list of modus associated with a
                Triadic Concept

            Returns:
                context (pandas Dataframe): returns the context after removing
                the features from its successor
            """

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

        updated_triadic_concept = triadic_concepts[triadic_concepts.index(
            current_concept_extent)].feature_generator_candidates = t_generator

        return updated_triadic_concept

    def compute_f_generators_candidates(triadic_concepts,
                                        links,
                                        compute_feature_generators_for_infimum):
        """Takes triadic_concepts, links and the parameter from the user
        compute_feature_generators_for_infimum to call the function
        'f_generators' to compute in parallel the Feature Generator Candidates.

        NOTE: the parameter 'compute_feature_generators_for_infimum' may have
        a great impact on the execution time, since the infimum usually has
        a empty set in its extent.

        Args:
            triadic_concepts (list): list of TriadicConcept objects
            links (list): list with the links between Triadic Concepts
            compute_feature_generators_for_infimum (boolean): parameter that
            the user can set in the input file (configs.json)

        Returns:
            triadic_concepts (list): updated list of TriadicConcept objects
            annotated with the Feature Generator Candidates
        """

        def compute_f_generators_supremum(triadic_concepts):
            """Takes the triadic_concepts, finds the supremum by ordering the
            concepts by the cardinality of the extents, and computes the
            Feature Generator Candidates for the supremum.
            The supremum has this special behavior because it does not have
            successors, so its Features Generator Candidates
            are created separately.

            Args:
                triadic_concepts (list): list of TriadicConcept objects

            Returns:
                triadic_concepts (list): updated list of TriadicConcept
                objects annotated with the Feature Generator Candidates
            """

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
        if not compute_feature_generators_for_infimum:
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
        """Takes the triadic_concepts and creates a Formal Context that
        represents all the Triadic Concepts.

        Args:
            triadic_concepts (list): list of TriadicConcept objects

        Returns:
            formal_context (concepts Context): returns the Formal Context
            representing all the Triadic Concepts
        """

        formal_context = Definition()
        for concept in tqdm(triadic_concepts):
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

    def validate_feature_generator_candidates(concept_extent,
                                              triadic_concepts,
                                              formal_context):
        """Takes the concept_extent, triadic_concepts and formal_context in
        order to validate if a Feature Generator Candidate is in fact
        associated with an extent. This is done by derivating a
        Feature Generator and checking if the result is the same as 
        the extent in 'concept_extent'.
        This function is executed in parallel using a multithreading approach.

        Args:
            concept_extent (set): extent of a TriadicConcept object
            triadic_concepts (list): list of TriadicConcept objects
            formal_context (concepts Context): the Formal Context representing
            all the Triadic Concepts

        Returns:
            concept_extent (set): the extent of a TriadicConcept object
            updated_triadic_concept (list): list of TriadicConcept objects
        """

        final_t_generator = []
        f_gens = triadic_concepts[triadic_concepts.index(
            set(concept_extent))].feature_generator_candidates

        def attributes_in_properties(attributes, formal_context):
            """Takes the attributes (intent x modus) and the formal_context
            in order to check if the attribute is in fact
            in the formal_context.

            Args:
                attributes (str): string representing the
                attribute (intent x modus)
                formal_context (concepts Context): the Formal Context
                representing all the Triadic Concepts

            Returns:
                bool: if the attribute exists in the formal_context,
                    returns True
            """

            for attribute in attributes:
                if attribute not in formal_context.properties:
                    return False
            return True

        def check_if_generator_belongs_to_extent(extent,
                                                 generator,
                                                 formal_context):
            """Takes the extent, generator, formal_context and check a
            Feature Generator is associated with an extent.
            Args:
                extent (set): the extent of a TriadicConcept
                generator (list): the pair of intent and modus of a
                Feature Generator
                formal_context (concepts Context): the Formal Context
                representing all the Triadic Concepts

            Returns:
                bool: returns True if the result of derivation operation gives
                the same extent as the extent passed as parameter
            """

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
            if isinstance(generator[0], str) and isinstance(generator[1], str):
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

        updated_triadic_concept = triadic_concepts[triadic_concepts.index(
            concept_extent)].feature_generator = final_t_generator

        return concept_extent, updated_triadic_concept

    def compute_minimality_feature_generators(concept_extent,
                                              triadic_concepts):
        """Takes the concept_extent and triadic_concepts to compute
        the minimality test on Feature Generators.
        Since we are interested in Minimal Feature generators,
        this function compares the compatible Generators and removes
        non Minimal Generators from the list associated with a Triadic Concept.

        Args:
            concept_extent (set): the extent of a TriadicConcept
            triadic_concepts (list): updated list of TriadicConcept objects
            annotated with the Feature Generator Candidates

        Returns:
            concept_extent (set): the extent of a TriadicConcept object
            updated_triadic_concept (list): updated list of
            TriadicConcept objects
        """

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

        updated_triadic_concept = triadic_concepts[triadic_concepts.index(
            concept_extent)].feature_generator_minimal = f_gens_final

        return concept_extent, updated_triadic_concept

    def compute_feature_generator_validation(triadic_concepts, formal_context):
        """Takes the triadic_concepts and formal_context to call the function
        the will validate the Feature Generator Candidates using a
        multithreading approach.

        Args:
            triadic_concepts (list): list of TriadicConcept objects
            formal_context (concepts Context): the Formal Context representing
            all the Triadic Concepts

        Returns:
            triadic_concepts (list): updated list of TriadicConcept objects
            annotated with the Minimal Feature Generators
        """

        ext_uniques = [concept.extent for concept in triadic_concepts]

        pool = ThreadPool(PROCESSES)
        for result in pool.starmap(
            TriadicConcept.validate_feature_generator_candidates,
            zip(ext_uniques, repeat(triadic_concepts),
                repeat(formal_context))):
            triadic_concepts[triadic_concepts.index(
                set(result[0]))].feature_generator = result[1]
        pool.close()

        pool = ThreadPool(PROCESSES)
        for result in pool.starmap(
                TriadicConcept.compute_minimality_feature_generators,
                zip(ext_uniques, repeat(triadic_concepts))):
            triadic_concepts[triadic_concepts.index(
                set(result[0]))].feature_generator_minimal = result[1]
        pool.close()

        return triadic_concepts

    def concept_stability_calculation(concept, triadic_concepts,
                                      formal_context):
        """Takes the concept, triadic_concepts and formal_context and computes
        the Concept Stability for each Triadic Concept. This is done by
        computing the powerset(extent). This function is executed in parallel
        using a multithreading approach.

        NOTE: since the powerset of the elements in the extent of all Triadic
        Concepts is computed, it has a great impact on the execution time when
        the input file gets bigger (large number of Triadic Concepts).

        Args:
            concept (TriadicConcept): an object of the class TriadicConcept
            triadic_concepts (list): list of TriadicConcept objects
            formal_context (concepts Context): the Formal Context representing
            all the Triadic Concepts

        Returns:
            list_concept_stability (list): returns the Concept Stability for
            each Triadic Concept object
        """

        def powerset(iterable):
            "list(powerset([1,2,3])) --> [(), (1,), (2,), (3,), (1,2), (1,3), (2,3), (1,2,3)] "
            s = list(iterable)
            return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

        context = Definition()
        list_concept_stability = []
        count_concept_stability = 0
        extent = triadic_concepts[triadic_concepts.index(concept)].extent
        intent = triadic_concepts[triadic_concepts.index(concept)].intent
        modus = triadic_concepts[triadic_concepts.index(concept)].modus
        extent = [x for x in extent]

        if extent != []:
            for item in zip(intent, modus):
                intent_item, modus_item = item
                if len(extent) == 1:
                    list_concept_stability.append(
                        [list(extent), intent_item, modus_item, 0.5])
                else:
                    powerset_ext = powerset(extent)
                    for ext in powerset_ext:
                        if list(ext) != []:
                            if len(ext) == 1:
                                intention = formal_context.intension(ext)
                                for element in list(intention):
                                    intent_part, modus_part = element.split()
                                    context.add_object(str(intent_part), [
                                        str(modus_part), ])
                            else:
                                intention = formal_context.intension(ext,)

                                # When the powerset of some EXTENT is computed,
                                # is it possible to create some combination of
                                # extents that does not have any shared
                                # feature.
                                # In this sense, this IF test will just skip
                                # these extents that doesn't share any feature.
                                if list(intention) == []:
                                    continue
                                for element in list(intention):
                                    intent_part, modus_part = element.split()
                                    context.add_object(str(intent_part), [
                                        str(modus_part), ])
                            _context = Context(*context)
                            lattice = _context.lattice
                            for intent_subset, modus_subset in lattice:
                                if set(list(intent_item)) == set(list(intent_subset)) and set(list(modus_item)) == set(list(modus_subset)):
                                    count_concept_stability += 1
                            context = Definition()
                    if list(ext) != []:
                        list_concept_stability.append(
                            [list(extent), intent_item, modus_item,
                             round(count_concept_stability/2**len(extent), 3)])
                    count_concept_stability = 0

        return list_concept_stability

    def compute_concept_stability(triadic_concepts, formal_context):
        """Takes triadic_concepts and formal_context to call the function
        'concept_stability_calculation' that will be executed in parallel.

        Args:
            triadic_concepts (list): list of TriadicConcept objects
            formal_context (concepts Context): the Formal Context representing
            all the Triadic Concepts

        Returns:
            triadic_concepts (list): list of TriadicConcept objects updated
            with Concept Stability 
        """

        ext_uniques = [concept.extent for concept in triadic_concepts]

        pool = ThreadPool(PROCESSES)
        list_concept_stability_final = pool.starmap(
            TriadicConcept.concept_stability_calculation,
            zip(ext_uniques, repeat(triadic_concepts), repeat(formal_context)))
        pool.close()

        for result in list_concept_stability_final:
            _extent = EMPTY_SET
            scores = []
            if result != []:
                for concept in result:
                    extent = frozenset(concept[0])
                    _extent = extent.copy()
                    intent = list(concept[1])
                    modus = list(concept[2])
                    concept_stability = concept[3]
                    scores.append([intent, modus, concept_stability])
            triadic_concepts[triadic_concepts.index(
                _extent)].concept_stability = scores

        return triadic_concepts

    def separation_index_calculation(triadic_concepts):
        """Takes the triadic_concepts and computes the Separation Index for
        all the Triadic Concepts in the list.

        Args:
            triadic_concepts (list): list of TriadicConcept objects

        Returns:
            triadic_concepts (list): list of TriadicConcept objects
            updated with Separation Index
        """

        sum_intent_modus = 0
        sum_intent_all_modus = 0
        sum_all_extent = 0
        size_A1 = 0
        size_A2 = 0
        size_A3 = 0
        list_separation_index = []
        list_appear_A2_A3 = []
        dic_count_extent = {}
        dic_count_intent_modus = {}
        list_appear_extent_intent_modus = []

        for concept in tqdm(triadic_concepts):
            extent = [x for x in concept.extent]
            intent, modus = concept.intent, concept.modus
            if extent != []:
                for element_extent in extent:
                    for item in zip(intent, modus):
                        intent_item, modus_item = item
                        for element_intent in intent_item:
                            for element_modus in modus_item:
                                if element_intent != 'ø' and element_modus != 'ø':

                                    if str(element_extent) not in dic_count_extent:
                                        dic_count_extent.update(
                                            {str(element_extent): 1})

                                    elif [[str(element_extent)], [str(element_intent)+" "+str(element_modus)]] not in list_appear_extent_intent_modus:
                                        count = dic_count_extent[str(
                                            element_extent)]
                                        count += 1
                                        dic_count_extent.update(
                                            {str(element_extent): count})

                                    if str(element_intent + " " + element_modus) not in dic_count_intent_modus:
                                        dic_count_intent_modus.update(
                                            {str(element_intent + " " + element_modus): 1})

                                    elif [[str(element_extent)], [str(element_intent)+" "+str(element_modus)]] not in list_appear_extent_intent_modus:
                                        count = dic_count_intent_modus[str(
                                            element_intent + " " + element_modus)]
                                        count += 1
                                        dic_count_intent_modus.update(
                                            {str(element_intent + " " + element_modus): count})

                                    list_appear_extent_intent_modus.append(
                                        [[str(element_extent)], [str(element_intent)+" "+str(element_modus)]])

        for concept in tqdm(triadic_concepts):
            extent = [x for x in concept.extent]
            intent, modus = concept.intent, concept.modus
            if extent != []:
                for element_extent in extent:
                    size_A1 += 1
                    sum_all_extent += dic_count_extent[element_extent]
                for item in zip(intent, modus):
                    intent_item, modus_item = item

                    if str(extent)+" " + str(intent_item) + " " + str(modus_item) not in list_appear_A2_A3:
                        size_A2 += len(intent_item)
                        size_A3 += len(modus_item)
                        list_appear_A2_A3.append(
                            str(extent)+" " + str(intent_item) + " " + str(modus_item))

                    for element_intent in intent_item:
                        for element_modus in modus_item:
                            if element_intent != 'ø' and element_modus != 'ø':

                                sum_intent_all_modus += dic_count_intent_modus[str(
                                    element_intent + " " + element_modus)]

                        sum_intent_modus += sum_intent_all_modus
                        sum_intent_all_modus = 0

                    if element_intent != 'ø' and element_modus != 'ø':
                        try:
                            separation_value = (size_A1 * size_A2 * size_A3) / (
                                (sum_all_extent + sum_intent_modus) - (size_A1 * size_A2 * size_A3))
                        except ZeroDivisionError:
                            separation_value = 0
                        list_separation_index.append(
                            [(extent), (intent_item), (modus_item), separation_value])

                    separation_value = 0
                    sum_intent_modus = 0
                    size_A2 = 0
                    size_A3 = 0

                sum_all_extent = 0
                size_A1 = 0

        for result in list_separation_index:
            if result != []:
                extent = frozenset(result[0])
                intent = list(result[1])
                modus = list(result[2])
                separation_index = result[3]
                triadic_concepts[triadic_concepts.index(extent)].separation_index.append([
                    intent, modus, round(separation_index, 3)])

        return triadic_concepts

    def compute_extensional_generators(triadic_concepts, links):
        """Takes the triadic_concepts and links to compute
        Extensional Generators. These generators will be further
        used to compute Extensional Implications.

        Args:
            triadic_concepts (list): list of TriadicConcept objects
            links (list): list with the links between Triadic Concepts

        Returns:
            triadic_concepts (list): list of TriadicConcept objects
            updated with Extensional Generators
        """

        def find_minimal_extensional_generators(triadic_concepts):
            """Takes the triadic_concepts and tests for each
            Extensional Generator Candidate whether they are
            Minimal or not. It also checks for redundant generators.

            Args:
                triadic_concepts (list): list of TriadicConcept objects
            """

            all_extents = [x.extent for x in triadic_concepts]
            to_remove = EMPTY_SET

            for extent in all_extents:
                triadic_concepts[triadic_concepts.index(
                    extent)].extensional_generator_minimal = triadic_concepts[triadic_concepts.index(
                        extent)].extensional_generator_candidates

            for concept in reversed(triadic_concepts):
                extensional_generators = triadic_concepts[triadic_concepts.index(
                    concept.extent)].extensional_generator_minimal

                for element in extensional_generators:
                    if set(element) in all_extents:
                        if len(element) > 1:
                            to_remove = frozenset({element})
                        else:
                            to_remove = set(element)
                        new_gen = extensional_generators - to_remove
                        triadic_concepts[triadic_concepts.index(
                            concept.extent)].extensional_generator_minimal = new_gen
                        to_remove = EMPTY_SET

                for element in extensional_generators:
                    check = triadic_concepts[triadic_concepts.index(
                        concept.extent)].extensional_generator_minimal
                    check = check - frozenset({element})
                    for gen in check:
                        if frozenset(element).issubset(frozenset(gen)):
                            to_remove = frozenset({gen})
                            new_gen = extensional_generators - to_remove
                            triadic_concepts[triadic_concepts.index(
                                concept.extent)].extensional_generator_minimal = new_gen
                        to_remove = EMPTY_SET

            for concept in reversed(triadic_concepts):
                if concept.extensional_generator_minimal == EMPTY_SET:
                    triadic_concepts[triadic_concepts.index(
                        concept.extent)].extensional_generator_minimal = concept.extent

        for link in reversed(links):
            current_node = link[0]
            successor_node = link[1]
            extensional_generators = triadic_concepts[triadic_concepts.index(
                current_node)].extensional_generator_candidates

            if extensional_generators == []:
                face_current_node = current_node - successor_node
                E_gen = set(face_current_node)
                triadic_concepts[triadic_concepts.index(
                    current_node)].extensional_generator_candidates = E_gen
            else:
                face_current_node = current_node - successor_node
                E_gen = triadic_concepts[triadic_concepts.index(
                    current_node)].extensional_generator_candidates
                for generator in triadic_concepts[triadic_concepts.index(current_node)].extensional_generator_candidates:
                    if set(generator) & face_current_node == EMPTY_SET:

                        if isinstance(generator, str):
                            new_E_gen = set(
                                [frozenset(frozenset({generator}) | set({x})) for x in face_current_node])
                        else:
                            new_E_gen = set(
                                [frozenset(frozenset(generator) | set({x})) for x in face_current_node])
                        E_gen = frozenset(
                            (frozenset(new_E_gen) | frozenset(E_gen)) - frozenset({generator}))
                    triadic_concepts[triadic_concepts.index(
                        current_node)].extensional_generator_candidates = E_gen

        find_minimal_extensional_generators(triadic_concepts)

        return triadic_concepts

    def create_hasse_diagram(triadic_concepts, links, hasse_diagram_file_path):
        """Takes the triadic_concepts, links and hasse_diagram_file_path to create the
        Hasse Diagram with all the links between the Triadic Concepts and
        annotated with the Feature Generators.
        The Hasse Diagram is a .graphml file that can be displayed on
        external softwares (as yEd) and it is saved in the output folder
        that the user specified in the configs.json file.

        Args:
            triadic_concepts (list): list of TriadicConcept objects
            links (list): list with the links between Triadic Concepts
            file_name (str): input file name
        """

        nodes = []

        def format_generators(generators):
            t_gens = []
            if generators == []:
                return 'ø'
            for v in generators:
                if isinstance(v[0], list):
                    intent = [', '.join(x for x in sorted(v[0]))]
                    modus = [', '.join(x for x in sorted(v[1]))]
                    t_gen = str(
                        "(" + ', '.join([x for x in intent])) + " - " + str(', '.join([x for x in modus]))+")"
                    t_gens.append(t_gen)
                else:
                    t_gen = "(" + str(v[0]) + " - " + str(v[1]) + ")"
                    t_gens.append(t_gen)
            if len(t_gens) > 1:
                return ["\n".join(x for x in t_gens)][0]
            else:
                return t_gens[0]

        def check_concept(concept, concept_original, nodes):
            if concept not in nodes:
                attributes = []

                concept_intent = triadic_concepts[triadic_concepts.index(
                    concept_original)].intent
                concept_modus = triadic_concepts[triadic_concepts.index(
                    concept_original)].modus
                concept_generators = triadic_concepts[triadic_concepts.index(
                    concept_original)].feature_generator_minimal

                for attribute in zip(concept_intent, concept_modus):
                    _int = str(', '.join(x for x in sorted(attribute[0])))
                    _modus = str(
                        ', '.join(x for x in sorted(attribute[1])))
                    attributes.append(
                        str('({0} - {1})'.format(_int, _modus)))

                hasse.add_node(concept, shape_fill="#FFFFFF",
                               shape="roundrectangle", font_size="14")
                label = str('Features:\n'+'\n'.join(x for x in attributes))
                hasse.add_node(concept+'concepts', label=label, shape_fill="#faddb1",
                               shape="rectangle", font_size="14")
                hasse.add_edge(concept+'concepts', concept,
                               line_type='dotted', arrowhead='none')
                nodes.append(concept)
                generators = format_generators(concept_generators)
                hasse.add_node(concept+'gen', label='F-generators:\n'+generators, shape_fill="#cee2f7",
                               shape="rectangle", font_size="14")
                hasse.add_edge(concept+'gen', concept,
                               line_type='dotted', arrowhead='none')

        hasse = pyyed.Graph()
        for link in tqdm(links):
            concept, successor = link[0], link[1]
            concept_original = concept.copy()
            successor_original = successor.copy()
            if concept == EMPTY_SET:
                concept = 'ø'
            if successor == EMPTY_SET:
                successor = 'ø'
            concept = str(', '.join(x for x in sorted(concept)))
            successor = str(', '.join(x for x in sorted(successor)))

            check_concept(concept, concept_original, nodes)
            check_concept(successor, successor_original, nodes)
            hasse.add_edge(concept, successor, arrowhead='t_shape')

        hasse.write_graph(hasse_diagram_file_path, pretty_print=True)
