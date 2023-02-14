# -*- coding: utf-8 -*-
"""
@author: pedroruas
"""

from Timer import Timer
import pandas as pd
import json
import os
from TriadicConcept import TriadicConcept


def old():
    file_name = 'Data/example_PNKRS_2017_big'
    file_name = 'Data/MUSH_32x4'
    file_name = 'Data/groceries_FINAL_THESIS_MONTH_3724objs_40att_12cond'
    file_extension = ".data.out"
    file_path = file_name + file_extension
    empty_set = set([])
    df = pd.read_csv(file_name+file_extension, sep=" ",
                     header=None, low_memory=False)
    df.columns = ["Extent", "Intent", "Modus"]
    df.loc[df['Extent'] == "ø", 'Extent'] = frozenset(empty_set)
    # Creating the column "|Extent|" with all values equal to 0
    df["|Extent|"] = 0
    
    for row in df.itertuples():
        idx = row[0]
        try:
            df.at[idx, '|Extent|'] = len(df.iloc[idx][0].split(","))
        except:
            continue

    df.sort_values(by=["|Extent|", "Extent"], ascending=True, inplace=True)

    new = frozenset([])
    # Converting all elements of the EXTENT into a set
    list_tuples = []
    iterator = 0
    for row in df.itertuples():
        extent = df.iloc[iterator][0]
        if extent != empty_set:
            extent = frozenset(extent.split(","))
        intent = df.iloc[iterator][1]
        intent = intent.split(",")
        condition = df.iloc[iterator][2]
        condition = str(condition).split(",")
        qtd_Objects = df.iloc[iterator][3]
        list_tuples.append((extent, intent, condition, qtd_Objects))
        iterator += 1

    amount_triadic_concepts = len(df)

    triadic_concepts = df.copy()
    del new
    del df

    data = pd.DataFrame(list_tuples)
    data.columns = ["Extent", "Intent", "Modus", "|Extent|"]
    #data.loc[data['Extent'] == {"ø"}, 'Extent'] = {}
    data.sort_values(by="|Extent|", ascending=True, inplace=True)

    del list_tuples

    data_unique = pd.DataFrame(data["Extent"].unique())
    data_unique.columns = ["Extent"]
    data_unique["Intent"] = ""
    data_unique["Modus"] = ""

    list_intent = []
    list_modus = []
    iterator = 0

    for idx, row in data_unique.iterrows():
        value = data_unique.iloc[idx][0]
        selected_data = data.loc[data['Extent'] == value]
        for row2 in selected_data.iterrows():
            list_intent.append(selected_data.iloc[iterator][1])
            list_modus.append(selected_data.iloc[iterator][2])
            iterator += 1
        iterator = 0
        data_unique.at[idx, 'Intent'] = list_intent
        data_unique.at[idx, 'Modus'] = list_modus
        list_intent = []
        list_modus = []
    return data_unique


def mine(file_path, compute_minimality_for_infimum):
    Timer.start("Reading triadic concepts")
    triadic_concepts = TriadicConcept.get_triadic_concepts_from_input_file(
        file_path)
    print("Number of Triadic Concepts:", len(triadic_concepts))
    time = Timer.stop()
    
    # Timer.start("Reading triadic concepts with pandas (old)")
    # tc = old()
    # print("Number of Triadic Concepts: ", tc.shape[0])
    # time = Timer.stop()
    
    # print("X"*100)
    # for c in triadic_concepts:
    #     print(c)
    # print(triadic_concepts[1])
    # print(triadic_concepts[2])
    # print(triadic_concepts[1] >= triadic_concepts[2])
    Timer.start("Creating triadic concepts faces")
    faces, all_extents = TriadicConcept.create_triadic_concepts_faces(
        triadic_concepts)
    time = Timer.stop()
    # print("FACES: ",faces)
    # print("ALL EXTENTS: ",all_extents)

    print("#"*100)
    Timer.start("Running T-iPred")
    links = TriadicConcept.T_iPred(triadic_concepts, faces, all_extents)
    time = Timer.stop()
    print("Number of links:", len(links))

    # print("#"*100)
    # Timer.start("Running links to dict")
    # links_dict = TriadicConcept.list_of_links_to_dict(links)
    # time = Timer.stop()
    # print("Number of itens:", len(links_dict))
    # for item in links:
    #     print(item)

    # print("ORIGINAL TRIADIC CONCEPTS")
    # print("+"*100)
    # for c in triadic_concepts:
    #     print(c)
    #     print()

    # print("#"*100)
    # for x in links:
    #     print(x)
    Timer.start("Computing F-Generators")
    updated_triadic_concepts = TriadicConcept.compute_f_generators_candidates(triadic_concepts, links, compute_minimality_for_infimum)
    time = Timer.stop()
    # print("Number of itens:", len(links_dict))
    
    # print("FEATURE GENERATOR CANDIDATES")
    # for c in updated_triadic_concepts:
    #     print(c)
    #     print()
    # print(triadic_concepts[triadic_concepts.index({'2'})])
    
    Timer.start("Computing Formal Context")
    formal_context = TriadicConcept.compute_formal_context(updated_triadic_concepts)
    time = Timer.stop()
    # print(formal_context)
    
    Timer.start("Validating Feature Generators")
    updated_triadic_concepts = TriadicConcept.compute_feature_generator_validation(updated_triadic_concepts, formal_context)
    time = Timer.stop()
    
    # print("FEATURE GENERATORS VALIDATION")
    # for c in updated_triadic_concepts:
    #     print(c)
    #     print()
    
    


def main():
    with open('configs.json') as json_file:
        data = json.load(json_file)

    for input_file_path in data['input_files']:
        _, file_name = os.path.split(input_file_path)
        output_dir = data['output_dir']
        print(f'Running Triadic Miner on {input_file_path} file...')
        compute_minimality_for_infimum = data[
            'compute_feature_generators_minimality_test_for_infimum']

        mine(input_file_path, compute_minimality_for_infimum)


if __name__ == "__main__":
    main()
