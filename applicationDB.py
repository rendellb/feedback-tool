import ConfigParser, io, sys, time, os, requests, datetime, threading, shutil, yagmail, csv, urllib2, logging, mysql.connector, random, string, sqlalchemy, uuid
from sqlalchemy import *
from mysql.connector import Error

class ApplicationDB:
    def __init__(self, host, dbName, user, pwd):
        self.user = user
        self.pwd = pwd
        self.host = host
        self.dbName = dbName
        self.createConn()
        
    def createConn(self):
        try:
            self.db = create_engine('mysql+mysqlconnector://' + self.user + ':' + self.pwd + '@' + self.host + '/' + self.dbName)
            self.metadata = MetaData(self.db)
            self.conn = self.db.connect()
            
            self.access = Table('access', self.metadata,
                Column('create_timestamp', String),
                Column('user_email', String),
            )
            
            self.submissions = Table('submissions', self.metadata,
                Column('create_timestamp', String),
                Column('uuid', String),
                Column('update_timestamp', String),
                Column('feedback', String),
                Column('queue', String),
                Column('moderator', String),
                Column('last_user', String),
                Column('level', String),
                Column('status_l2', String),
                Column('status_l3', String),
                Column('status_l4', String),
                Column('assignee', String),
                Column('inquisitor', String),
                Column('verified', String),
                Column('claimed', String),
                Column('deescalated', String),
                Column('reviewed', String)
            )
            
            self.upvotes = Table('upvotes', self.metadata,
                Column('create_timestamp', String),
                Column('uuid', String),
                Column('last_user', String),
                Column('association', String)
            )
            
            self.flags = Table('flags', self.metadata,
                Column('create_timestamp', String),
                Column('uuid', String),
                Column('last_user', String)
            )
            
            self.responses = Table('responses', self.metadata,
                Column('create_timestamp', String),
                Column('update_timestamp', String),
                Column('uuid', String),
                Column('feedback_uuid', String),
                Column('last_user', String),
                Column('response', String),
                Column('reviewed', String),
                Column('reviewer', String),
                Column('reviewer2', String),
                Column('notes', String),
                Column('correct', String)
            )
            
            self.papertrail = Table('papertrail', self.metadata,
                Column('create_timestamp', String),
                Column('uuid', String),
                Column('last_user', String)
            )
    
        except IOError:
            self.conn = ''
        except:
            raise
            
    def runQuery(self, query):
        self.db.execute(query)
        
    def logAccess(self, email):
        stmt = self.access.insert().values(
            create_timestamp = str(datetime.datetime.now()),
            user_email = str(email)
        )
        self.conn.execute(stmt)
        
    def addFeedback(self, feedback, inquisitor, queue):
        stmt = self.submissions.insert().values(
            create_timestamp = str(datetime.datetime.now()),
            uuid = str(uuid.uuid4()),
            feedback = str(feedback),
            level = 2,
            queue = str(queue),
            assignee = 'unassigned',
            verified = 0,
            inquisitor = inquisitor
        )
        self.conn.execute(stmt)
        
    def upvoteFeedback(self, uuid, user, association):
        stmt = self.upvotes.insert().values(
            create_timestamp = str(datetime.datetime.now()),
            uuid = str(uuid),
            last_user = str(user),
            association = str(association)
        )
        self.conn.execute(stmt)
        
    def removeUpvote(self, uuid, user, association):
        stmt = self.upvotes.delete().where(
            and_(
                self.upvotes.c.uuid == str(uuid),
                self.upvotes.c.last_user == str(user),
                self.upvotes.c.association == str(association)
            )
        )
        self.conn.execute(stmt)
        
    def flagFeedback(self, uuid, user):
        stmt = self.flags.insert().values(
            create_timestamp = str(datetime.datetime.now()),
            uuid = str(uuid),
            last_user = str(user)
        )
        self.conn.execute(stmt)
        
    def removeFlag(self, uuid, user):
        stmt = self.flags.delete().where(
            and_(
                self.flags.c.uuid == str(uuid),
                self.flags.c.last_user == str(user)
            )
        )
        self.conn.execute(stmt)
        
    def verifyFeedback(self, uuid, user, verify):
        stmt = self.submissions.update().where(
            self.submissions.c.uuid == str(uuid)
        ).values(
            update_timestamp = str(datetime.datetime.now()),
            moderator = str(user),
            last_user = str(user),
            verified = verify
        )
        self.conn.execute(stmt)
        
    def feedbackClaim(self, uuid, user):
        self.paperTrail(uuid, user)
        stmt = self.submissions.update().where(
            and_(
                self.submissions.c.uuid == str(uuid)
            )
        ).values(
            update_timestamp = str(datetime.datetime.now()),
            assignee = str(user),
            claimed = str(user)
        )
        self.conn.execute(stmt)
        
    def feedbackEscalate(self, uuid, user, level):
        self.paperTrail(uuid, user)
        stmt = self.submissions.update().where(
            and_(
                self.submissions.c.uuid == str(uuid)
            )
        ).values(
            update_timestamp = str(datetime.datetime.now()),
            level = str(level),
            last_user = str(user),
            assignee = 'unassigned'
        )
        self.conn.execute(stmt)
        
    def feedbackReassign(self, uuid, user, queue):
        self.paperTrail(uuid, user)
        stmt = self.submissions.update().where(
            and_(
                self.submissions.c.uuid == str(uuid)
            )
        ).values(
            update_timestamp = str(datetime.datetime.now()),
            queue = str(queue),
            last_user = str(user),
            assignee = 'unassigned'
        )
        self.conn.execute(stmt)
        
    def feedbackSubmit(self, uuid, user, response):
        self.paperTrail(uuid, user)
        stmt = self.submissions.update().where(
            and_(
                self.submissions.c.uuid == str(uuid)
            )
        ).values(
            update_timestamp = str(datetime.datetime.now()),
            last_user = str(user),
            reviewed = 0
        )
        self.conn.execute(stmt)
        
    def setClaim(self, uuid, assignee):
        stmt = self.submissions.update().where(
            and_(
                self.submissions.c.uuid == str(uuid)
            )
        ).values(
            update_timestamp = str(datetime.datetime.now()),
            claimed = assignee
        )
        self.conn.execute(stmt)
        
    def addResponse(self, fuuid, user, response):
        stmt = self.responses.insert().values(
            create_timestamp = str(datetime.datetime.now()),
            uuid = str(uuid.uuid4()),
            feedback_uuid = str(fuuid),
            last_user = str(user),
            response = str(response),
            reviewed = 0
        )
        self.conn.execute(stmt)
        
    def addResponsePublished(self, fuuid, user, response):
        stmt = self.responses.insert().values(
            create_timestamp = str(datetime.datetime.now()),
            uuid = str(uuid.uuid4()),
            feedback_uuid = str(fuuid),
            last_user = str(user),
            response = str(response),
            reviewed = 1
        )
        self.conn.execute(stmt)
        
    def addAmendment(self, fuuid, user, response):
        stmt = self.responses.insert().values(
            create_timestamp = str(datetime.datetime.now()),
            uuid = str(uuid.uuid4()),
            feedback_uuid = str(fuuid),
            last_user = str(user),
            response = str(response),
            reviewed = 1
        )
        self.conn.execute(stmt)
        
    def correctResponse(self, fuuid, ruuid, user, response):
        stmt = self.responses.insert().values(
            create_timestamp = str(datetime.datetime.now()),
            uuid = str(uuid.uuid4()),
            feedback_uuid = str(fuuid),
            last_user = str(user),
            response = str(response),
            reviewed = 0
        )
        self.conn.execute(stmt)
        
        stmt = self.responses.update().where(
            and_(
                self.responses.c.uuid == str(ruuid)
            )
        ).values(
            update_timestamp = str(datetime.datetime.now()),
            reviewed = 4
        )
        self.conn.execute(stmt)
        
    def markCorrect(self, ruuid, user):
        stmt = self.responses.update().where(
            and_(
                self.responses.c.uuid == str(ruuid)
            )
        ).values(
            update_timestamp = str(datetime.datetime.now()),
            reviewer2 = str(user),
            correct = 1
        )
        self.conn.execute(stmt)
        
    def completeReview(self, uuid, user, reviewed, comments):
        stmt = self.responses.update().where(
            and_(
                self.responses.c.uuid == str(uuid)
            )
        ).values(
            update_timestamp = str(datetime.datetime.now()),
            reviewer = str(user),
            reviewed = reviewed,
            notes = str(comments)
        )
        self.conn.execute(stmt)
        
    def editReview(self, ruuid, fuuid, user, response):
        stmt = self.responses.update().where(
            and_(
                self.responses.c.uuid == str(ruuid)
            )
        ).values(
            update_timestamp = str(datetime.datetime.now()),
            reviewer = str(user),
            reviewed = 3
        )
        self.conn.execute(stmt)
        
        stmt = self.responses.insert().values(
            create_timestamp = str(datetime.datetime.now()),
            update_timestamp = str(datetime.datetime.now()),
            uuid = str(uuid.uuid4()),
            feedback_uuid = str(fuuid),
            last_user = str(user),
            response = str(response),
            reviewed = 1,
            reviewer = str(user)
        )
        self.conn.execute(stmt)
        
    def assignFeedback(self, uuid, user):
        self.paperTrail(uuid, user)
        stmt = self.submissions.update().where(
            self.submissions.c.uuid == str(uuid)
        ).values(
            update_timestamp = str(datetime.datetime.now()),
            assignee = str(user)
        )
        self.conn.execute(stmt)
        
    def paperTrail(self, uuid, user):
        stmt = self.papertrail.insert().values(
            create_timestamp = str(datetime.datetime.now()),
            uuid = str(uuid),
            last_user = str(user)
        )
        self.conn.execute(stmt)
        
    def autoPublish(self):
        query = str(open('sql/autoPublish.sql', 'r').read())
        self.db.execute(query)
        
    def getUnanswered(self):
        data = []
        query = str(open('sql/getUnanswered.sql', 'r').read())
        self.data = self.db.execute(query)
        for row in self.data:
            data.append({'created': row[0], 
                         'updated': row[1], 
                         'feedback': urllib2.unquote(row[2]), 
                         'queue': row[3], 
                         'last_user': row[4], 
                         'assignee': row[5], 
                         'uuid': row[6], 
                         'level': row[7]})
            
        return data
    
    def getAnswered(self):
        data = []
        query = str(open('sql/getAnswered.sql', 'r').read())
        self.data = self.db.execute(query)
        for row in self.data:
            data.append({'created': row[0], 
                         'updated': row[1], 
                         'feedback': urllib2.unquote(row[2]), 
                         'queue': row[3], 
                         'last_user': row[4], 
                         'assignee': row[5], 
                         'uuid': row[6], 
                         'level': row[7]})
            
        return data
        
    def getFeedback(self, uuid):
        data = []
        query = str(open('sql/getFeedback.sql', 'r').read())
        self.data = self.db.execute(query)
        for row in self.data:
            created = datetime.datetime.strftime(row[0], '%m/%d/%Y - %I:%M %p')
            data.append({'created': created, 
                         'updated': row[1], 
                         'feedback': urllib2.unquote(row[2]), 
                         'queue': row[3], 
                         'last_user': row[4], 
                         'l2': row[5], 
                         'l3': row[6], 
                         'l4': row[7], 
                         'assignee': row[8], 
                         'uuid': row[9], 
                         'level': row[10]})
            
        return data
    
    def modFeedback(self):
        data = []
        query = str(open('sql/modFeedback.sql', 'r').read())
        self.data = self.db.execute(query)
        for row in self.data:
            data.append({'created': row[0], 
                         'feedback': urllib2.unquote(row[1]), 
                         'queue': row[2], 
                         'uuid': row[3]})
            
        return data
    
    def getAllFeedback(self):
        data = []
        query = str(open('sql/getAllFeedback.sql', 'r').read())
        self.data = self.db.execute(query)
        for row in self.data:
            created = datetime.datetime.strftime(row[0], '%m/%d/%Y - %I:%M %p')
            data.append({'created': created, 
                         'updated': row[1], 
                         'feedback': urllib2.unquote(row[2]), 
                         'queue': row[3], 
                         'last_user': row[4], 
                         'l2': row[5], 
                         'l3': row[6], 
                         'l4': row[7], 
                         'assignee': row[8], 
                         'uuid': row[9], 
                         'level': row[10], 
                         'response': row[11], 
                         'inquirer': row[12]})
            
        return data
    
    def getCSRFeedback(self):
        data = []
        responses = []
        
        self.data = self.db.execute("SELECT create_timestamp, feedback_uuid, last_user, response, uuid FROM responses WHERE reviewed = 1 ORDER BY create_timestamp")
        for row in self.data:
            responses.append({'created': row[0], 'feedback_uuid': row[1], 'user': row[2], 'response': row[3], 'uuid': row[4]})
        
        self.data = self.db.execute("SELECT create_timestamp, feedback, queue, uuid, level, inquisitor FROM submissions WHERE feedback IS NOT NULL AND verified = 1 ORDER BY STR_TO_DATE(create_timestamp, '%Y-%m-%d %H:%M:%S') ASC")
        for row in self.data:
            uuid = row[3]
            
            responseSet = []
            for response in responses:
                if response['feedback_uuid'] == uuid:
                    responseSet.append(response)
            
            responseStr = ''
            updated = '---'
            response_uuid = ''
            for idx, response in enumerate(responseSet):
                if len(responseSet) > 1:
                    if idx != len(responseSet) - 1:
                        responseStr += '<s>' + response['response'] + '</s><br /><hr />'
                    else:
                        responseStr += response['response'] + '<br />'
                        updated = datetime.datetime.strftime(response['created'], '%m/%d/%Y - %I:%M %p')
                        response_uuid = response['uuid']
                else:
                    responseStr += response['response'] + '<br />'
                    updated = datetime.datetime.strftime(response['created'], '%m/%d/%Y - %I:%M %p')
                    response_uuid = response['uuid']
            
            created = datetime.datetime.strftime(row[0], '%m/%d/%Y - %I:%M %p')
            data.append({'created': created, 'feedback': urllib2.unquote(row[1]), 'queue': row[2], 'uuid': uuid, 'level': row[4], 'inquirer': row[5], 'response': responseStr, 'updated': updated, 'response_uuid': response_uuid})
            
        return data
        
    def getQueue(self, email, level):
        data = []
        
        self.data = self.db.execute("SELECT hs.create_timestamp, hs.update_timestamp, hs.feedback, hs.queue, hs.last_user, hs.assignee, hs.uuid, hs.level, hs.claimed, hr.notes, hr.response, hr.uuid, hs.deescalated FROM submissions hs LEFT JOIN responses hr ON hr.feedback_uuid = hs.uuid WHERE ((response IS NULL OR response = '') OR (reviewed = 2)) AND verified = 1 AND assignee = '" + email + "'")
        for row in self.data:
            created = datetime.datetime.strftime(row[0], '%m/%d/%Y - %I:%M %p')
            data.append({'created': created, 'updated': row[1], 'feedback': urllib2.unquote(row[2]), 'queue': row[3], 'last_user': row[4], 'assignee': row[5], 'uuid': row[6], 'level': row[7], 'claim': row[8], 'notes': row[9], 'response': row[10], 'response_uuid': row[11], 'deescalated': row[12]})
            
        return data
    
    def getFeedbackUpvotes(self):
        data = []
        self.data = self.db.execute("SELECT create_timestamp, uuid, last_user, association FROM upvotes WHERE association = 'feedback'")
        for row in self.data:
            data.append({'created': row[0], 'uuid': row[1], 'user': row[2], 'type': row[3]})
            
        return data
    
    def getResponseUpvotes(self):
        data = []
        self.data = self.db.execute("SELECT create_timestamp, uuid, last_user, association FROM upvotes WHERE association = 'response'")
        for row in self.data:
            data.append({'created': row[0], 'uuid': row[1], 'user': row[2], 'type': row[3]})
            
        return data
    
    def getMyFlags(self, email):
        data = []
        self.data = self.db.execute("SELECT create_timestamp, uuid, last_user FROM flags WHERE last_user = '" + email + "'")
        for row in self.data:
            data.append({'created': row[0], 'uuid': row[1], 'user': row[2]})
            
        return data
    
    def getFlags(self):
        data = []
        self.data = self.db.execute("SELECT create_timestamp, uuid, last_user FROM flags")
        for row in self.data:
            data.append({'created': row[0], 'uuid': row[1], 'user': row[2]})
            
        return data
    
    def getOpenQueue(self):
        data = []
        self.data = self.db.execute("SELECT hs.create_timestamp, hs.update_timestamp, hs.feedback, hs.queue, hs.last_user, hs.assignee, hs.uuid, hs.level, hs.claimed, hr.response FROM submissions hs LEFT JOIN responses hr ON hr.feedback_uuid = hs.uuid WHERE (response IS NULL OR response = '') AND verified = 1 AND assignee = 'open'")
        for row in self.data:
            created = datetime.datetime.strftime(row[0], '%m/%d/%Y - %I:%M %p')
            data.append({'created': created, 'updated': row[1], 'feedback': urllib2.unquote(row[2]), 'queue': row[3], 'last_user': row[4], 'assignee': row[5], 'uuid': row[6], 'level': row[7], 'claim': row[8], 'response': row[9]})
            
        return data
    
    def getReviewQueue(self, emails):
        data = []
        if emails != '':
            self.data = self.db.execute("SELECT hs.create_timestamp, hs.update_timestamp, hs.feedback, hs.queue, hs.last_user, hs.assignee, hs.uuid, hs.level, hs.claimed, hr.response, hr.uuid, hs.assignee FROM submissions hs LEFT JOIN responses hr ON hr.feedback_uuid = hs.uuid WHERE hr.reviewed = 0 AND hr.last_user IN (" + emails + ")")
            for row in self.data:
                created = datetime.datetime.strftime(row[0], '%m/%d/%Y - %I:%M %p')
                data.append({'created': created, 'updated': row[1], 'feedback': urllib2.unquote(row[2]), 'queue': row[3], 'last_user': row[4], 'assignee': row[5], 'uuid': row[6], 'level': row[7], 'claim': row[8], 'response': row[9], 'response_uuid': row[10], 'assignee': row[11]})
            
        return data
    
    def getAmendmentQueue(self, cohorts, level):
        data = []
        responses = []
        
        cohortStr = "'Gen'"
        for cohort in cohorts:
            cohortStr += ", '" + cohort + "'"
        
        self.data = self.db.execute("SELECT create_timestamp, feedback_uuid, last_user, response, uuid, correct, reviewer2 FROM responses WHERE reviewed = 1 ORDER BY create_timestamp")
        for row in self.data:
            responses.append({'created': row[0], 'feedback_uuid': row[1], 'user': row[2], 'response': row[3], 'uuid': row[4], 'correct': row[5], 'reviewer2': row[6]})
        
        self.data = self.db.execute("SELECT create_timestamp, feedback, queue, uuid, level, inquisitor FROM submissions WHERE feedback IS NOT NULL AND verified = 1 AND LEFT(queue, 3) IN (" + cohortStr + ") ORDER BY STR_TO_DATE(create_timestamp, '%Y-%m-%d %H:%M:%S') ASC")
        
        if level >= 4:
            self.data = self.db.execute("SELECT create_timestamp, feedback, queue, uuid, level, inquisitor FROM submissions WHERE feedback IS NOT NULL ORDER BY STR_TO_DATE(create_timestamp, '%Y-%m-%d %H:%M:%S') ASC")
        
        for row in self.data:
            uuid = row[3]
            
            responseSet = []
            for response in responses:
                if response['feedback_uuid'] == uuid:
                    responseSet.append(response)
            
            responseStr = ''
            updated = '---'
            response_uuid = ''
            responseUser = ''
            correct = ''
            for idx, response in enumerate(responseSet):
                responseStr += '<b style="color: blue;">' + response['user'] + '</b>:<br />'
                if len(responseSet) > 1:
                    if idx != len(responseSet) - 1:
                        responseStr += '<s>' + response['response'] + '</s><br /><hr />'
                    else:
                        responseStr += response['response'] + '<br />'
                        updated = datetime.datetime.strftime(response['created'], '%m/%d/%Y - %I:%M %p')
                        response_uuid = response['uuid']
                        responseUser = response['user']
                        if response['correct'] == 1:
                            correct = response['reviewer2']
                else:
                    responseStr += response['response'] + '<br />'
                    updated = datetime.datetime.strftime(response['created'], '%m/%d/%Y - %I:%M %p')
                    response_uuid = response['uuid']
                    responseUser = response['user']
                    if response['correct'] == 1:
                        correct = response['reviewer2']
            
            created = datetime.datetime.strftime(row[0], '%m/%d/%Y - %I:%M %p')
            
            if responseStr != '':
                data.append({'created': created, 'feedback': urllib2.unquote(row[1]), 'queue': row[2], 'uuid': uuid, 'level': row[4], 'inquirer': row[5], 'response': responseStr, 'updated': updated, 'response_uuid': response_uuid, 'correct': correct})
            
        return data
            
    def runQuery(self, query):
        self.db.execute(query)
        
    def getCohort(self, email):
        data = []
        self.data = self.db.execute("SELECT cohort FROM roster WHERE user_email = '" + email + "'")
        for row in self.data:
            data.append(row[0])
            
        return data
        
    def getAdmins(self):
        data = []
        self.data = self.db.execute("SELECT user_email FROM roster WHERE cohort = 'ADMIN'")
        for row in self.data:
            data.append(row[0])
            
        return data
    
    def getManagers(self):
        data = []
        query = str(open('sql/getManagers.sql', 'r').read())
        self.data = self.db.execute(query)
        for row in self.data:
            data.append(row[0])
            
        return data
    
    def getLeads(self):
        data = []
        query = str(open('sql/getLeads.sql', 'r').read())
        self.data = self.db.execute(query)
        for row in self.data:
            data.append(row[0])
            
        return data
    
    def getLeadData(self):
        data = [];
        self.data = self.db.execute("SELECT DISTINCT user_email, cohort, shift_start, shift_end, shift_days FROM roster WHERE cohort = 'TL' ORDER BY 1");
        for row in self.data:
            data.append({'email': row[0], 'cohort': row[1], 'start': row[2], 'end': row[3], 'days': row[4]})
            
        print ('Leads: ' + str(len(data)))
        return data
    
    def getCohorts(self, email):
        data = []
        self.data = self.db.execute("SELECT DISTINCT cohort FROM roster WHERE manager_email = '" + email + "' OR tl_email = '" + email + "'")
        for row in self.data:
            data.append(row[0])
            
        return data
    
    def getMyTeam(self, email):
        data = []
        emailStr = ''
        self.data = self.db.execute("SELECT DISTINCT tl_email FROM roster WHERE manager_email = '" + email + "' AND tl_email IS NOT NULL ORDER BY 1")
        for row in self.data:
            emailStr += "'" + row[0] + "',"
            
        emailStr = emailStr[:len(emailStr) - 1]
        
        return emailStr
    
    def closeConnection(self):
        self.conn.close()