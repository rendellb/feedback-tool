import ConfigParser, io, sys, time, os, requests, datetime, threading, shutil, yagmail, csv, urllib2, logging, random, string, uuid
from flask import Flask, jsonify, render_template, request, make_response, current_app, Response, json, redirect, url_for, send_from_directory, escape, session, abort
from werkzeug import secure_filename
from functools import update_wrapper, wraps
from datetime import timedelta, tzinfo
from os import listdir
from os.path import isfile, join
from applicationDB import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '7dQRnRbeU95F6xpx'

localUser = 'rendell@rtbanzon.com'

with open('configs/config.yaml') as f:
    sample_config = f.read()

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(io.BytesIO(sample_config))

appUser = config.get('appdb', 'user')
appPWD = config.get('appdb', 'passwd')
appDB = config.get('appdb', 'db')
appHost = config.get('appdb', 'host')
        
def getAuth():
    return localUser
    
def randomString():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', request.json['_csrf_token'])
        if not token or token != request.json['_csrf_token']:
            abort(402)

def generateCSRF():
    if '_csrf_token' not in session:
        session['_csrf_token'] = randomString()
        session.permanent = True
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generateCSRF

def check_auth(user):
    whitelist = []
    
    managers = whitelistL3() 
    for manager in managers:
        whitelist.append(manager)
        
    leads = whitelistL2()
    for lead in leads:
        whitelist.append(lead)
        
    admins = whitelistL4()
    for admin in admins:
        whitelist.append(admin)
    
    if user in whitelist:
        return True
    
    return False

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        global authEmail
        authEmail = getAuth()
        if not check_auth(authEmail):
            return render_template('403.html')
        return f(*args, **kwargs)
    return decorated

def getOtherAdmins():
    whitelist = [
        'other@rtbanzon.com'
    ]
    
    return whitelist

def getSeniors():
    whitelist = [
        'senior@rtbanzon.com',
    ]
    
    return whitelist

def getOps():
    whitelist = [
        'ops@rtbanzon.com'
    ]
    
    return whitelist
    
def whitelistL4():
    whitelist = [
        'rendell@rtbanzon.com'
    ]
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    whitelist += adb.getAdmins()
    adb.closeConnection()
    
    whitelist += getSeniors()
    whitelist += getOps()
    whitelist += getOtherAdmins()
    
    return whitelist

def whitelistL3():
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    whitelist = adb.getManagers()
    adb.closeConnection()
    
    return whitelist

def whitelistL2():
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    whitelist = adb.getLeads()
    adb.closeConnection()
    
    return whitelist

def getLevel(email):
    level = 1
    
    if email in whitelistL4():
        level = 4
    if email in whitelistL3():
        level = 3
    if email in whitelistL2():
        level = 2
        
    return level

def whitelisted(email):
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    adb.logAccess(email)
    cohort = adb.getCohort(email)
    adb.closeConnection()
    
    whitelist = whitelistL2()
    whitelist += whitelistL3()
    whitelist += whitelistL4()
    
    if email in whitelist:
        return True
    
    return False
    #try:
        #if(cohort[0] == 104 or cohort[0] == 6):
            #return True
        #else:
            #return False
    #except:
        #return False
    
def getCohorts(email):
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    cohorts = adb.getCohorts(email)
    adb.closeConnection()
    
    return cohorts
    
def assignment():
    import tasks
    tasks.assign()
    
@app.route('/')
def index():
    authEmail = getAuth()
    if whitelisted(authEmail):
        adb = ApplicationDB(appHost, appDB, appUser, appPWD)
        queue = adb.getCSRFeedback()
        upvotes = adb.getFeedbackUpvotes()
        upvotes2 = adb.getResponseUpvotes()
        flags = adb.getMyFlags(authEmail)
        adb.closeConnection()

        data = {'queue': queue, 'upvotes': upvotes, 'upvotes2': upvotes2, 'flags': flags}
        user = {'email': authEmail}
        return render_template('index.html', user=user, data=data)
    else:
        return render_template('403.html')

