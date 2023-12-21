def update(list_a, list_b, counter):
  def find_unique_elements(list_a, list_b):
    set_b = set(list_b)
    list_a_new = [value for value in list_a if value not in set_b]
    return list_a_new
    
  list_a_new = find_unique_elements(list_a, list_b)
  index = 0
  if len(list_a_new) <= (30 - counter - 1):
    for i in range(counter, counter + len(list_a_new)):
      list_b[i] = list_a_new[index]
      index = index + 1
  else:
    for i in range(counter, 30):
      list_b[i] = list_a_new[index]
      index = index + 1
    for j in range(len(list_a_new) - 30 + counter):
      list_b[i] = list_a_new[index]
      index = index + 1
      
  return list_b
