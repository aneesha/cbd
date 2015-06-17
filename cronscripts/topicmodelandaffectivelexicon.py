# Generate a topic model for messages containing
# ---- Cyberbullying Traces
# ---- No Cyberbullying Traces
# Calculate words counts against an affective lexicon for
# ---- Cyberbullying Traces
# ---- No Cyberbullying Traces

from gensim import corpora, models, similarities
from collections import defaultdict
from pprint import pprint
from sqlalchemy.engine import create_engine
import json

def save_summaryobject (table, row):

    keys = row.keys();
    sql = "INSERT INTO " + table + " ("
    sql = sql + ", ".join(keys)
    sql = sql + ") VALUES ("
    sql = sql + ", ".join([ ("'" + str(row[key]) + "'") for key in keys])
    sql = sql + ")"

    id = connection.execute(sql);

    return id

def loadStopWords(stopWordFile):
    stopWords = []
    for line in open(stopWordFile):
        for word in line.split( ): #in case more than one per line
            stopWords.append(word)
    return stopWords

def loadAffectiveDictionary(affectiveWordFile):
    affectiveWords = {}
    linecount = 0
    for line in open(affectiveWordFile):
        if linecount>2:
            words = line.split("\t")
            if words[0] not in affectiveWords:
                affectiveWords[words[0]] = {'anger': 0, 'anticipation': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'negative': 0, 'positive': 0, 'sadness': 0, 'surprise': 0, 'trust':0 }
            affective_senses = affectiveWords[words[0]]
            affective_senses[words[1]] = int(words[2])
        linecount = linecount + 1
    return affectiveWords

# calculate affective senses counts
def affective_sense_counts(texts, affectivelexicon_dict):
	affective_senses_counts = {'anger': 0, 'anticipation': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'negative': 0, 'positive': 0, 'sadness': 0, 'surprise': 0, 'trust':0 }
	for text in texts:
		for token in text:
			if token in affectivelexicon_dict:
				affective_senses = affectivelexicon_dict[token]
			for sense in affective_senses_counts:
				affective_senses_counts[sense] = affective_senses_counts[sense] + int(affective_senses[sense])

	affective_counts_json =  json.dumps(affective_senses_counts)
	return affective_counts_json

# remove common words and tokenize
def remove_stopwords(documents):
    stoplist = loadStopWords('englishstop.txt')
    texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]

    # remove words that appear only once
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1

    texts = [[token for token in text if frequency[token] > 1] for text in texts]

    return texts

def get_LDAasJSON(texts):
    # Make dictionary
    dictionary = corpora.Dictionary(texts)
    #dictionary.save('test.dict') # store the dictionary, for future reference

    #Create and save corpus
    corpus = [dictionary.doc2bow(text) for text in texts]
    #corpora.MmCorpus.serialize('test.mm', corpus) # store to disk, for later use

    #Run LDA
    model = models.ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=20)
    #Save Model
    #model.save('ldamodel.m')

    tmp = model.show_topics(num_topics=20, num_words=5, log=False, formatted=False)

    #print tmp
    json_tm = json.dumps(tmp)

    return json_tm

#load affective text lexicon
affectivelexicon_dict = loadAffectiveDictionary('NRC-emotion-lexicon-wordlevel-alphabetized-v0.92.txt')

# Create database connection
documents = []
engine = create_engine("sqlite:///cyber.sqlite3")
connection = engine.connect()

# Delete stored topics and affective lexicon counts
connection.execute("DELETE FROM cbd_mlcache");

# load documents (i.e. posts or messages containing cyberbullying traces) from database
sql = "SELECT id, body FROM cbd_processedsocialmediamessage WHERE has_bullying='Yes'"
result = connection.execute(sql);
for row in result:
    documents.append(row[1].replace('#039;',''))

cyberbullyingdocs = remove_stopwords(documents)

documents = []
# load documents (i.e. posts or messages NOT containing cyberbullying traces) from database
sql = "SELECT id, body FROM cbd_processedsocialmediamessage WHERE has_bullying='No'"
result = connection.execute(sql);
for row in result:
    documents.append(row[1].replace('#039;',''))

noncyberbullyingdocs = remove_stopwords(documents)

topic_model_json = get_LDAasJSON(noncyberbullyingdocs)
topic_model_cyberbullying_json = get_LDAasJSON(cyberbullyingdocs)

affective_counts_json = affective_sense_counts(noncyberbullyingdocs, affectivelexicon_dict)
affective_counts_cyberbullying_json = affective_sense_counts(cyberbullyingdocs, affectivelexicon_dict)

record = {"topic_model_json": topic_model_json.replace("'", "''"), "topic_model_cyberbullying_json": topic_model_cyberbullying_json.replace("'", "''"), "affective_counts_json": affective_counts_json.replace("'", "''"), 'affective_counts_cyberbullying_json': affective_counts_cyberbullying_json.replace("'", "''")}
save_summaryobject ("cbd_mlcache", record)
