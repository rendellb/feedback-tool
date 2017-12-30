from ConfigParser import RawConfigParser
from io import BytesIO
from random import randint
from yagmail import SMTP
from functools import update_wrapper, wraps
from datetime import timedelta, tzinfo
from os import listdir
from os.path import isfile, join
from applicationDB import *

with open('configs/config.yaml') as f:
    sample_config = f.read()

config = RawConfigParser(allow_no_value=True)
config.readfp(BytesIO(sample_config))

appUser = config.get('appdb', 'user')
appPWD = config.get('appdb', 'passwd')
appDB = config.get('appdb', 'db')
appHost = config.get('appdb', 'host')
        
def email(recipient, subject, contents):
    yag = yagmail.SMTP('user@rtbanzon.com', 'password')
    yag.send(recipient, subject, contents)

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

def assign():
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    feedback = adb.getUnanswered()
    leads = adb.getLeadData()
    managers = adb.getManagers()
    ops = getOps()
    seniors = getSeniors()
    adb.autoPublish()
    adb.closeConnection()
    
    now = datetime.datetime.now()
    
    if basePath == '/opt/coe':
        now = datetime.datetime.now() - timedelta(hours=7)
    
    dow = str(now.strftime('%A'))[:3]
    today = now.date()
    
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    
    for row in feedback:
        updated = datetime.datetime.strptime(str(row['updated']), '%Y-%m-%d %H:%M:%S')
        created = datetime.datetime.strptime(str(row['created']), '%Y-%m-%d %H:%M:%S')
        assign = False
        assignee = ''
        
        if row['queue'] == 'Operations':
            ops = getOps()
            if row['assignee'] not in ops:
                try:
                    if updated < now - timedelta(hours=2):
                        assign = True
                except:
                    pass
                
                if assign:
                    if len(ops) > 0:
                        select = randint(0, len(ops) - 1)
                        assignee = ops[select]
        elif row['level'] == 2:
            if row['assignee'] not in leads:
                assign = True
                
            else:
                try:
                    if created < now - timedelta(days=2):
                        adb.assignFeedback(row['uuid'], 'open')
                    elif updated < now - timedelta(hours=5):
                        assign = True
                except:
                    pass

            if assign:
                activeLeads = []
                for lead in leads:
                    days = lead['days'].split(',')

                    if dow in days:
                        try:
                            start = datetime.datetime.strptime(str(today) + ' ' + lead['start'], '%Y-%m-%d %H:%M:%S')
                            end = datetime.datetime.strptime(str(today) + ' ' + lead['end'], '%Y-%m-%d %H:%M:%S')

                            if end < start:
                                end += timedelta(days=1)

                            if start < now and now < end:
                                if lead['site'] == 2:
                                    activeLeads.append(lead)
                        except:
                            pass
                
                if row['queue'] != 'General':
                    subLeads = []
                    for lead in activeLeads:
                        if row['queue'][:3] in adb.getCohorts(lead['email']):
                            subLeads.append(lead)
                    if len(subLeads) > 0:
                        select = randint(0, len(subLeads) - 1)
                        assignee = subLeads[select]['email']
                else:
                    if len(activeLeads) > 0:
                        select = randint(0, len(activeLeads) - 1)
                        assignee = activeLeads[select]['email']
        elif row['level'] == 3:
            if row['assignee'] not in managers:
                assign = True
            else:
                try:
                    if created < now - timedelta(days=5):
                        adb.assignFeedback(row['uuid'], 'open')
                    elif updated < now - timedelta(hours=5):
                        assign = True
                except:
                    pass
            
            if assign:
                if row['queue'] != 'General':
                    subManagers = []
                    for manager in managers:
                        if row['queue'][:3] in adb.getCohorts(manager):
                            subManagers.append(manager)
                            
                    if len(subManagers) > 0:
                        select = randint(0, len(subManagers) - 1)
                        assignee = subManagers[select]
                else:
                    select = randint(0, len(managers) - 1)
                    assignee = managers[select]
        elif row['level'] >= 4:
            if row['assignee'] not in seniors:
                select = randint(0, len(seniors) - 1)
                assignee = seniors[select]
            
        if assignee != '':
            emailStr = ''
            emailStr += 'New feedback has been assigned to you in <a href="https://feedback-tool.rtbanzon.com/lead">the Feedback Tool</a>!'
            emailStr += '<br />'
            emailStr += '<br /><b>Queue:</b> ' + row['queue']
            emailStr += '<br /><b>Level:</b> ' + str(row['level'])
            emailStr += '<br /><b>Feedback:</b> ' + row['feedback']
            emailStr += '<br /><br />This feedback will remained assigned to you for the next 5 hours. If you\'re unable to respond to it at the moment but will be able to do so later, <b>Claim</b> it to keep it in your queue for 48 hours.'
            if basePath == '/opt/coe':
                email(str(assignee), 'Feedback Tool - New Feedback!', emailStr)
            else:
                email('banzon@rtbanzon.com', 'Feedback Tool - New Feedback!', emailStr)

            adb = ApplicationDB(appHost, appDB, appUser, appPWD)
            adb.assignFeedback(row['uuid'], assignee)
            adb.closeConnection()

def lengthOfTime():
    adb = ApplicationDB(appHost, appDB, appUser, appPWD)
    feedback = adb.getAnswered()
    adb.closeConnection()
    
    dateTotal = ''
    for row in feedback:
        diff = datetime.datetime.strptime(row['updated'], '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime.strptime(row['created'], '%Y-%m-%d %H:%M:%S.%f')
        
        if diff.total_seconds() / 60 / 60 / 24 > 7:
            print row
        if dateTotal == '':
            dateTotal = diff
        else:
            dateTotal += diff
            
    print (dateTotal.total_seconds() / len(feedback)) / 60 / 60 / 24