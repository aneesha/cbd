from twython import Twython

#Setup API Keys
app_key = ""
app_secret = ""
oauth_token = ""
oauth_token_secret = ""

twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

# see https://dev.twitter.com/rest/reference/get/search/tweets for search options
results = twitter.search(q="#GoT", count=100)
for tweet in results['statuses']:
    body = tweet['text']
    id = tweet['id']
    timestamp = tweet['created_at']
    location = tweet['user']['location']
    userid = tweet['user']['id']
    username = tweet['user']['screen_name']
    print id, timestamp, location, userid, username, body
