def find_unique_elements(list_a, list_b):
    set_b = set(map(lambda d: frozenset(d.items()), list_b))
    list_a_new = [item for item in list_a if frozenset(
        item.items()) not in set_b]
    return list_a_new