@app.route('/lead')
@requires_auth
def lead():
    authEmail = getAuth()
    level = getLevel(authEmail)
    cohorts = getCohorts(authEmail)
    
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    team = adb.getMyTeam(authEmail)
    queue = adb.getQueue(authEmail, level)
    upvotes = adb.getFeedbackUpvotes()
    openQueue = adb.getOpenQueue()
    reviewQueue = adb.getReviewQueue(team)
    modQueue = []
    amendQueue = []
    flags = []
    if level >= 3:
        modQueue = adb.modFeedback()
        amendQueue = adb.getAmendmentQueue(cohorts, level)
        flags = adb.getFlags()
    
    adb.closeConnection()
    adb.closeConnection()
    
    data = {'queue': queue, 'upvotes': upvotes, 'open': openQueue, 'mod': modQueue, 'review': reviewQueue, 'amend': amendQueue, 'flags': flags}
    user = {'email': authEmail, 'level': level}
    return render_template('lead.html', user=user, data=data)

@app.route('/mod')
@requires_auth
def mod():
    authEmail = getAuth()
    level = getLevel(authEmail)
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    queue = adb.modFeedback()
    adb.closeConnection()
    
    data = {'queue': queue}
    user = {'email': authEmail}
    return render_template('mod.html', user=user, data=data)
 
@app.route('/feedback', methods=['POST'])
def feedback():
    inquirer = 'anonymous'
    
    if request.json['identify'] == True:
        inquirer = getAuth()
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    adb.addFeedback(request.json['feedback'].encode('utf-8').strip(), inquirer, request.json['queue'])
    adb.closeConnection()
    
    response = {'status': 200, 'value': 'success'}
    return jsonify(response)

@app.route('/check', methods=['POST'])
def check():
    user = request.json['email']
    level = getLevel(user)
    cohorts = getCohorts(user)
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    data = adb.getQueue(user, level)
    adb.closeConnection()
    
    response = {'status': 200, 'rows': data}
    return jsonify(response)

@app.route('/data/claim', methods=['POST'])
def claim():
    uuid = request.json['uuid']
    user = getAuth()
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    adb.feedbackClaim(uuid, user)
    adb.closeConnection()
    
    response = {'status': status}
    return jsonify(response)

@app.route('/data/escalate', methods=['POST'])
def escalate():
    uuid = request.json['uuid']
    user = getAuth()
    level = getLevel(user)
    cohorts = getCohorts(authEmail)
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    feedback = adb.getFeedback(uuid)
    if len(feedback) == 1:
        currentLevel = feedback[0]['level'] + 1
        adb.feedbackEscalate(uuid, user, currentLevel)
    else:
        status = 404
    data = adb.getQueue(user, level)
    adb.closeConnection()
    
    response = {'status': status, 'results': data}
    return jsonify(response)

@app.route('/data/deescalate', methods=['POST'])
def deescalate():
    uuid = request.json['uuid']
    user = getAuth()
    level = getLevel(user)
    cohorts = getCohorts(authEmail)
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    feedback = adb.getFeedback(uuid)
    if len(feedback) == 1:
        currentLevel = feedback[0]['level'] - 1
        adb.feedbackEscalate(uuid, user, currentLevel)
    else:
        status = 404
    data = adb.getQueue(user, level)
    adb.closeConnection()
    
    response = {'status': status, 'results': data}
    return jsonify(response)

@app.route('/data/reassign', methods=['POST'])
def reassign():
    uuid = request.json['uuid']
    user = getAuth()
    queue = request.json['queue']
    level = getLevel(user)
    cohorts = getCohorts(authEmail)
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    adb.feedbackReassign(uuid, user, queue)
    data = adb.getQueue(user, level)
    adb.closeConnection()
    
    response = {'status': status, 'results': data}
    return jsonify(response)

@app.route('/data/submit', methods=['POST'])
def submit():
    uuid = request.json['uuid']
    user = getAuth()
    response = request.json['response'].encode('utf-8').strip()
    level = getLevel(user)
    cohorts = getCohorts(authEmail)
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    if level < 3:
        adb.addResponse(uuid, user, response)
    else:
        adb.addResponsePublished(uuid, user, response)
    data = adb.getQueue(user, level)
    adb.closeConnection()
    
    response = {'status': status, 'results': data}
    return jsonify(response)

@app.route('/data/amend', methods=['POST'])
def amend():
    uuid = request.json['uuid']
    user = getAuth()
    response = request.json['response'].encode('utf-8').strip()
    level = getLevel(user)
    cohorts = getCohorts(authEmail)
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    adb.addAmendment(uuid, user, response)
    amendQueue = []
    flags = []
    if level >= 3:
        amendQueue = adb.getAmendmentQueue(cohorts, level)
        flags = adb.getFlags()
    data = adb.getQueue(user, level)
    adb.closeConnection()
    
    response = {'status': status, 'results': data, 'flags': flags, 'amend': amendQueue}
    return jsonify(response)

