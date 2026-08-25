import operator
from collections import defaultdict
from typing import List, Dict, Tuple, Any

def load_concepts_from_file(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[int, Dict[str, Any]]]:
    """
    Reads the data file and structures the triadic concepts.
    Returns a list and a dictionary mapped by the document ID.
    """
    triadic_concepts = []
    triadic_concepts_dict = {}
    
    with open(file_path, 'r', encoding='utf-8') as reader:
        for idx, row in enumerate(reader):
            line = row.rstrip('\n').split(" ")
            if len(line) < 3:
                continue
                
            extent = sorted(line[0].split(','))
            intent = sorted(line[1].split(','))
            modus = sorted(line[2].split(','))
            
            # Removes empty elements that might arise from the split
            extent = [x for x in extent if x]
            intent = [x for x in intent if x]
            modus = [x for x in modus if x]

            data = {
                'doc_id': idx,
                'triadic_concept': ",".join(extent + intent + modus),
                'triadic_concept_show': f"{','.join(extent)} - {','.join(intent)} - {','.join(modus)}",
                'extent': ",".join(extent),
                'extent_size': len(extent),
                'intent': ",".join(intent),
                'intent_size': len(intent),
                'modus': ",".join(modus),
                'modus_size': len(modus)
            }
            triadic_concepts_dict[idx] = data
            triadic_concepts.append(data)
            
    return triadic_concepts, triadic_concepts_dict

def build_inverted_index(triadic_concepts: List[Dict[str, Any]]) -> Dict[str, List[int]]:
    """
    Builds an inverted index mapping elements (words) to their respective doc_ids.
    """
    inv_index = defaultdict(list)
    for concept in triadic_concepts:
        doc_id = concept['doc_id']
        words = concept['triadic_concept'].split(',')
        for word in words:
            if word: # Avoids adding empty strings to the index
                inv_index[word].append(doc_id)
    return dict(inv_index)

def _parse_query_part(part: str) -> List[str]:
    """Private helper function to clean and split parts of the query."""
    if not part or part in ['?', '']:
        return []
    return [x.strip() for x in part.split(',') if x.strip() and x.strip() not in ['?', '']]

def _get_candidate_documents(query_elements: List[str], inv_index: Dict[str, List[int]]) -> Dict[int, int]:
    """
    Private helper function.
    Returns a dictionary mapping {doc_id: number_of_found_query_elements}.
    Replaces the slow 'res.count(x)' logic with a linear O(N) count.
    """
    res_counts = defaultdict(int)
    for element in query_elements:
        if element in inv_index:
            for doc_id in inv_index[element]:
                res_counts[doc_id] += 1
    return dict(res_counts)

def get_concepts_max(query: Tuple[str, str, str], inv_index: Dict[str, List[int]]) -> Tuple[List[int], int]:
    """
    Returns the document IDs that have the MAXIMUM number of matches with the query.
    """
    query_elements = _parse_query_part(query[0]) + _parse_query_part(query[1]) + _parse_query_part(query[2])
    
    res_counts = _get_candidate_documents(query_elements, inv_index)
    if not res_counts:
        return [], 0
        
    max_value = max(res_counts.values())
    docs_with_max = [doc_id for doc_id, count in res_counts.items() if count == max_value]
    
    return docs_with_max, max_value

def get_concepts(query: Tuple[str, str, str], inv_index: Dict[str, List[int]]) -> Tuple[List[int], int]:
    """
    Returns all document IDs that have any intersection with the query.
    """
    query_elements = _parse_query_part(query[0]) + _parse_query_part(query[1]) + _parse_query_part(query[2])
    
    res_counts = _get_candidate_documents(query_elements, inv_index)
    value = len(query_elements) - 1 
    
    return list(res_counts.keys()), value

