# -*- coding: utf-8 -*-
"""
@author: pedroruas
"""

import pytest
from AssociationRules import AssociationRule
from TriadicConcept import TriadicConcept


@pytest.fixture
def fixture_BCAI_implications() -> AssociationRule:
    minimum_support_rules = 0.1
    compute_feature_generators_for_infimum = False
    triadic_concepts = TriadicConcept.get_triadic_concepts_from_input_file(
        'Data/example_PNKRS_2017_big.data.out')
    faces, all_extents = TriadicConcept.create_triadic_concepts_faces(
        triadic_concepts)
    links = TriadicConcept.T_iPred(triadic_concepts, faces, all_extents)
    triadic_concepts = TriadicConcept.compute_f_generators_candidates(
        triadic_concepts, links, compute_feature_generators_for_infimum)
    formal_context = TriadicConcept.compute_formal_context(
        triadic_concepts)
    triadic_concepts = TriadicConcept.compute_feature_generator_validation(
        triadic_concepts, formal_context)

    return AssociationRule.compute_BCAI_implications(
        triadic_concepts, minimum_support_rules)


@pytest.fixture
def fixture_BACI_implications() -> AssociationRule:
    minimum_support_rules = 0.1
    compute_feature_generators_for_infimum = False
    triadic_concepts = TriadicConcept.get_triadic_concepts_from_input_file(
        'Data/example_PNKRS_2017_big.data.out')
    faces, all_extents = TriadicConcept.create_triadic_concepts_faces(
        triadic_concepts)
    links = TriadicConcept.T_iPred(triadic_concepts, faces, all_extents)
    triadic_concepts = TriadicConcept.compute_f_generators_candidates(
        triadic_concepts, links, compute_feature_generators_for_infimum)
    formal_context = TriadicConcept.compute_formal_context(
        triadic_concepts)
    triadic_concepts = TriadicConcept.compute_feature_generator_validation(
        triadic_concepts, formal_context)

    return AssociationRule.compute_BACI_implications(
        triadic_concepts, minimum_support_rules)


@pytest.fixture
def fixture_BCAAR_association_rules() -> AssociationRule:
    minimum_support_rules = 0.1
    minimum_confidence_rules = 0.1
    compute_feature_generators_for_infimum = False
    triadic_concepts = TriadicConcept.get_triadic_concepts_from_input_file(
        'Data/example_PNKRS_2017_big.data.out')
    faces, all_extents = TriadicConcept.create_triadic_concepts_faces(
        triadic_concepts)
    links = TriadicConcept.T_iPred(triadic_concepts, faces, all_extents)
    triadic_concepts = TriadicConcept.compute_f_generators_candidates(
        triadic_concepts, links, compute_feature_generators_for_infimum)
    formal_context = TriadicConcept.compute_formal_context(
        triadic_concepts)
    triadic_concepts = TriadicConcept.compute_feature_generator_validation(
        triadic_concepts, formal_context)
    return AssociationRule.compute_BCAAR_association_rules(
        triadic_concepts, minimum_support_rules,
        minimum_confidence_rules, links)


@pytest.fixture
def fixture_BACAR_association_rules() -> AssociationRule:
    minimum_support_rules = 0.1
    minimum_confidence_rules = 0.1
    compute_feature_generators_for_infimum = False
    triadic_concepts = TriadicConcept.get_triadic_concepts_from_input_file(
        'Data/example_PNKRS_2017_big.data.out')
    faces, all_extents = TriadicConcept.create_triadic_concepts_faces(
        triadic_concepts)
    links = TriadicConcept.T_iPred(triadic_concepts, faces, all_extents)
    triadic_concepts = TriadicConcept.compute_f_generators_candidates(
        triadic_concepts, links, compute_feature_generators_for_infimum)
    formal_context = TriadicConcept.compute_formal_context(
        triadic_concepts)
    triadic_concepts = TriadicConcept.compute_feature_generator_validation(
        triadic_concepts, formal_context)

    return AssociationRule.compute_BACAR_association_rules(
        triadic_concepts, minimum_support_rules,
        minimum_confidence_rules, links)


def test_BCAI_implications(fixture_BCAI_implications: AssociationRule) -> None:
    assert len(fixture_BCAI_implications) == 22


def test_BACI_implications(fixture_BACI_implications: AssociationRule) -> None:
    assert len(fixture_BACI_implications) == 18


def test_BCAAR_association_rules(fixture_BCAAR_association_rules: AssociationRule) -> None:
    assert len(fixture_BCAAR_association_rules) == 16


def test_BACAR_association_rules(fixture_BACAR_association_rules: AssociationRule) -> None:
    assert len(fixture_BACAR_association_rules) == 8
