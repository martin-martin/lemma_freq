
# coding: utf-8

# In[18]:

import os
import re
import time
import logging
import gzip
import json
import pandas as pd
from pprint import pformat
import xml.etree.ElementTree as ET


# In[2]:

# set up logging
logging.basicConfig(filename="word_freq.log", filemode="w", format="%(asctime)s %(message)s", level=logging.DEBUG)
logging.info("================= STARTED RUNNING =================")
logging.info("")
# measure process time
t_proc = time.clock()
# measure real time elapsed
t_wall = time.time()


# In[3]:

# fetches every OPUS file in all subdirectories
file_list = []
for root, dirs, files in os.walk("corpora/OPUS_es"):
    for file in files:
        if file.endswith(".gz"):
             file_list.append(os.path.join(root, file))


# In[ ]:

# testing
#file_list = file_list[:2]
#file_list


# In[5]:

# the dict that will hold all the info
word_freq = dict()
# a regex to exclude punctuation
non_words = re.compile(r"[\W\d]+")


# In[16]:

def get_frequency(tree, word_freq, non_words):
    """parses the XML ElementTree and creates a count of word occurences."""
    start_time = time.time()
    try:
        root = tree.getroot()
        tok_count, word_count = 0, 0 # initialize counts for stats
        current_length = len(word_freq)
        for word in root.iter("w"): # finds recusively all <w> tags (contain the words)
            tok_count += 1
            # get the current word token and discard capitalization
            token = word.text.lower()
            if not re.search(non_words, token): # exclude special chars & punctuation
                word_count += 1
                # create count entry or add 1 if it is already there
                word_freq[token] = word_freq.get(token, 0) + 1
    except:
        logging.warning("______WARNING: file not processed______")
        logging.warning("something went wrong inside the ElementTree...")
    logging.info("--- worked for {0} seconds ---".format(time.time() - start_time))
    logging.info("processed {0} tokens of which {1} were word tokens".format(tok_count, word_count))
    new_length = len(word_freq)
    logging.info("added {0} words to word dict; new length: {1}".format(new_length - current_length, new_length))
    return word_freq


# In[19]:

for zip_file in file_list:
    with gzip.open(zip_file, "rb") as xml_file:
        logging.info("")
        logging.info("FILE -------> {0}".format(xml_file))
        try:
            tree = ET.parse(xml_file)
            get_frequency(tree, word_freq, non_words)
        except:
            logging.warning("______WARNING: file {0} not processed______".format(xml_file))
            logging.warning("probably it is empty.")


# In[ ]:

logging.info("")
logging.info("")
logging.info("================= ******* THE END ******** =================")
logging.info("seconds process time: {0}".format(time.clock() - t_proc))
logging.info("seconds real time: {0}".format(time.time() - t_wall))


# In[ ]:

# define the directory to save the outputs
output_dir = "output_wf"
try:
    os.mkdir(output_dir)
except:
    pass


# In[ ]:

# save also the full frequency dict
with open(output_dir + "/word_frequency.json", "w") as f:
    json.dump(word_freq, f)


# In[ ]:

# sort the dict values according to frequency and keep the top 10000
fdf = pd.DataFrame(list(word_freq.items()), columns=["word", "frequency"])
sorted_fdf = fdf.sort_values(by=["frequency"], ascending=[False])
top_10000_fdf = sorted_fdf[:10000]
top_10000_fdf.to_csv(output_dir + "/top_10000.csv", encoding="utf-8")