def get_ranked_triadic_concepts(
    query: Tuple[str, str, str], 
    inv_index: Dict[str, List[int]], 
    triadic_concepts_dict: Dict[int, Dict[str, Any]], 
    threshold_matched_elements: int,
    top_k: int
) -> List[Tuple[str, float]]:
    """
    Ranks the triadic concepts using the original custom metric,
    now normalized to return a score between 0.0 and 1.0.
    """
    ext_query = _parse_query_part(query[0])
    int_query = _parse_query_part(query[1])
    mod_query = _parse_query_part(query[2])
    
    ext_size = len(ext_query)
    int_size = len(int_query)
    mod_size = len(mod_query)
    
    query_elements = ext_query + int_query + mod_query
    total_query_size = len(query_elements)
    
    if total_query_size == 0:
        return []

    # Fetches candidate documents using the O(N) inverted index
    res_counts = _get_candidate_documents(query_elements, inv_index)
    
    # Filters documents by the threshold
    min_value_required = total_query_size - threshold_matched_elements
    candidate_docs = [doc_id for doc_id, count in res_counts.items() if count >= min_value_required]
    
    ranked_docs = []
    
    # Pre-calculates query sets for faster intersection operations
    ext_set, int_set, mod_set = set(ext_query), set(int_query), set(mod_query)
    
    # Defines the proportional weights of each dimension
    weight_ext = ext_size / total_query_size
    weight_int = int_size / total_query_size
    weight_mod = mod_size / total_query_size
    
    def _calc_normalized_dimension_score(query_set: set, query_size: int, concept_string: str) -> float:
        """Calculates the score of a dimension and normalizes it between 0 and 1"""
        if query_size == 0:
            return 0.0
            
        concept_set = set(x for x in concept_string.split(',') if x)
        intersection_len = len(query_set.intersection(concept_set))
        max_union_size = max(query_size, len(concept_set))
        
        # Original logic
        raw_score = intersection_len + (intersection_len / max_union_size if max_union_size > 0 else 0)
        
        # Normalization by dividing by the maximum possible score
        max_possible_score = query_size + 1
        return raw_score / max_possible_score

    for doc_id in candidate_docs:
        concept = triadic_concepts_dict[doc_id]
        
        # Calculates the already normalized [0, 1] score of each dimension
        score_ext = _calc_normalized_dimension_score(ext_set, ext_size, concept['extent'])
        score_int = _calc_normalized_dimension_score(int_set, int_size, concept['intent'])
        score_mod = _calc_normalized_dimension_score(mod_set, mod_size, concept['modus'])
        
        # Applies the dimension weights
        final_ranking = (score_ext * weight_ext) + \
                        (score_int * weight_int) + \
                        (score_mod * weight_mod)
        
        # Now the final_ranking is guaranteed to be between 0.0 and 1.0
        ranked_docs.append((concept['triadic_concept_show'], round(final_ranking, 2)))
        
    return sorted(ranked_docs, key=lambda x: x[1], reverse=True)[:top_k]

def _calc_jaccard_dimension(query_set: set, concept_string: str) -> float:
    """
    Calculates the Jaccard Similarity Index (Intersection / Union) 
    for a single dimension (Extent, Intent, or Modus).
    """
    concept_set = set(x for x in concept_string.split(',') if x)
    
    # If both sets are empty, the standard Jaccard in mathematics would be 1.0, 
    # but for search ranking purposes, we contribute 0.0 to avoid inflating the score.
    if not query_set and not concept_set:
        return 0.0
        
    intersection_len = len(query_set.intersection(concept_set))
    union_len = len(query_set.union(concept_set))
    
    return intersection_len / union_len if union_len > 0 else 0.0