@app.route('/data/submitcorrection', methods=['POST'])
def submitcorrection():
    uuid = request.json['uuid']
    ruuid = request.json['ruuid']
    user = getAuth()
    response = request.json['response'].encode('utf-8').strip()
    level = getLevel(user)
    cohorts = getCohorts(authEmail)
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    adb.correctResponse(uuid, ruuid, user, response)
    data = adb.getQueue(user, level)
    adb.closeConnection()
    
    response = {'status': status, 'results': data}
    return jsonify(response)

@app.route('/data/queue', methods=['GET'])
def queue():
    authEmail = getAuth()
    level = getLevel(authEmail)
    cohorts = getCohorts(authEmail)
    
    status = 200

    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    team = adb.getMyTeam(authEmail)
    queue = adb.getQueue(authEmail, level)
    reviewQueue = adb.getReviewQueue(team)
    openQueue = adb.getOpenQueue()
    modQueue = []
    if level >= 3:
        modQueue = adb.modFeedback()
    adb.closeConnection()
    adb.closeConnection()
    
    response = {'status': status, 'queue': queue, 'open': openQueue, 'mod': modQueue, 'review': reviewQueue}
    return jsonify(response)

@app.route('/data/allfeedback', methods=['GET'])
def allFeedback():
    authEmail = getAuth()
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    data = adb.getAllFeedback()
    adb.closeConnection()
    
    response = {'status': status, 'results': data}
    return jsonify(response)

@app.route('/data/mod', methods=['GET'])
def modFeedback():
    authEmail = getAuth()
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    data = adb.modFeedback()
    adb.closeConnection()
    
    response = {'status': status, 'results': data}
    return jsonify(response)

@app.route('/data/upvote', methods=['POST'])
def upvote():
    uuid = request.json['uuid']
    user = getAuth()
    action = request.json['action']
    association = request.json['type']
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    if action == 1:
        adb.upvoteFeedback(uuid, user, association)
    elif action == 0:
        adb.removeUpvote(uuid, user, association)
    upvotes = adb.getFeedbackUpvotes()
    upvotes2 = adb.getResponseUpvotes()
    adb.closeConnection()
    
    response = {'status': status, 'upvotes': upvotes, 'upvotes2': upvotes2}
    return jsonify(response)

@app.route('/data/flag', methods=['POST'])
def flag():
    uuid = request.json['uuid']
    user = getAuth()
    action = request.json['action']
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    if action == 1:
        adb.flagFeedback(uuid, user)
    elif action == 0:
        adb.removeFlag(uuid, user)
    adb.closeConnection()
    
    response = {'status': status}
    return jsonify(response)

@app.route('/data/modverify', methods=['POST'])
def modVerify():
    uuid = request.json['uuid']
    user = getAuth()
    verify = request.json['verify']
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    adb.verifyFeedback(uuid, user, verify)
    data = adb.modFeedback()
    adb.closeConnection()
    
    response = {'status': status, 'mod': data}
    return jsonify(response)

@app.route('/data/review', methods=['POST'])
def review():
    ruuid = request.json['ruuid']
    fuuid = request.json['fuuid']
    user = getAuth()
    confirm = request.json['confirm']
    comments = request.json['comments']
    assignee = request.json['assignee']
    
    reviewed = 2
    if confirm == 'approved':
        reviewed = 1
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    adb.completeReview(ruuid, user, reviewed, comments)
    adb.setClaim(fuuid, assignee)
    data = adb.modFeedback()
    adb.closeConnection()
    
    response = {'status': status, 'mod': data}
    return jsonify(response)

@app.route('/data/edit-submit', methods=['POST'])
def editSubmit():
    fuuid = request.json['fuuid']
    uuid = request.json['uuid']
    user = getAuth()
    response = request.json['response']
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    adb.editReview(uuid, fuuid, user, response)
    data = adb.modFeedback()
    adb.closeConnection()
    
    response = {'status': status, 'mod': data}
    return jsonify(response)

@app.route('/data/mark-correct', methods=['POST'])
def markCorrect():
    ruuid = request.json['ruuid']
    user = getAuth()
    
    status = 200
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    adb.markCorrect(ruuid, user)
    adb.closeConnection()
    
    response = {'status': status}
    return jsonify(response)

@app.route('/ping', methods=['POST'])
def ping():
    response = {'status': 200}
    return jsonify(response)

@app.route('/assign')
@requires_auth
def assignRouting():
    assignment()
    return 'Assigned'

@app.route('/health')
def health():
    return 'OK'
    
if __name__ == '__main__':
    app.run()