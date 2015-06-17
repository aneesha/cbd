# cbd - Cyberbullying Detection System

## About the project
This project was funded by a small grant provided by AUDA Foundation for a project entitled [Developing an online cloud-based cyberbullying detection system](http://www.audafoundation.org.au/grant-recipients/2013-grant-recipients/university-of-technology-sydney/) to Bhuva Narayan at UTS.

## What is included in the project?
* The project consists of a web-based application build in django (i.e. Python) that includes a dashboard for users to monitor cyberbullying (located in the cbd_project folder). 
* A machine learning classification algorithm (eg Support Vector Machine) can be trained to identify cyberbullying messages and then the classified messages can be imported into a database and is summarised on a dashboard. 
* The dashboard displays timeseries data, topic models (for cyberbullying messages and non cyber bullying messages) and a summary of the affective dimensions found in the test messages (for cyberbullying messages and non cyber bullying messages)
* Cron scripts (in the cronscripts) folder that must be scheduled to perform topic modeling and affective sentiment analysis (i.e. topicmodelandaffectivelexicon.py)
* A moderation role that is able to mark classified messages as mis-classified. 
* A sample python script to get data from Twitter (i.e. injest_twitter.py)

![Dashbaord](https://github.com/aneesha/cbd/blob/master/dashboard.png "Cyberbullying Dashboard")

## Installation Requirements
* Django
* gensim (for LDA topic modeling)
* django-qsstats-magic for timeseries display for graphing (https://pypi.python.org/pypi/django-qsstats-magic/0.7.2)
* twython (for running injest_twitter.py)

## Building a Classifier
In order to build a cyberbullying classifier a manually labelled dataset is required. A few labeled datasets are available (http://chatcoder.com/DataDownload) but it is recommended that you create and label your own dataset based upon the social media platform that you need to integrate with. Weka can be used to train and evaluate the classification algorithm. It is recommended that training and testing be performed with a Support Vector Machine, Mutinomial Naive Bayes and Random Forest. A good tutorial to follow is https://www.youtube.com/watch?v=IY29uC4uem8

## Topic Modeling and Affective Sentiment Analysis
* The gensim library is used to perform topic modeling using the Latent Dirichlet Allocation algorithm. The dashboard displays topics for non cyberbullying messages and cyberbullying messages. 10 topics are displayed along with 5 of the top words in the topic.
* The affective sentiment analysis uses a publically available NRC Word-Emotion Association Lexicon - Version 0.92 (http://www.saifmohammad.com/WebPages/ResearchInterests.html). Words in the corpus are matched to the lexicon and counted for both non cyberbullying messages and cyberbullying messages in topicmodelandaffectivelexicon.py. The resulting counts across the affective dimensions are displayed on a radar plot on the dashboard.

## Dashboard Template
The project uses the sb-admin2 twitter bootstrap admin template (http://startbootstrap.com/template-overviews/sb-admin-2/). 