def get_ranked_triadic_concepts_jaccard(
    query: Tuple[str, str, str], 
    inv_index: Dict[str, List[int]], 
    triadic_concepts_dict: Dict[int, Dict[str, Any]], 
    threshold_matched_elements: int,
    top_k: int
) -> List[Tuple[str, float]]:
    """
    Ranks the triadic concepts using the Jaccard Similarity Index,
    weighting the importance of each dimension by the size of the original query.
    """
    ext_query = _parse_query_part(query[0])
    int_query = _parse_query_part(query[1])
    mod_query = _parse_query_part(query[2])
    
    ext_size = len(ext_query)
    int_size = len(int_query)
    mod_size = len(mod_query)
    
    query_elements = ext_query + int_query + mod_query
    total_query_size = len(query_elements)
    
    if total_query_size == 0:
        return []

    # Fetches candidate documents using the O(N) inverted index
    res_counts = _get_candidate_documents(query_elements, inv_index)
    
    # Filters documents by the threshold
    min_value_required = total_query_size - threshold_matched_elements
    candidate_docs = [doc_id for doc_id, count in res_counts.items() if count >= min_value_required]
    
    ranked_docs = []
    
    # Pre-calculates the query sets to optimize repetitive operations
    ext_set, int_set, mod_set = set(ext_query), set(int_query), set(mod_query)
    
    # Defines the weights of each dimension based on the user's query
    weight_ext = ext_size / total_query_size
    weight_int = int_size / total_query_size
    weight_mod = mod_size / total_query_size

    for doc_id in candidate_docs:
        concept = triadic_concepts_dict[doc_id]
        
        # Calculates Jaccard for each dimension
        jaccard_ext = _calc_jaccard_dimension(ext_set, concept['extent'])
        jaccard_int = _calc_jaccard_dimension(int_set, concept['intent'])
        jaccard_mod = _calc_jaccard_dimension(mod_set, concept['modus'])
        
        # Calculates the final score weighted by the three dimensions
        final_ranking = (jaccard_ext * weight_ext) + \
                        (jaccard_int * weight_int) + \
                        (jaccard_mod * weight_mod)
                        
        ranked_docs.append((concept['triadic_concept_show'], round(final_ranking, 2)))
        
    # Sorts by score from highest to lowest and returns the top K
    return sorted(ranked_docs, key=lambda x: x[1], reverse=True)[:top_k]

def _calc_dice_dimension(query_set: set, concept_string: str) -> float:
    """
    Calculates the Sørensen-Dice Coefficient (2 * Intersection / Sum of Sizes)
    for a single dimension (Extent, Intent, or Modus).
    """
    concept_set = set(x for x in concept_string.split(',') if x)
    
    # If both sets are empty, we return 0.0 to avoid inflating the search score
    if not query_set and not concept_set:
        return 0.0
        
    intersection_len = len(query_set.intersection(concept_set))
    total_elements = len(query_set) + len(concept_set)
    
    return (2.0 * intersection_len) / total_elements if total_elements > 0 else 0.0


def get_ranked_triadic_concepts_dice(
    query: Tuple[str, str, str], 
    inv_index: Dict[str, List[int]], 
    triadic_concepts_dict: Dict[int, Dict[str, Any]], 
    threshold_matched_elements: int,
    top_k: int
) -> List[Tuple[str, float]]:
    """
    Ranks the triadic concepts using the Sørensen-Dice Coefficient,
    weighting the importance of each dimension by the size of the original query.
    """
    ext_query = _parse_query_part(query[0])
    int_query = _parse_query_part(query[1])
    mod_query = _parse_query_part(query[2])
    
    ext_size = len(ext_query)
    int_size = len(int_query)
    mod_size = len(mod_query)
    
    query_elements = ext_query + int_query + mod_query
    total_query_size = len(query_elements)
    
    if total_query_size == 0:
        return []

    # Fetches candidate documents using the O(N) inverted index
    res_counts = _get_candidate_documents(query_elements, inv_index)
    
    # Filters documents by the threshold
    min_value_required = total_query_size - threshold_matched_elements
    candidate_docs = [doc_id for doc_id, count in res_counts.items() if count >= min_value_required]
    
    ranked_docs = []
    
    # Pre-calculates the query sets to optimize repetitive operations
    ext_set, int_set, mod_set = set(ext_query), set(int_query), set(mod_query)
    
    # Defines the weights of each dimension based on the user's query
    weight_ext = ext_size / total_query_size
    weight_int = int_size / total_query_size
    weight_mod = mod_size / total_query_size

    for doc_id in candidate_docs:
        concept = triadic_concepts_dict[doc_id]
        
        # Calculates Dice for each dimension
        dice_ext = _calc_dice_dimension(ext_set, concept['extent'])
        dice_int = _calc_dice_dimension(int_set, concept['intent'])
        dice_mod = _calc_dice_dimension(mod_set, concept['modus'])
        
        # Calculates the final score weighted by the three dimensions
        final_ranking = (dice_ext * weight_ext) + \
                        (dice_int * weight_int) + \
                        (dice_mod * weight_mod)
                        
        ranked_docs.append((concept['triadic_concept_show'], round(final_ranking, 2)))
        
    # Sorts by score from highest to lowest and returns the top K
    return sorted(ranked_docs, key=lambda x: x[1], reverse=True)[:top_k]

