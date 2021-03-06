import base64
import json
import re
import sys
sys.path.append("../../..")
import datetime
import pymongo
from pymongo import MongoClient

from GithubUser.DMLib.DMDatabase import DMDatabase

# The first user is mojombo, id == 1, created: 2007-10-20

def get_user_event(user_res):
    type_res = []
    for item in user_res["event"]:
        type_res.append(item["type"])

# remove the duplicated
    return list(set(type_res))

def find_by_day_int (db, day_int):
    event_list = ["CommitCommentEvent",
              "CreateEvent",
              "DeleteEvent",
              "DeploymentEvent",
              "DeploymentStatusEvent",
              "DownloadEvent",
              "FollowEvent",
              "ForkEvent",
              "ForkApplyEvent",
              "GistEvent",
              "GollumEvent",
              "IssueCommentEvent",
              "IssuesEvent",
              "MemberEvent",
              "MembershipEvent",
              "PageBuildEvent",
              "PublicEvent",
              "PullRequestEvent",
              "PullRequestReviewCommentEvent",
              "PushEvent",
              "ReleaseEvent",
              "RepositoryEvent",
              "StatusEvent",
              "TeamAddEvent",
              "WatchEvent" ]
    print "start to find " + str(day_int)
    need_update = 0
    saved_res = db["research_result"].find_one({"type": "monthly_day_user_event", "month": day_int/100, "day": day_int})
    if saved_res:
        need_update = 1

    query_created = {"created_at_int": day_int}
    query_updated = {"count": {"$gt": 0}}
    query_json = {"$and": [query_created, query_updated]}

    res_list = []
    res = db["event"].find(query_json)
    for item in res:
        res_list.append(item)

    res_len = len(res_list)
#https://developer.github.com/v3/activity/events/types
    answer = {"type": "monthly_day_user_event", 
              "month": day_int/100,
              "day": day_int,
              "total_public": res_len,
              "update_date": datetime.datetime.utcnow()
             }
    for event_list_item in event_list:
        answer[event_list_item] = 0

#res_list_item is the record of each user
    for res_list_item in res_list:
        user_event_type = get_user_event(res_list_item)
        for user_event_type_item in user_event_type:
            answer[user_event_type_item] += 1

    print "\n----------------------\nDay " + str(day_int)
    print answer
    print   "----------------------\n"

    if need_update:
        db["research_result"].update({"type":"monthly_day_user_event", "month": day_int/100, "day": day_int}, {"$set": answer})
        print "The " + str(day_int) + " result is updated"
    else:
        db["research_result"].insert(answer)
        print "The " + str(day_int/100) + " result is added"

    return

def find_by_month_int (db, month_int_start):
    event_list = ["CommitCommentEvent",
              "CreateEvent",
              "DeleteEvent",
              "DeploymentEvent",
              "DeploymentStatusEvent",
              "DownloadEvent",
              "FollowEvent",
              "ForkEvent",
              "ForkApplyEvent",
              "GistEvent",
              "GollumEvent",
              "IssueCommentEvent",
              "IssuesEvent",
              "MemberEvent",
              "MembershipEvent",
              "PageBuildEvent",
              "PublicEvent",
              "PullRequestEvent",
              "PullRequestReviewCommentEvent",
              "PushEvent",
              "ReleaseEvent",
              "RepositoryEvent",
              "StatusEvent",
              "TeamAddEvent",
              "WatchEvent" ]
    print "start to find " + str(month_int_start)
    need_update = 0
    saved_res = db["research_result"].find_one({"type": "monthly_user_event", "month": month_int_start/100})
    if saved_res:
        need_update = 1

    month_int_end = month_int_start + 100
    query_created = {"created_at_int": {"$gte": month_int_start, "$lt": month_int_end}}
    query_updated = {"count": {"$gt": 0}}
    query_json = {"$and": [query_created, query_updated]}

    res_list = []
    res = db["event"].find(query_json)
    for item in res:
        res_list.append(item)

    res_len = len(res_list)
#https://developer.github.com/v3/activity/events/types
    answer = {"type": "monthly_user_event", 
              "month": month_int_start/100,
              "total_public": res_len,
              "update_date": datetime.datetime.utcnow()
             }
    for event_list_item in event_list:
        answer[event_list_item] = 0

#res_list_item is the record of each user
    for res_list_item in res_list:
        user_event_type = get_user_event(res_list_item)
        for user_event_type_item in user_event_type:
            answer[user_event_type_item] += 1

    print "\n----------------------\nMonth " + str(month_int_start/100)
    print answer
    print   "----------------------\n"

    if need_update:
        db["research_result"].update({"type":"monthly_user_event", "month": month_int_start/100}, {"$set": answer})
        print "The " + str(month_int_start/100) + " result is updated"
    else:
        db["research_result"].insert(answer)
        print "The " + str(month_int_start/100) + " result is added"

    return

#FIXME:tmp: 20130600
#begin at 2007-10, end at 2015-01
def calculate_months_int(db):
    begin_date = {"year": 2007, "month": 10}
#    begin_date = {"year": 2014, "month": 10}
    end_date = {"year": 2014, "month": 10}
    for year in range(begin_date["year"], end_date["year"]+1):
        begin_month = 1
        end_month = 12
        if year == begin_date["year"]:
            begin_month = begin_date["month"]
        elif year == end_date["year"]:
            end_month = end_date["month"]

        for month in range(begin_month, end_month+1):
            month_int = year*10000 + month * 100
            find_by_month_int(db, month_int)
#            for day in range(1, 32):
#                day_int = month_int + day
#                find_by_day_int(db, day_int)


#login = "torvalds" for example
def print_user_info(db, login):
    res = db["event"].find_one({"login": login})
    print res["count"]
    print res
    for item in res["event"]:
        print item["type"]
 
def merge_month(db, month):
    event_list = ["CommitCommentEvent",
              "CreateEvent",
              "DeleteEvent",
              "DeploymentEvent",
              "DeploymentStatusEvent",
              "DownloadEvent",
              "FollowEvent",
              "ForkEvent",
              "ForkApplyEvent",
              "GistEvent",
              "GollumEvent",
              "IssueCommentEvent",
              "IssuesEvent",
              "MemberEvent",
              "MembershipEvent",
              "PageBuildEvent",
              "PublicEvent",
              "PullRequestEvent",
              "PullRequestReviewCommentEvent",
              "PushEvent",
              "ReleaseEvent",
              "RepositoryEvent",
              "StatusEvent",
              "TeamAddEvent",
              "WatchEvent" ]

    answer = {"type": "monthly_user_event", 
              "month": month,
              "total_public": 0,
              "update_date": datetime.datetime.utcnow()
             }
    for event_list_item in event_list:
        answer[event_list_item] = 0

    res = db["research_result"].find({"type": "monthly_day_user_event", "month": month})
    for item in res:
        answer["total_public"] += item["total_public"]
        for event_list_item in event_list:
            answer[event_list_item] += item[event_list_item]

    saved_res = db["research_result"].find_one({"type": "monthly_user_event", "month": month})
    if saved_res:
        need_update = 1

    if need_update:
        db["research_result"].update({"type":"monthly_user_event", "month": month}, {"$set": answer})
        print "The " + str(month) + " result is updated"
    else:
        db["research_result"].insert(answer)
        print "The " + str(month) + " result is added"

def main_int ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
#        print_user_info(db, "initlove")
#        calculate_months_int(db)
         merge_month(db, 201412)
    else:
        print "Cannot connect to database"

main_int()
