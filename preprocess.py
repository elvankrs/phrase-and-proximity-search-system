import sys, os, re, xml.dom.minidom, string, pickle
from xml.dom.minidom import parse, parseString

data_path = sys.argv[1]

def normalize(text):
  text = text.translate(str.maketrans('', '', string.punctuation)) # Punctuation removal
  text = text.lower()  # Case folding
  text = re.sub(r'\d+','', text) # Removing numbers
  return text

def tokenize(text):
  text = text.replace('\n', ' ')
  tokens = text.split()
  return tokens

def preprocess(documents):

  tokenized_docs = []
  term_dict = {}

  for document in documents:
    doc = parseString(document)

    # Get the doc IDs
    doc_id = int(dict(doc.documentElement.attributes.items())["NEWID"])

    # Get the content of the document

    doc_title = ''
    doc_body = ''

    if len(doc.getElementsByTagName("TITLE")) != 0:
      doc_title = doc.getElementsByTagName("TITLE")[0].firstChild.nodeValue

    if len(doc.getElementsByTagName("BODY")) != 0:
      doc_body = doc.getElementsByTagName("BODY")[0].firstChild.nodeValue

    doc_final = doc_title + ' ' + doc_body

    doc_final = normalize(doc_final)
    doc_tokens = tokenize(doc_final)

    tokenized_docs.append(doc_tokens)

    # Process the terms in the document
    pos = 1

    for term in doc_tokens:

      if term not in term_dict.keys(): # if the term is a newcomer
        term_dict[term] = [1] # frequency of the term is 1

        doc_dict = {} # document is also a newcomer
        doc_dict[doc_id] = [1] # number of occurrences of the term in that document
        doc_dict[doc_id].append([pos])

        term_dict[term].append(doc_dict) # document dictionary added to the postings list


      else: # if the term is already present

        if doc_id not in term_dict[term][1].keys(): # if the doc is newcomer

          term_dict[term][1][doc_id] = [1]
          term_dict[term][1][doc_id].append([pos])

          term_dict[term][0] += 1 # number of documents that contain the term

    
        else: # if the doc is already present
          term_dict[term][1][doc_id][1].append(pos)
          term_dict[term][1][doc_id][0] += 1

      if doc_id == 3:
        break

      pos += 1 # After processing the term is finished, iterate the position
      
  return term_dict


rm_pattern = re.compile(r"&#\d*;")
rm2_pattern = re.compile(r"\n Reuter\n")
doc_pattern = re.compile(r"<REUTERS.*?<\/REUTERS>", re.S)

documents = []

# Read the docs

for file in os.listdir(data_path):
    
  if file.endswith(".sgm"):
      
    # Read each sgm file
    file_name = os.path.join(data_path, file)
    f = open(file_name, 'r', encoding='latin-1', errors='ignore')
    data_file = f.read()
    f.close()

    data_file = rm_pattern.sub('', data_file) # Remove &#0 since XML does not support these characters 
    data_file = rm2_pattern.sub('', data_file) # Remove "Reuter" which occurs at the end of each BODY field

    file_documents = doc_pattern.findall(data_file) # Extract the documents in the file
    documents += file_documents # Add file documents to all documents


# Preprocess the documents and form the dictionary
term_dict = preprocess(documents)

# Save the term dictionary to a pickle file
with open('term_dict.pkl', 'wb') as fp:
    pickle.dump(term_dict, fp)