def _calc_tversky_dimension(query_set: set, concept_string: str, alpha: float, beta: float) -> float:
    """
    Calculates the Tversky Index for a single dimension (Extent, Intent, or Modus).
    """
    concept_set = set(x for x in concept_string.split(',') if x)
    
    # Returns 0.0 if both sets are empty to avoid inflating the score
    if not query_set and not concept_set:
        return 0.0
        
    intersection_len = len(query_set.intersection(concept_set))
    
    # Elements in the query missing from the concept (false negatives)
    x_minus_y_len = len(query_set - concept_set) 
    
    # Extra elements in the concept not present in the query (false positives)
    y_minus_x_len = len(concept_set - query_set) 
    
    # Applies the formula with alpha and beta weights
    denominator = intersection_len + (alpha * x_minus_y_len) + (beta * y_minus_x_len)
    
    return intersection_len / denominator if denominator > 0 else 0.0


def get_ranked_triadic_concepts_tversky(
    query: Tuple[str, str, str], 
    inv_index: Dict[str, List[int]], 
    triadic_concepts_dict: Dict[int, Dict[str, Any]], 
    threshold_matched_elements: int,
    top_k: int,
    alpha: float = 1.0,
    beta: float = 1.0
) -> List[Tuple[str, float]]:
    """
    Ranks the triadic concepts using the Tversky Index.
    Allows fine control over the weight of false positives and false negatives via alpha and beta.
    """
    ext_query = _parse_query_part(query[0])
    int_query = _parse_query_part(query[1])
    mod_query = _parse_query_part(query[2])
    
    ext_size = len(ext_query)
    int_size = len(int_query)
    mod_size = len(mod_query)
    
    query_elements = ext_query + int_query + mod_query
    total_query_size = len(query_elements)
    
    if total_query_size == 0:
        return []

    # Fetches candidate documents using the O(N) inverted index
    res_counts = _get_candidate_documents(query_elements, inv_index)
    
    # Filters documents by the threshold
    min_value_required = total_query_size - threshold_matched_elements
    candidate_docs = [doc_id for doc_id, count in res_counts.items() if count >= min_value_required]
    
    ranked_docs = []
    
    # Pre-calculates the query sets
    ext_set, int_set, mod_set = set(ext_query), set(int_query), set(mod_query)
    
    # Defines the proportional weights of each dimension
    weight_ext = ext_size / total_query_size
    weight_int = int_size / total_query_size
    weight_mod = mod_size / total_query_size

    for doc_id in candidate_docs:
        concept = triadic_concepts_dict[doc_id]
        
        # Calculates Tversky for each dimension passing alpha and beta
        tversky_ext = _calc_tversky_dimension(ext_set, concept['extent'], alpha, beta)
        tversky_int = _calc_tversky_dimension(int_set, concept['intent'], alpha, beta)
        tversky_mod = _calc_tversky_dimension(mod_set, concept['modus'], alpha, beta)
        
        # Calculates the final weighted score
        final_ranking = (tversky_ext * weight_ext) + \
                        (tversky_int * weight_int) + \
                        (tversky_mod * weight_mod)
                        
        # The result will remain in the [0.0, 1.0] scale
        ranked_docs.append((concept['triadic_concept_show'], round(final_ranking, 2)))
        
    return sorted(ranked_docs, key=lambda x: x[1], reverse=True)[:top_k]


# ==============================================================================
# Usage Example
# ==============================================================================
if __name__ == '__main__':
    FILE_PATH = './input/example_PNKRST.data.out'
    
    # 1. Load the data
    concepts_list, concepts_dict = load_concepts_from_file(FILE_PATH)
    
    # 2. Build the inverted index
    inverted_idx = build_inverted_index(concepts_list)
    
    # 3. Perform the search
    query = ('1,6', 'R', 'c')
    
    results = get_ranked_triadic_concepts(
        query=query, 
        inv_index=inverted_idx, 
        triadic_concepts_dict=concepts_dict, 
        threshold_matched_elements=1, 
        top_k=3
    )
    
    print("Top 3 Concepts Found:")
    for res, score in results:
        print(f"Score: {score} | Concept: {res}")