
# coding: utf-8

# # Creating a Spanish Lemma-Frequency list from Open Source corpora

# In[1]:

import re
import os
import gzip
import time
import operator
import json
import logging
import pandas as pd
from pprint import pformat
import xml.etree.ElementTree as ET


# In[2]:

# set up logging
logging.basicConfig(filename="lemma_freq.log", format="%(asctime)s %(message)s", level=logging.DEBUG)
logging.info("================= STARTED RUNNING =================")
logging.info("")
# measure process time
t_proc = time.clock()
# measure real time elapsed
t_wall = time.time()


# ## Fetch many files

# In[3]:

base_dir = "corpora/OPUS_es"
subfolders = os.listdir(base_dir)
dig_deeper = "xml/es"
subfolders.remove('.DS_Store')
subfolders


# In[ ]:

# fetches every OPUS file in all the subdirectories
file_list = []
for root, dirs, files in os.walk("corpora/OPUS_es"):
    for file in files:
        if file.endswith(".gz"):
             file_list.append(os.path.join(root, file))


# In[6]:

# short list for testing
test_list = file_list[:5]


# ## Initialize all things

# In[7]:

# the dicts that will hold all the info
lemma_freq = dict()
what_lems = dict()
# a regex to exclude punctuation
non_words = re.compile(r"[\W\d]+")


# In[8]:

def fetch_frequency(tree, lemma_freq, what_lems, non_words):
    # initialize some stats
    start_time = time.time()
    s_count = 0
    t_count = 0
    # root the tree
    root = tree.getroot()
    # root[1] accesses the <body> of the XML file, where the text resides
    for sent in root[1]:
        # count introduced for keeping track
        s_count += 1
        if sent.tag == "s":
            for word in sent:
                t_count += 1
                # get the current word token and discard capitalization
                token = word.text.lower()
                # avoid adding sentence delimiters to the word dictionary
                if not re.search(non_words, token):
                    lemma = word.get("lem")
                    # not every word has a lemma form!
                    if type(lemma) == type(None):
                        # use the word itself as dict key instead
                        # check whether the key exists (initialize it with 0 if not) and add 1 to the count
                        lemma_freq[token] = lemma_freq.get(token, 0) + 1
                        # create a set of tokens to the lemma key (for controlling the lemmatization work)
                        what_lems[token] = what_lems.get(token, set()).union({token})
                    # otherwise we collect the lemma info
                    else:    
                        lemma_freq[lemma] = lemma_freq.get(lemma, 0) + 1
                        # add to word list to retrace what words the lemmas came from
                        what_lems[lemma] = what_lems.get(lemma, set()).union({token})
    logging.info("--- worked for {0} seconds ---".format(time.time() - start_time))
    logging.info("processed {0} sentences with all together {1} word tokens".format(s_count, t_count))
    return lemma_freq, what_lems


# ## Execute the program

# In[9]:

for zip_file in test_list:
#for zip_file in file_list:
    with gzip.open(zip_file, "rb") as xml_file:
        try:
            tree = ET.parse(xml_file)
            logging.info("processing {0}...".format(zip_file))
            lemma_freq, what_lems = fetch_frequency(tree, lemma_freq, what_lems, non_words)
            logging.info("current length of lemma freq dict: {0}".format(len(lemma_freq)))
            logging.info("")
        except:
            logging.warning("*****ATTENTION***** Mistake in the following file *****ATTENTION*****")
            logging.info("{0}".format(zip_file))
            logging.info("")


# In[10]:

logging.info("================= FINISH LINE =================")
logging.info("seconds process time: {0}".format(time.clock() - t_proc))
logging.info("seconds real time: {0}".format(time.time() - t_wall))
logging.info("")
# start a new timer to time the calculations
t_stats = time.time()


# In[11]:

# how many of the processed words have inflections?
count = 0
for key, value in what_lems.items():
    if len(value) == 1:
        count += 1
logging.info("================= STATS, DUDE! =================")
logging.info("from the {0} lemmas {1} have inflections and {2} are just single words".format(len(what_lems), len(what_lems) - count, count))
logging.info("YO!")


# In[12]:

# start a new timer to time the calculations
t_files = time.time()

# define the directory to save the outputs
output_dir = "outputs"
try:
    os.mkdir(output_dir)
except:
    pass



# In[13]:

# check up on how the lemmatizations went
try:
    with open(output_dir + "/check_lems.json", "w") as f:
        json.dump(what_lems, f)
except:
    logging.warning("*****ATTENTION***** failed to write file *****ATTENTION*****")
    with open(output_dir + "/check_lems.txt", "w") as f:
        f.write(pformat(what_lems))


# In[14]:

# save also the full frequency dict
try:
    with open(output_dir + "/full_frequency.json", "w") as f:
        json.dump(lemma_freq, f)
except:
    logging.warning("*****ATTENTION***** failed to write file *****ATTENTION*****")
    with open(output_dir + "/full_frequency.txt", "w") as f:
        f.write(pformat(lemma_freq))


# In[15]:

# sort the dict values according to frequency and keep the top 5000
fdf = pd.DataFrame(list(lemma_freq.items()), columns=["word", "frequency"])


# In[17]:

sorted_fdf = fdf.sort_values(by=["frequency"], ascending=[False])
top_5000_fdf = sorted_fdf[:5000]
top_5000_fdf.to_csv(output_dir + "/top_5000.csv", encoding="utf-8")


# In[18]:

logging.info("================= ******* THE END ******** =================")
logging.info("seconds process time: {0}".format(time.clock() - t_proc))
logging.info("seconds real time: {0}".format(time.time() - t_wall))

