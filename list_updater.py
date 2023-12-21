def update(list_a, list_b, counter):
  def find_unique_elements(list_a, list_b):
    set_b = set(map(lambda d: frozenset(d.items()), list_b))
    list_a_new = [item for item in list_a if frozenset(item.items()) not in set_b]
    return list_a_new
    
  list_a_new = find_unique_elements(list_a, list_b)

  unordered_counter = counter
  while unordered_counter < len(list_b) and list_b[unordered_counter] in list_a:
    unordered_counter += 1
  
  index = 0
  if len(list_a_new) <= (30 - unordered_counter - 1):
    for i in range(unordered_counter, unordered_counter + len(list_a_new)):
      list_b[i] = list_a_new[index]
      index = index + 1
      if (index == len(list_a_new)):
        break
  else:
    for i in range(unordered_counter, 30):
      list_b[i] = list_a_new[index]
      index = index + 1
      if (index == len(list_a_new)):
        break
    for j in range(len(list_a_new) - 30 + unordered_counter):
      list_b[i] = list_a_new[index]
      index = index + 1
      if (index == len(list_a_new)):
        break
      
  return list_b
