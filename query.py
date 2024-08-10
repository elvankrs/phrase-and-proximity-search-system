import sys, os, re, xml.dom.minidom, string, pickle
from xml.dom.minidom import parse, parseString

dict_path = sys.argv[1]

# Read the dictionary pkl file
with open(dict_path, 'rb') as fp:
    term_dict = pickle.load(fp)


def freq(term):
  return term_dict[term][0]


def sort_by_increasing_freq(query):
  terms = query.split()
  term_frequencies = []
  for term in terms:
    term_frequencies.append(freq(term))

  term_frequencies, terms = zip(*sorted(zip(term_frequencies, terms)))
  
  return terms


def postings(term, return_type):
  if return_type == "list": return list(term_dict[term][1])
  else: return term_dict[term][1]


def positions(postings_dict, doc_ID):
  # Given the postings list and the docID, find the positions list
  return postings_dict[doc_ID][1]


def sort_by_increasing_size(query):
  pos_lists = query
  list_sizes = []
  for pos_list in pos_lists:
    list_sizes.append(len(pos_list))

  list_sizes, pos_lists = zip(*sorted(zip(list_sizes, pos_lists)))
  
  return pos_lists


def intersect(p1, p2):

  answer = []
  ctr=0

  p1_iter, p2_iter = iter(p1), iter(p2) # iterators
  doc_ID_p1, doc_ID_p2 = next(p1_iter, "end"), next(p2_iter, "end")

  while (doc_ID_p1 != "end") and (doc_ID_p2 != "end"):
    
    ctr+=1

    if doc_ID_p1 == doc_ID_p2:
      answer.append(doc_ID_p1)
      doc_ID_p1, doc_ID_p2 = next(p1_iter, "end"), next(p2_iter, "end")
    
    elif doc_ID_p1 < doc_ID_p2:
      doc_ID_p1 = next(p1_iter, "end")

    else:
      doc_ID_p2 = next(p2_iter, "end")

    if ctr > 25000: break

  return answer


def intersect_multiple(query):
  # query: list of terms in the query (['old', 'crop', 'cocoa'] for "old crop cocoa" query)
  terms = sort_by_increasing_freq(query)
  result = postings(terms[0], "list")
  # terms = terms[1:]
  while (len(terms) != 0) and (len(result) != 0):
    result = intersect(result, postings(terms[0], "list"))
    terms = terms[1:]
  return result


def check_answers(query, candidate_answers):
  # Checks the positions in the candidate answers in order to find an exact match.

  answer = []
  for candidate_answer in candidate_answers:
    # candidate answer is the doc ID.

    pos_list_sizes = []

    for term in query.split(): # First, find the maximum position index in order to form a list to reconstruct the string
      postings_dict = postings(term, "dict")
      pos_list = positions(postings_dict, candidate_answer)
      pos_list_sizes.append(max(pos_list))

    pos_list_size = max(pos_list_sizes)

    reconstructed_str = []

    for i in range(pos_list_size + 1):
      reconstructed_str.append(" ")
    
    for term in query.split(): # add terms to reconstructed str (list)
      postings_dict = postings(term, "dict")
      pos_list = positions(postings_dict, candidate_answer)
      for pos in pos_list:
        reconstructed_str[pos] = term
    
    final_str = ""
    for ch in reconstructed_str: # convert the list to string for the final check
      final_str += ch + " "

    if query in final_str: # finally check if the reconstructed string contains the query
      answer.append(candidate_answer)
      
  return answer



def positional_intersect(p1, p2, k):

  answer, ans_IDs = [], []
  ctr=0

  p1_iter, p2_iter = iter(postings(p1, "list")), iter(postings(p2, "list")) # iterators (iterate over the docs in the postings list)
  doc_ID_p1, doc_ID_p2 = next(p1_iter, "end"), next(p2_iter, "end")

  while (doc_ID_p1 != "end") and (doc_ID_p2 != "end"):
    
    ctr+=1
    if doc_ID_p1 == doc_ID_p2:

      l = []

      postings_dict_p1, postings_dict_p2 = postings(p1, "dict"), postings(p2, "dict")
      positions(postings_dict_p1, doc_ID_p1)
      
      pos1_iter, pos2_iter = iter(positions(postings_dict_p1, doc_ID_p1)), iter(positions(postings_dict_p2, doc_ID_p2))
      pos_p1, pos_p2 = next(pos1_iter, "end"), next(pos2_iter, "end")

      while (pos_p1 != "end"):

        while (pos_p2 != "end"):

          if abs(pos_p1 - pos_p2) <= k:
            l.append(pos_p2)
          elif pos_p2 > pos_p1:
            break
          pos_p2 = next(pos2_iter, "end")

        while (len(l) != 0) and (abs(l[0] - pos_p1) > k):
          del l[0]
        
        for ps in l:
          answer.append((doc_ID_p1, pos_p1, ps))
          ans_IDs.append(doc_ID_p1)
        
        pos_p1 = next(pos1_iter, "end")
      
      doc_ID_p1, doc_ID_p2 = next(p1_iter, "end"), next(p2_iter, "end")
    
    elif doc_ID_p1 < doc_ID_p2:
      doc_ID_p1 = next(p1_iter, "end")

    else:
      doc_ID_p2 = next(p2_iter, "end")

    if ctr > 100000: break
    
    ans_IDs = list(set(ans_IDs))
  
  return answer, ans_IDs



def phrase_query(query): # Phrase query

  candidate_answers = intersect_multiple(query)
  answer = check_answers(query, candidate_answers)
  print(*answer)
  return answer


def proximity_query(w1, w2, k): # Proximity query
  answer, ans_IDs = positional_intersect(w1, w2, int(k) + 1)
  print(*ans_IDs)
  return list(set(ans_IDs))


if len(sys.argv) > 3:
  w1, k, w2 = sys.argv[2], sys.argv[3], sys.argv[4]
  if (w1 in term_dict.keys()) and (w2 in term_dict.keys()):
    proximity_query(w1, w2, k)
  else:
    print()
    exit()

else:
  phrase = sys.argv[2]
  for word in phrase.split(): # Check if all the terms occur in the dictionary
    if word not in term_dict.keys():
      print()
      exit()

  phrase_query(phrase)