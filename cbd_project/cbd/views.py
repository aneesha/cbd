from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Count

import json
import datetime

from django.db.models import Max
from django.db.models import Min

import datetime, qsstats

from cbd.models import ProcessedSocialMediaMessage, MLCache, IncorrectClassification

from django.core import serializers
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

def index(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/dashboard/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('cbd/index.html', {}, context)

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/cbd/index.html')

@login_required
def moderate(request):
    context = RequestContext(request)
    threadid = request.GET.get('threadid')

    user = request.user
    userid = user.id

    messages = SocialMediaMessage.objects.filter(threadid=threadid).order_by('id')

    coded_messages = SocialMediaCodedMessage.objects.filter(userid=userid, threadid=threadid)
    coded_messages_dict = {}

    for msg in coded_messages:
        coded_messages_dict[msg.postid] = {"comment": msg.message_comment, "role": msg.author_role, "evidence": msg.bullying_evidence_in_message, "usedurbandict": msg.message_contains_urban_dictionary_acronym  }

    saved_codes_json = json.dumps(coded_messages_dict)

    context_dict = {'messages':  messages, 'threadid': threadid, 'saved_codes_json': saved_codes_json}

    return render_to_response('cbd/messages.html', context_dict, context)

@csrf_exempt
@require_http_methods(["POST"])
def save_coding(request):
    user = request.user
    userid = user.id
    postid = request.POST['postid']
    evidenceoption = request.POST['evidenceoption']
    acronymcheckbox = request.POST['acronymcheckbox']
    comment = request.POST['comment']
    role = request.POST['role']
    threadid = request.POST['threadid']
    urbandictcheckbox = False
    if acronymcheckbox=="true":
       urbandictcheckbox = True
    codedMessage = SocialMediaCodedMessage(userid=userid, postid=postid, author_role=role, message_comment=comment, bullying_evidence_in_message=evidenceoption, message_contains_urban_dictionary_acronym=urbandictcheckbox, threadid=threadid)
    codedMessage.save()
    return HttpResponse("Saved")

@login_required
def dashboard(request):
    # Get data for dashboard widgets
    nosocialmediausers = ProcessedSocialMediaMessage.objects.values_list('username', flat=True).distinct().count() #SocialMediaUser.objects.count()
    nosocialmediamessages = ProcessedSocialMediaMessage.objects.count() #SocialMediaMessage.objects.count()

    nobullytraces = ProcessedSocialMediaMessage.objects.filter(has_bullying='Yes').count() #SocialMediaMessage.objects.filter(bullying_trace=True).count()

    missclassifiedcount = IncorrectClassification.objects.count()

    #grouped count of bullying roles
    '''
    bullyrolecount = #SocialMediaMessage.objects.values('author_role').annotate(Count('author_role'))
    #print json.dumps(bullyrolecount, ensure_ascii=False)
    bullyrolecount_dict="["
    for bullyrole in bullyrolecount:
        bullyroleobj_dict="{'label': '" + bullyrole["author_role"] + "', 'value': '" + str(bullyrole["author_role__count"]) + "'},"
        bullyrolecount_dict = bullyrolecount_dict + bullyroleobj_dict
    bullyrolecount_dict= bullyrolecount_dict + "]"
    '''
    # dummy values are added as no labled data is available for training a model
    bullyrolecount_dict="["
    bullyrolecount_dict = bullyrolecount_dict + "{'label': 'Bystander', 'value': '1'},"
    bullyrolecount_dict = bullyrolecount_dict + "{'label': 'Reinforcer', 'value': '1'},"
    bullyrolecount_dict = bullyrolecount_dict + "{'label': 'Assistant', 'value': '1'},"
    bullyrolecount_dict = bullyrolecount_dict + "{'label': 'Defender', 'value': '2'},"
    bullyrolecount_dict = bullyrolecount_dict + "{'label': 'Bully', 'value': '12'},"
    bullyrolecount_dict = bullyrolecount_dict + "{'label': 'Victim', 'value': '17'},"
    bullyrolecount_dict = bullyrolecount_dict + "{'label': 'Reporter', 'value': '4'},"
    bullyrolecount_dict = bullyrolecount_dict + "{'label': 'Accuser', 'value': '2'},"
    bullyrolecount_dict = bullyrolecount_dict + "{'label': 'None', 'value': '100'},"
    bullyrolecount_dict= bullyrolecount_dict + "]"

    maxdate = ProcessedSocialMediaMessage.objects.all().aggregate(Max('date'))
    mindate = ProcessedSocialMediaMessage.objects.all().aggregate(Min('date'))

    qs = ProcessedSocialMediaMessage.objects.filter(has_bullying='Yes')

    qss = qsstats.QuerySetStats(qs, 'date')

    start, end = mindate['date__min'], maxdate['date__max']
    sales_by_month_ts = qss.time_series(start, end, interval='months')
    MonthL = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    months_dict="["
    for t in sales_by_month_ts:
        monthobj_dict="{'month': '" + t[0].strftime("%Y-%m") + "', 'incidents': '" + str(t[1]) + "'},"
        months_dict = months_dict + monthobj_dict
    months_dict= months_dict + "]"
    # timeseries for last 7 days
    today = maxdate['date__max'] # datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=7)

    time_series = qss.time_series(seven_days_ago, today)
    DayL = ['Mon','Tues','Wed','Thurs','Fri','Sat','Sun']
    weekts_dict="["
    for t in time_series:
        dayobj_dict="{'y': '" + DayL[t[0].weekday()] + "', 'a': '" + str(t[1]) + "'},"
        weekts_dict = weekts_dict + dayobj_dict
    weekts_dict= weekts_dict + "]"

    #get most recent bullying incidents/traces
    recentincidents = ProcessedSocialMediaMessage.objects.filter(has_bullying='Yes').order_by('date')[:5]

    context = RequestContext(request)

    # load affective word counts
    mlcache = MLCache.objects.all()[:1]
    topic_model_json = ''
    topic_model_cyberbullying_json = ''
    affective_counts_json = ''
    affective_counts_cyberbullying_json = ''

    for x in mlcache:
        affective_counts_json = x.affective_counts_json
        affective_counts_cyberbullying_json = x.affective_counts_cyberbullying_json
        topic_model_json = x.topic_model_json
        topic_model_cyberbullying_json = x.topic_model_cyberbullying_json

    affective_dict = json.loads(affective_counts_json)

    affective_count_list = [] #must be in order
    affective_count_list.append(affective_dict['sadness'])
    affective_count_list.append(affective_dict['anticipation'])
    affective_count_list.append(affective_dict['disgust'])
    affective_count_list.append(affective_dict['positive'])
    affective_count_list.append(affective_dict['anger'])
    affective_count_list.append(affective_dict['joy'])
    affective_count_list.append(affective_dict['fear'])
    affective_count_list.append(affective_dict['trust'])
    affective_count_list.append(affective_dict['negative'])
    affective_count_list.append(affective_dict['surprise'])

    affective_count_list_str = ','.join(map(str, affective_count_list))

    # Load and print up to 10 Topics
    tm_dict = json.loads(topic_model_json)
    count = 1
    tm_str = "<ul>"
    for tp in tm_dict:
        tm_str = tm_str + "<li><strong>Topic %d</strong></br>" % (count)
        words_in_topic = []
        for t in tp:
            words_in_topic.append(t[1])
        wrds = ','.join(map(str, words_in_topic))
        tm_str = tm_str + wrds + "</li>"
        count = count + 1
        if count==11: break
    tm_str = tm_str + "</ul>"

    affective_cyber_dict = json.loads(affective_counts_cyberbullying_json)

    affective_count_list = [] #must be in order
    affective_count_list.append(affective_cyber_dict['sadness'])
    affective_count_list.append(affective_cyber_dict['anticipation'])
    affective_count_list.append(affective_cyber_dict['disgust'])
    affective_count_list.append(affective_cyber_dict['positive'])
    affective_count_list.append(affective_cyber_dict['anger'])
    affective_count_list.append(affective_cyber_dict['joy'])
    affective_count_list.append(affective_cyber_dict['fear'])
    affective_count_list.append(affective_cyber_dict['trust'])
    affective_count_list.append(affective_cyber_dict['negative'])
    affective_count_list.append(affective_cyber_dict['surprise'])

    affective_cyber_count_list_str = ','.join(map(str, affective_count_list))

    # Load and print up to 10 Topics
    tm_dict = json.loads(topic_model_cyberbullying_json)
    count = 1
    tm_cyber_str = "<ul>"
    for tp in tm_dict:
        tm_cyber_str = tm_cyber_str + "<li><strong>Topic %d</strong></br>" % (count)
        words_in_topic = []
        for t in tp:
            words_in_topic.append(t[1])
        wrds = ','.join(map(str, words_in_topic))
        tm_cyber_str = tm_cyber_str + wrds + "</li>"
        count = count + 1
        if count==11: break
    tm_cyber_str = tm_cyber_str + "</ul>"

    context_dict = {'tm_str': tm_str, 'tm_cyber_str':tm_cyber_str, 'affective_count_list_str': affective_count_list_str, 'affective_cyber_count_list_str': affective_cyber_count_list_str, 'nosocialmediausers': nosocialmediausers, 'nosocialmediamessages': nosocialmediamessages, 'nobullytraces': nobullytraces, 'missclassifiedcount': missclassifiedcount, 'rolejson': bullyrolecount_dict, 'recentincidents': recentincidents, 'weekts_dict': weekts_dict, 'months_dict': months_dict}

    return render_to_response('cbd/dashboard.html', context_dict, context)
