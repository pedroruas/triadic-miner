# -*- coding: utf-8 -*-
"""
@author: pedroruas
"""

import pytest
from triadic_miner.TriadicConcept import TriadicConcept


@pytest.fixture
def fixture_triadic_concepts() -> TriadicConcept:
    return TriadicConcept.get_triadic_concepts_from_input_file(
        "input/example_PNKRS.data.out"
    )


@pytest.fixture
def fixture_links() -> list:
    triadic_concepts = TriadicConcept.get_triadic_concepts_from_input_file(
        "input/example_PNKRS.data.out"
    )
    faces, all_extents = TriadicConcept.create_triadic_concepts_faces(triadic_concepts)
    return TriadicConcept.T_iPred(triadic_concepts, faces, all_extents)


@pytest.fixture
def fixture_feature_generators() -> TriadicConcept:
    compute_feature_generators_for_infimum = False

    triadic_concepts = TriadicConcept.get_triadic_concepts_from_input_file(
        "input/example_PNKRS.data.out"
    )
    faces, all_extents = TriadicConcept.create_triadic_concepts_faces(triadic_concepts)
    links = TriadicConcept.T_iPred(triadic_concepts, faces, all_extents)
    triadic_concepts = TriadicConcept.compute_f_generators_candidates(
        triadic_concepts, links, compute_feature_generators_for_infimum
    )
    formal_context = TriadicConcept.compute_formal_context(triadic_concepts)

    return TriadicConcept.compute_feature_generator_validation(
        triadic_concepts, formal_context
    )


@pytest.fixture
def fixture_concept_stability() -> TriadicConcept:
    triadic_concepts = TriadicConcept.get_triadic_concepts_from_input_file(
        "input/example_PNKRS.data.out"
    )
    formal_context = TriadicConcept.compute_formal_context(triadic_concepts)
    return TriadicConcept.compute_concept_stability(triadic_concepts, formal_context)


@pytest.fixture
def fixture_separation_index() -> TriadicConcept:
    triadic_concepts = TriadicConcept.get_triadic_concepts_from_input_file(
        "input/example_PNKRS.data.out"
    )
    return TriadicConcept.separation_index_calculation(triadic_concepts)


def test_reading_triadic_concepts_file(
    fixture_triadic_concepts: TriadicConcept,
) -> None:
    assert len(fixture_triadic_concepts) == 17
    assert {"1"} == (
        fixture_triadic_concepts[fixture_triadic_concepts.index({"1"})].extent
    )
    assert {"R"} in (
        fixture_triadic_concepts[fixture_triadic_concepts.index({"1"})].intent
    )
    assert {"N", "P"} in (
        fixture_triadic_concepts[fixture_triadic_concepts.index({"1"})].intent
    )
    assert {"N", "K", "P"} in (
        fixture_triadic_concepts[fixture_triadic_concepts.index({"1"})].intent
    )
    assert {"c", "a"} in (
        fixture_triadic_concepts[fixture_triadic_concepts.index({"1"})].modus
    )
    assert {"d", "a", "b"} in (
        fixture_triadic_concepts[fixture_triadic_concepts.index({"1"})].modus
    )
    assert {"a", "b"} in (
        fixture_triadic_concepts[fixture_triadic_concepts.index({"1"})].modus
    )


def test_T_iPred(fixture_links: list) -> None:
    assert len(fixture_links) == 29
    assert ({"5"}, frozenset()) in fixture_links
    assert ({"2"}, frozenset()) in fixture_links
    assert ({"1"}, frozenset()) in fixture_links
    assert ({"4"}, frozenset()) in fixture_links
    assert ({"3", "4"}, frozenset({"4"})) in fixture_links
    assert ({"1", "4"}, frozenset({"4"})) in fixture_links
    assert ({"1", "4"}, frozenset({"1"})) in fixture_links
    assert ({"2", "4"}, frozenset({"4"})) in fixture_links
    assert ({"2", "4"}, frozenset({"2"})) in fixture_links
    assert ({"2", "5"}, frozenset({"2"})) in fixture_links
    assert ({"2", "5"}, frozenset({"5"})) in fixture_links
    assert ({"1", "5"}, frozenset({"1"})) in fixture_links
    assert ({"1", "5"}, frozenset({"5"})) in fixture_links
    assert ({"5", "3", "4"}, frozenset({"5"})) in fixture_links
    assert ({"5", "3", "4"}, frozenset({"3", "4"})) in fixture_links
    assert ({"1", "3", "4"}, frozenset({"1", "4"})) in fixture_links
    assert ({"1", "3", "4"}, frozenset({"3", "4"})) in fixture_links
    assert ({"1", "2", "4"}, frozenset({"4", "2"})) in fixture_links
    assert ({"1", "2", "4"}, frozenset({"1", "4"})) in fixture_links
    assert ({"1", "3", "5"}, frozenset({"1", "5"})) in fixture_links
    assert ({"5", "1", "3", "4"}, frozenset({"1", "3", "5"})) in fixture_links
    assert ({"5", "1", "3", "4"}, frozenset({"1", "3", "4"})) in fixture_links
    assert ({"5", "1", "3", "4"}, frozenset({"4", "3", "5"})) in fixture_links
    assert ({"5", "2", "3", "4"}, frozenset({"4", "2"})) in fixture_links
    assert ({"5", "2", "3", "4"}, frozenset({"4", "3", "5"})) in fixture_links
    assert ({"5", "2", "3", "4"}, frozenset({"5", "2"})) in fixture_links
    assert ({"3", "2", "1", "4", "5"}, frozenset({"1", "4", "3", "5"})) in fixture_links
    assert ({"3", "2", "1", "4", "5"}, frozenset({"4", "2", "3", "5"})) in fixture_links
    assert ({"3", "2", "1", "4", "5"}, frozenset({"1", "4", "2"})) in fixture_links


def test_feature_generators(fixture_feature_generators: TriadicConcept) -> None:
    assert [["K", "c"]] == (
        fixture_feature_generators[
            fixture_feature_generators.index({"5"})
        ].feature_generator_minimal
    )
    assert ["K", "d"] in (
        fixture_feature_generators[
            fixture_feature_generators.index({"2"})
        ].feature_generator_minimal
    )
    assert (
        len(
            (
                fixture_feature_generators[
                    fixture_feature_generators.index({"2"})
                ].feature_generator_minimal
            )
        )
        == 3
    )


def test_concept_stability(fixture_concept_stability: TriadicConcept) -> None:
    assert (
        len(
            fixture_concept_stability[
                fixture_concept_stability.index({"4", "5", "2", "3"})
            ].concept_stability
        )
        == 1
    )
    assert (
        0.375
        == fixture_concept_stability[
            fixture_concept_stability.index({"4", "5", "2", "3"})
        ].concept_stability[0][-1]
    )
    assert (
        len(
            fixture_concept_stability[
                fixture_concept_stability.index({"5", "2"})
            ].concept_stability
        )
        == 3
    )


def test_separation_index(fixture_separation_index: TriadicConcept) -> None:
    assert (
        len(
            fixture_separation_index[
                fixture_separation_index.index({"1", "5"})
            ].separation_index
        )
        == 2
    )
    assert (
        0.176
        == fixture_separation_index[
            fixture_separation_index.index({"1", "4", "2"})
        ].separation_index[0][-1]
    )
