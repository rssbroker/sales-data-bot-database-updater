from collections import Counter


def find_mapping(string_a, string_b):
    if len(string_a) < len(string_b):
        string_a = ("0" * (len(string_b)-len(string_a))) + string_a
    elif len(string_a) > len(string_b):
        string_a = string_a[-len(string_b):-1]
    mapping = {}
    for char_a, char_b in zip(string_a, string_b):
        mapping[char_b] = char_a
    return mapping


def restore_strings(list_a, list_b):
    # Use the mapping from the first pair of strings
    initial_mapping = find_mapping(list_a[0], list_b[0])

    # Create a mapping candidates dictionary based on characters in List A and List B
    mapping_candidates = {}
    for string_a, string_b in zip(list_a, list_b):
        for char_a, char_b in zip(string_a, string_b):
            if char_b not in mapping_candidates:
                mapping_candidates[char_b] = Counter()

            mapping_candidates[char_b][char_a] += 1

    # Use the most common mapping for each character in List B
    final_mapping = {char_b: counter.most_common(
        1)[0][0] for char_b, counter in mapping_candidates.items()}

    # Use the final mapping to restore the original strings
    restored_list_b = [''.join(final_mapping.get(char, char)
                               for char in string_b) for string_b in list_b]

    return restored_list_b
