from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from sqltool import sqlTool
from flask_cors import CORS
import json
import datetime
import time
import runpy
import logging
import threading
import schedule
import script
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_REMOVED
import alert
import sqllib


app = Flask(__name__)
api = Api(app)
CORS(app)

def mergeResultHead(re,head):
    myLists = []
    for res in re:
            res = list(res)
            myLists.append(dict(zip(head, res)))
    return myLists
    

# * Outline
# ! Database Service
# * User Service
# * Device Service
# * Notification Service
# * Another Web Service
# ! Job/Script Service
# * Jobs scheduler Service


class tryJson(Resource):
    def post(self):
        data = request.get_json()
        print(data)
        return {"task":"Success"},201
        

api.add_resource(tryJson, "/tryJson")        

# * ----------------------------------------------------------------
# * ------------------------  User Service
# * ---------------------------------------------------------------


# * getUser
# * addUser
# * removeUser
# * editUser
# * auth
# toggleEmailAlert

class getUser(Resource):
    def get(self):
        selector = """SELECT user.id,user.username,user.firstname,user.lastname,user.usertype FROM user;"""
        results, headTables = sqllib.select(selector)
        myLists = []
        myLists.clear()
        for res in results:
            res = list(res)
            myLists.append(dict(zip(headTables, res)))
        results.clear()
        headTables.clear()
        return jsonify(myLists)


class addUserService(Resource):
    def post(self):
        data = request.get_json()
        user = data['regUsername']
        passW = data['regPassword']
        fname = data['regFirstName']
        lname = data['regLastName']
        email = data['regEmail']

        # TODO : check duplicate

        insertor = """INSERT INTO user (user.username, user.password, user.firstname, user.lastname,user.usertype,user.email)
                    VALUES ('{0}', '{1}', '{2}','{3}',{4},'{5}');"""
        insertor = insertor.format(user,passW,fname,lname,0,email)
        sqllib.insertor(insertor)
        task = {'task': "success"}
        return task
    


class removeUserService(Resource):
    def delete(self, userId):
        remove = """DELETE FROM user WHERE user.id='{0}';"""
        remove = remove.format(userId)
        err = sqllib.executor(remove)
        if err:
            return {'task': "success"}
        else:
            return {'task': "fail"}


class editUserService(Resource):
    def post(self):
        data = request.get_json()
        userId =  data['Id']
        user = data['Username']
        passW = data['Password']
        fname = data['FirstName']
        lname = data['LastName']
        email = data['Email']
        userType = data['type']
        print(data)
        updator = """UPDATE user
                        SET
                        user.username = '{user}',
                        user.password = '{passW}',
                        user.firstname = '{fname}',
                        user.lastname = '{lastname}',
                        user.usertype = {userT},
                        user.email = '{email}'
                        WHERE
                        user.id = {id};"""
        err = sqllib.updator(updator.format(
            user=user ,
            passW=passW,
            fname=fname,
            lastname=lname,
            email=email,
            userT=userType,
            id=userId
        ));
        if err == True:
            return {'task':'success'}
        else:
            return {'task':'fail'}


class auth(Resource):
    def post(self):
        data = request.get_json()
        
        user = data['username']
        passW = data['password']
        selector = "SELECT * FROM user WHERE user.username ='{0}' AND user.password = '{1}';"
        selector = selector.format(user,passW)
        try:
            results , head = sqllib.select(selector)
            
            re = []
            if results:
                re = mergeResultHead(results,head)
                
                uType = ""
                if re[0]['usertype'] == 1:
                    uType = "admin"
                else:
                    uType = "user"
            # print(re)
            if re:
                return {'auth': "success",
                        'type' : uType,
                        'fname': re[0]['firstname'],
                        'lname':re[0]['lastname'],
                        'id':re[0]['id'],}   
        except Exception as err:
            return {'auth': "fail"}
        return {'auth': "fail"}
        
class toggleMailAlert(Resource):
    def post(self):
        data = request.get_json()
        c = 0
        selector = """SELECT * FROM user
        WHERE user.id = {id}"""

        re , head = sqllib.select(selector.format(id=data['id']))

        ress = mergeResultHead(re,head)
        # print(ress[0]['emailAlert'])
        # print(type(ress[0]['emailAlert']))
        if(ress[0]['emailAlert'] == 0):
            updator = """UPDATE user
            SET
            user.emailAlert = 1
            WHERE
            user.id = {id};"""
            sqllib.updator(updator.format(id=data['id']))
            c = 1
        else:
            updator = """UPDATE user
            SET
            user.emailAlert = 0
            WHERE
            user.id = {id};"""
            sqllib.updator(updator.format(id=data['id']))
            c=0

        return {'task':'success','changeTo':c}        

class getUserById(Resource):
    def get(self,inid):
        selector = """SELECT * FROM user
                        WHERE user.id = {id}"""

        re , head = sqllib.select(selector.format(id=inid))

        res = mergeResultHead(re,head)
        print(res)
        res[0].pop('password')
        
        return jsonify(res)

api.add_resource(getUserById, "/getUserById/<string:inid>")
api.add_resource(getUser, "/getUser")
api.add_resource(addUserService, "/userAdd")
api.add_resource(removeUserService, "/userRemove/<string:userId>")
api.add_resource(toggleMailAlert, "/toggleMailUser")
api.add_resource(editUserService, "/userEdit")
api.add_resource(auth, "/auth")


# * ----------------------------------------------------------------
# * ------------------------  Devices Service
# * ---------------------------------------------------------------


# * getDevice
# * addDevice
# * editDevice
# * removeDevice
class getDevice(Resource):
    def get(self):
        selector = """SELECT * FROM devicedetail
                        INNER JOIN devicelocation WHERE devicelocation.deviceid = devicedetail.deviceid;"""
                        
        myLists = []
        myLists.clear()
        re , head = sqllib.select(selector)
        for res in re:
            res = list(res)
            myLists.append(dict(zip(head, res)))
        
        return jsonify(myLists)


class addDeviceService(Resource):
    def post(self):
        data = request.get_json()
        selector = """SELECT
                        IF(
                            EXISTS(
                            SELECT
                                *
                            FROM
                                devicedetail
                            WHERE
                                devicedetail.ip = "{ip}"
                            ),
                            1,
                            0
                        );
                        """
                        
        re , head = sqllib.select(selector.format(ip = data['ip']))
        
        if(re[0][0] == 1):
            task = {'task': "fail",
                    'description' : 'duplicate ip'}
            return task
        else: 
            insertor = """INSERT INTO devicedetail(devicedetail.ip,devicedetail.community,devicedetail.active,devicedetail.brand,devicedetail.contractnumber,devicedetail.serialnumber,devicedetail.type) VALUES
                        ("{ip}","{commu}",{active},"{brand}","{contractnum}","{serialnum}","{intype}");
                        """
                        
            insertor = insertor.format(ip = data['ip'],
                                commu = data['commu'],
                                active = data['active'],
                                brand = data['brand'],
                                contractnum = data['contractNum'],
                                serialnum = data['serialNumber'],
                                intype = data['type'],
                                build = data['build'],
                                location = data['location'],
                                node = data['node'],
                                rack = data['rack'])
            
            sqllib.insertor(insertor)
            insertor = """INSERT INTO devicelocation(deviceid,build,location,node,rack) VALUES
                        ((SELECT DISTINCT devicedetail.deviceid FROM devicedetail WHERE devicedetail.ip = "{ip}"),"{build}","{location}","{node}","{rack}");"""
                        
            insertor = insertor.format(ip = data['ip'],
                                commu = data['commu'],
                                active = data['active'],
                                brand = data['brand'],
                                contractnum = data['contractNum'],
                                serialnum = data['serialNumber'],
                                intype = data['type'],
                                build = data['build'],
                                location = data['location'],
                                node = data['node'],
                                rack = data['rack'])
            sqllib.insertor(insertor)
            task = {'task': "success"}
            return task

class addDeviceByCSVService(Resource):
    def post(self):
        data = request.get_json()
        selector = """SELECT
                        IF(
                            EXISTS(
                            SELECT
                                *
                            FROM
                                devicedetail
                            WHERE
                                devicedetail.ip = "{ip}"
                            ),
                            1,
                            0
                        );
                        """
                        
        re , head = sqllib.select(selector.format(ip = data['ip']))
        
        if(re[0][0] == 1):
            task = {'task': "fail",
                    'description' : 'duplicate ip'}
            return task
        else: 
            insertor = """INSERT INTO devicedetail(devicedetail.ip,devicedetail.community,devicedetail.active,devicedetail.brand,devicedetail.contractnumber,devicedetail.serialnumber,devicedetail.type) VALUES
                        ("{ip}","{commu}",{active},"{brand}","{contractnum}","{serialnum}","{intype}");
                        """
                        
            insertor = insertor.format(ip = data['ip'],
                                commu = data['communitystring'],
                                active = data['active'],
                                brand = data['brand'],
                                contractnum = data['contact number'],
                                serialnum = data['serial number'],
                                intype = data['type'],
                                build = data['build'],
                                location = data['location'],
                                node = data['node'],
                                rack = data['rack'])
            
            sqllib.insertor(insertor)
            insertor = """INSERT INTO devicelocation(deviceid,build,location,node,rack) VALUES
                        ((SELECT DISTINCT devicedetail.deviceid FROM devicedetail WHERE devicedetail.ip = "{ip}"),"{build}","{location}","{node}","{rack}");"""
                        
            insertor = insertor.format(ip = data['ip'],
                                commu = data['communitystring'],
                                active = data['active'],
                                brand = data['brand'],
                                contractnum = data['contact number'],
                                serialnum = data['serial number'],
                                intype = data['type'],
                                build = data['build'],
                                location = data['location'],
                                node = data['node'],
                                rack = data['rack'])
            sqllib.insertor(insertor)
            task = {'task': "success"}
            return task


class removeDeviceService(Resource):
    def delete(self, DeviceId):
        
        
        deletor = """DELETE FROM portsnmpstatus WHERE portsnmpstatus.deviceid = {id}"""
        err = sqllib.deletor(deletor.format(id=DeviceId))
        deletor = """DELETE FROM snmpstatus WHERE snmpstatus.deviceid = {id};"""
        err = sqllib.deletor(deletor.format(id=DeviceId))
        deletor = """DELETE FROM icmpstatus WHERE icmpstatus.deviceid = {id};"""
        err = sqllib.deletor(deletor.format(id=DeviceId))
        deletor = """DELETE FROM devicelocation WHERE devicelocation.deviceid = {id};"""
        err = sqllib.deletor(deletor.format(id=DeviceId))
        deletor = """DELETE FROM devicedetail WHERE devicedetail.deviceid = {id};"""
        err = sqllib.deletor(deletor.format(id=DeviceId))
        task = {'task': "success"}
        return task


class editDeviceService(Resource):
    def post(self):
        data = request.get_json()
        updator = """UPDATE devicedetail
                    SET
                    devicedetail.ip = "{ip}",
                    devicedetail.community = "{commu}",
                    devicedetail.active = {active},
                    devicedetail.serialnumber = "{serialNumber}",
                    devicedetail.brand="{brand}",
                    devicedetail.contractnumber = "{contractNum}",
                    devicedetail.`type` = "{type}"
                    WHERE
                    devicedetail.deviceId = {id};"""
        err = sqllib.updator(updator.format(ip = data['ip'],
                            commu = data['commu'],
                            active = data['active'],
                            hostname = data['hostname'],
                            build = data['build'],
                            location = data['location'],
                            node = data['node'],
                            rack = data['rack'],
                            brand = data['brand'],
                            contractNum = data['contractNum'],
                            type = data['type'],
                            serialNumber = data['serialNumber'],
                            id = data['deviceId']))
        updator = """UPDATE devicelocation
                    SET
                    devicelocation.build = "{build}",
                    devicelocation.location = "{location}",
                    devicelocation.node = "{node}",
                    devicelocation.rack = "{rack}"
                    WHERE
                    devicelocation.deviceid = {id}
                    """
        err = sqllib.updator(updator.format(ip = data['ip'],
                            commu = data['commu'],
                            active = data['active'],
                            hostname = data['hostname'],
                            build = data['build'],
                            location = data['location'],
                            node = data['node'],
                            rack = data['rack'],
                            brand = data['brand'],
                            contractNum = data['contractNum'],
                            type = data['type'],
                            serialNumber = data['serialNumber'],
                            id = data['deviceId']))
         
        task = {'task': "success"}
        return task
    

api.add_resource(getDevice, "/getDevice")
api.add_resource(addDeviceService, "/deviceAdd")
api.add_resource(addDeviceByCSVService, "/deviceAddCSV")
api.add_resource(removeDeviceService, "/deviceRemove/<string:DeviceId>")
api.add_resource(editDeviceService,"/editDevice")

# * ----------------------------------------------------------------
# * ------------------------  Single Devices Service
# * ---------------------------------------------------------------

class getDeviceOne(Resource):
    def get(self,ip):
        selector = """SELECT 
                    ip,
                    community,
                    active,
                    serialnumber,
                    brand,
                    contractnumber,
                    `type`,
                    build,
                    locationID,
                    location,
                    node,
                    rack
                    FROM devicedetail
                    INNER JOIN devicelocation 
                    ON devicelocation.deviceid = (SELECT DISTINCT devicedetail.deviceid FROM devicedetail WHERE devicedetail.ip = "10.1.1.1")
                    WHERE ip = "{iip}";"""
                    
        re , head = sqllib.select(selector.format(iip=ip))
        
        out = mergeResultHead(re,head)
        
        return jsonify(out)
class getSnmpDeviceOne(Resource):
    def get(self,ip):
        selector = """SELECT * FROM snmpstatus
                        WHERE snmpstatus.deviceid = (SELECT DISTINCT devicedetail.deviceid FROM devicedetail WHERE devicedetail.ip = "{iip}");"""
                        
        re,head = sqllib.select(selector.format(iip=ip))
        
        out = mergeResultHead(re,head)
        seconds  = int(out[0]['upTime'])/100
        out[0]['upTime'] = str(datetime.timedelta(seconds=seconds ))
        return jsonify(out)
    
class getPortDeviceOne(Resource):
    def get(self,ip):
        selector = """SELECT * FROM portsnmpstatus
                    WHERE portsnmpstatus.deviceid = (SELECT DISTINCT devicedetail.deviceid FROM devicedetail WHERE devicedetail.ip = "{iip}");"""
        re,head = sqllib.select(selector.format(iip=ip))
        return jsonify(mergeResultHead(re,head))
    
class getIcmpDeviceOne(Resource):
    def get(self,ip):
        selector = """SELECT  * FROM icmpstatus
                        WHERE icmpstatus.deviceid = (SELECT DISTINCT devicedetail.deviceid FROM devicedetail WHERE devicedetail.ip = "{iip}")
                        ORDER BY icmpstatus.icmpid DESC;"""
                        
        re,head = sqllib.select(selector.format(iip=ip))
        return jsonify(mergeResultHead(re,head))
    
class getIcmpDeviceOneLast(Resource):
    def get(self,ip):
        selector = """SELECT  * FROM icmpstatus
                        WHERE icmpstatus.deviceid = (SELECT DISTINCT devicedetail.deviceid FROM devicedetail WHERE devicedetail.ip = "{iip}")
                        ORDER BY icmpstatus.icmpid DESC
                        LIMIT 1;"""
                        
        re,head = sqllib.select(selector.format(iip=ip))
        return jsonify(mergeResultHead(re,head))
    
api.add_resource(getDeviceOne, "/getDeviceOne/<string:ip>")
api.add_resource(getSnmpDeviceOne, "/getSnmpDeviceOne/<string:ip>")
api.add_resource(getPortDeviceOne, "/getPortDeviceOne/<string:ip>")
api.add_resource(getIcmpDeviceOne, "/getIcmpDeviceOne/<string:ip>")
api.add_resource(getIcmpDeviceOneLast, "/getIcmpDeviceOneLast/<string:ip>")


# * ----------------------------------------------------------------
# * ------------------------  Notification/Alert Service
# * ---------------------------------------------------------------


class getNotification(Resource):
    def get(self):
        task = {'task': "success"}
        return task


api.add_resource(getNotification, "/getNotification")


# * ----------------------------------------------------------------
# * ------------------------  Report
# * ---------------------------------------------------------------

# * report1   
# * report2  
# * report3   
# * report4   
# * report5   

class report1(Resource):
    def post(self):
        data = request.get_json()
        select = data['select']
        dateFrom = data['dateFrom']
        dateToo = data['dateToo']
       
        # get location name
        selector  = """SELECT DISTINCT devicelocation.{select} FROM devicelocation;"""
        reDL ,headDL = sqllib.select(selector.format(select=select))
        
       

        finalData = []
        finalData.clear()
        for dl in reDL:
            dataJ = []
            # get all ip in that location
            selector = """SELECT DISTINCT devicedetail.ip FROM devicedetail
                    INNER JOIN devicelocation ON devicedetail.deviceid = devicelocation.deviceid
                    INNER JOIN icmpstatus ON devicedetail.deviceid = icmpstatus.deviceid
                            AND devicelocation.{select} = "{where}";"""
                    
            reD , headD = sqllib.select(selector.format(select=select,where=dl[0]))
            sumDurationL = datetime.timedelta(seconds=0)
            for i in reD:
                # get status by ip
                selector = """SELECT * FROM devicedetail
                            INNER JOIN devicelocation ON devicedetail.deviceid = devicelocation.deviceid
                            INNER JOIN icmpstatus ON devicedetail.deviceid = icmpstatus.deviceid
                            WHERE devicedetail.ip = "{ip}"
                            AND devicelocation.{select} = "{where}"
                            AND icmpstatus.timedate BETWEEN CAST('{datefrom}' AS DATE) AND CAST('{too}' AS DATE);"""
                # print(selector.format(ip= i[0],select=select,where=dl[0],datefrom=dateFrom,too=dateToo))
                re , head = sqllib.select(selector.format(ip= i[0],select=select,where=dl[0],datefrom=dateFrom,too=dateToo))
                res = mergeResultHead(re,head)
                # print("list array",res)
                # array of status op ip
                # store time of down 
                downlist = []
                
                downlist.clear()
                start = []
                pre = []
                end = []
                sumDuration = datetime.timedelta(seconds=0)
                # for find downlist
                for item in res:
                    if start != []:
                        if item == res[-1]:
                            end = item
                            downlist.append({"start":start,"end":end,"duration":str(end['timedate'] - start['timedate'])})
                            sumDuration += end['timedate'] - start['timedate']
                            start = []
                            end = []
                        elif item['icmpstatus'] == '0':
                            end = item
                        elif item['icmpstatus'] == '1':
                            downlist.append({"start":start,"end":end,"duration":str(end['timedate'] - start['timedate'])})
                            sumDuration += end['timedate'] - start['timedate']
                            start = []
                            end = []                 
                        
                            
                    else:
                        if item['icmpstatus'] == '0':
                            pre = item
                            start = item
                            end = item
                        if item == res[-1]:
                            start = item
                            end = item
                            downlist.append({"start":start,"end":end,"duration":str(end['timedate'] - start['timedate'])})
                            sumDuration += end['timedate'] - start['timedate']
                            start = []
                            end = []
                print(downlist)
                if len(downlist) != 0:
                    dataJ.append({"data":downlist,"sumDuration":str(sumDuration)})
                sumDurationL += sumDuration
                
                # print(dataJ)
            if(len(dataJ) != 0):
                finalData.append({
                    dl[0] : dataJ,
                    "sumDuration" : str(sumDurationL)
                })
            # dataJ.clear() 
            
                    
       
        return jsonify(finalData)
    
        
   
class report2(Resource):
    def post(self):
        data = request.get_json()
        selector = """SELECT DISTINCT devicedetail.ip FROM devicedetail
                    INNER JOIN devicelocation ON devicedetail.deviceid = devicelocation.deviceid
                    INNER JOIN icmpstatus ON devicedetail.deviceid = icmpstatus.deviceid"""
        if data:
            selector += " WHERE 1"
            try:
                if data['node']:
                    selector += (" AND devicelocation.node = " + "'"+data['node']+"'") 
            except:
                pass
            try:
                if data['build']:
                    selector += (" AND devicelocation.build = " + "'"+data['build']+"'")
            except:
                pass
            try:
                if data['location']:
                    selector += (" AND devicelocation.location = " + "'"+data['location']+"'")  
            except:
                pass
            try:
                if data['rack']:
                    selector += (" AND devicelocation.rack = " + "'"+data['rack']+"'")  
            except:
                pass
            
        selector += ";"     
        
        re,head = sqllib.select(selector)
        
        dateFrom = data['dateFrom']
        dateToo = data['dateToo']
        dataJ = []
        sumDurationL = datetime.timedelta(seconds=0)
        for i in re:
            print("/n ip:",i[0])
            print("/n dateFrom:",dateFrom)
            print("/n dateToo:",dateToo)
            # get status by ip
            selector = """SELECT * FROM devicedetail
                        INNER JOIN devicelocation ON devicedetail.deviceid = devicelocation.deviceid
                        INNER JOIN icmpstatus ON devicedetail.deviceid = icmpstatus.deviceid
                        WHERE devicedetail.ip = "{ip}"
                        AND icmpstatus.timedate BETWEEN CAST('{datefrom}' AS DATE) AND CAST('{too}' AS DATE);"""
            # print(selector.format(ip= i[0],select=select,where=dl[0],datefrom=dateFrom,too=dateToo))
            re , head = sqllib.select(selector.format(ip= i[0],datefrom=dateFrom,too=dateToo))
            res = mergeResultHead(re,head)
            # print("list array",res)
            # array of status op ip
            # store time of down 
            downlist = []
            
            downlist.clear()
            start = []
            pre = []
            end = []
            sumDuration = datetime.timedelta(seconds=0)
            # for find downlist
            for item in res:
                if start != []:
                    if item == res[-1]:
                        end = item
                        downlist.append({"start":start,"end":end,"duration":str(end['timedate'] - start['timedate'])})
                        sumDuration += end['timedate'] - start['timedate']
                        start = []
                        end = []
                    elif item['icmpstatus'] == '0':
                        end = item
                    elif item['icmpstatus'] == '1':
                        downlist.append({"start":start,"end":end,"duration":str(end['timedate'] - start['timedate'])})
                        sumDuration += end['timedate'] - start['timedate']
                        
                        start = []
                        end = []                 
                    
                        
                else:
                    if item['icmpstatus'] == '0':
                        pre = item
                        start = item
                        end = item
                    if item == res[-1]:
                        start = item
                        end = item
                        downlist.append({"start":start,"end":end,"duration":str(end['timedate'] - start['timedate'])})
                        sumDuration += end['timedate'] - start['timedate']
                        start = []
                        end = []
            if len(downlist) != 0:
                dataJ.append({"data":downlist,"sumDuration":str(sumDuration)})
            sumDurationL += sumDuration
            
        finalData = {
        'data':dataJ,
        'sumDuration':str(sumDurationL)
        }
        return jsonify(finalData) 

class report3(Resource):
    def post(self):
        data = request.get_json()
        # print(data)
        selector = """SELECT devicelocation.node,devicelocation.build,devicelocation.location,devicelocation.rack,devicedetail.ip,snmpstatus.hostname,devicedetail.`type`,devicedetail.brand,devicedetail.serialnumber,devicedetail.contractnumber FROM  devicedetail
                        INNER JOIN devicelocation ON devicedetail.deviceid = devicelocation.deviceid
                        left JOIN snmpstatus ON devicedetail.deviceid = snmpstatus.deviceid"""
        if data:
            selector += " WHERE 1"
            try:
                if data['node']:
                    selector += (" AND devicelocation.node = " + "'"+data['node']+"'") 
            except:
                pass
            try:
                if data['build']:
                    selector += (" AND devicelocation.build = " + "'"+data['build']+"'")
            except:
                pass
            try:
                if data['location']:
                    selector += (" AND devicelocation.location = " + "'"+data['location']+"'")  
            except:
                pass
            try:
                if data['rack']:
                    selector += (" AND devicelocation.rack = " + "'"+data['rack']+"'")  
            except:
                pass
            try:
                if data['contract']:
                    selector += (" AND devicedetail.contractnumber = " + "'"+data['contract']+"'")  
            except:
                pass
             
            
            
            
        
        
        selector += ";"     
        print(selector)
        re,head = sqllib.select(selector)
        return jsonify(mergeResultHead(re,head))
                    
class report4(Resource):
    def get(self):
        
        dataJ = {
            "active" :{
              "build" :[],  
              "location" :[],  
              "node" :[],  
              "rack" :[]  
            },
            "noactive" :{
                
              "build" :[],  
              "location" :[],  
              "node" :[],  
              "rack" :[]
            },
            "all":{
                
              "build" :[],  
              "location" :[],  
              "node" :[],  
              "rack" :[]
            }
        }
        selector  = """SELECT DISTINCT devicelocation.location FROM devicelocation;"""
        re,head=sqllib.select(selector);
        for i in re:
            i = list(i)
            selector  = """SELECT COUNT(*) FROM devicelocation
                        INNER JOIN devicedetail ON devicedetail.deviceid = devicelocation.deviceid
                        WHERE devicelocation.location = '{loca}'
                        AND devicedetail.active = 1;"""
            try:
                rein,headin = sqllib.select(selector.format(loca=i[0]))
                data = {i[0]:rein[0][0]}
            except:
                print("report4 error : sql select")
            dataJ['active']['location'].append(data);
            selector  = """SELECT COUNT(*) FROM devicelocation
                        INNER JOIN devicedetail ON devicedetail.deviceid = devicelocation.deviceid
                        WHERE devicelocation.location = '{loca}'
                        AND devicedetail.active = 0;"""
            try:
                rein,headin = sqllib.select(selector.format(loca=i[0]))
                data = {i[0]:rein[0][0]}
            except:
                print("report4 error : sql select")
            dataJ['noactive']['location'].append(data);
            dataJ['all']['location'].append(data);
            
        selector  = """SELECT DISTINCT devicelocation.node FROM devicelocation;"""
        re,head=sqllib.select(selector);
        for i in re:
            i = list(i)
            selector  = """SELECT COUNT(*) FROM devicelocation
                        INNER JOIN devicedetail ON devicedetail.deviceid = devicelocation.deviceid
                        WHERE devicelocation.node = '{loca}'
                        AND devicedetail.active = 1;"""
            try:
                rein,headin = sqllib.select(selector.format(loca=i[0]))
                data = {i[0]:rein[0][0]}
            except:
                print("report4 error : sql select")
            dataJ['active']['node'].append(data);
            selector  = """SELECT COUNT(*) FROM devicelocation
                        INNER JOIN devicedetail ON devicedetail.deviceid = devicelocation.deviceid
                        WHERE devicelocation.node = '{loca}'
                        AND devicedetail.active = 0;"""
            try:
                rein,headin = sqllib.select(selector.format(loca=i[0]))
                data = {i[0]:rein[0][0]}
            except:
                print("report4 error : sql select")
            dataJ['noactive']['node'].append(data);
            dataJ['all']['node'].append(data);
            
        selector  = """SELECT DISTINCT devicelocation.rack FROM devicelocation;"""
        re,head=sqllib.select(selector);
        for i in re:
            i = list(i)
            selector  = """SELECT COUNT(*) FROM devicelocation
                        INNER JOIN devicedetail ON devicedetail.deviceid = devicelocation.deviceid
                        WHERE devicelocation.rack = '{loca}'
                        AND devicedetail.active = 1;"""
            try:
                rein,headin = sqllib.select(selector.format(loca=i[0]))
                data = {i[0]:rein[0][0]}
            except:
                print("report4 error : sql select")
            dataJ['active']['rack'].append(data);
            selector  = """SELECT COUNT(*) FROM devicelocation
                        INNER JOIN devicedetail ON devicedetail.deviceid = devicelocation.deviceid
                        WHERE devicelocation.rack = '{loca}'
                        AND devicedetail.active = 0;"""
            try:
                rein,headin = sqllib.select(selector.format(loca=i[0]))
                data = {i[0]:rein[0][0]}
            except:
                print("report4 error : sql select")
            dataJ['noactive']['rack'].append(data);
            dataJ['all']['rack'].append(data);
            
        selector  = """SELECT DISTINCT devicelocation.build FROM devicelocation;"""
        re,head=sqllib.select(selector);
        for i in re:
            i = list(i)
            selector  = """SELECT COUNT(*) FROM devicelocation
                        INNER JOIN devicedetail ON devicedetail.deviceid = devicelocation.deviceid
                        WHERE devicelocation.build = '{loca}'
                        AND devicedetail.active = 1;"""
            try:
                rein,headin = sqllib.select(selector.format(loca=i[0]))
                data = {i[0]:rein[0][0]}
            except:
                print("report4 error : sql select")
            dataJ['active']['build'].append(data);
            selector  = """SELECT COUNT(*) FROM devicelocation
                        INNER JOIN devicedetail ON devicedetail.deviceid = devicelocation.deviceid
                        WHERE devicelocation.build = '{loca}'
                        AND devicedetail.active = 0;"""
            try:
                rein,headin = sqllib.select(selector.format(loca=i[0]))
                data = {i[0]:rein[0][0]}
            except:
                print("report4 error : sql select")
            dataJ['noactive']['build'].append(data);
            dataJ['all']['build'].append(data);
        
        
                    
        return jsonify(dataJ)
    
   
class report5(Resource):
     def post(self):
        data = request.get_json()
        selector  = """SELECT DISTINCT devicelocation.{select} FROM devicelocation;"""
        reDL ,headDL = sqllib.select(selector.format(select=data['select']))
        finalData = []
        for r in reDL:
            selector = """SELECT DISTINCT devicedetail.ip FROM devicedetail
                        INNER JOIN devicelocation ON devicedetail.deviceid = devicelocation.deviceid
                        INNER JOIN icmpstatus ON devicedetail.deviceid = icmpstatus.deviceid"""
            selector += " WHERE devicelocation.{select} = '{loca}'"
            
            
           
            
            selector += ";"     
            
            re,head = sqllib.select(selector.format(select=data['select'],loca=r[0]))
            dateFrom = data['dateFrom']
            dateToo = data['dateToo']
            dataJ = []
            
            sumDurationL = datetime.timedelta(seconds=0)
            for i in re:
                # get status by ip
                selector = """SELECT * FROM devicedetail
                            INNER JOIN devicelocation ON devicedetail.deviceid = devicelocation.deviceid
                            INNER JOIN icmpstatus ON devicedetail.deviceid = icmpstatus.deviceid
                            WHERE devicedetail.ip = "{ip}"
                            AND icmpstatus.timedate BETWEEN CAST('{datefrom}' AS DATE) AND CAST('{too}' AS DATE);"""
                # print(selector.format(ip= i[0],select=select,where=dl[0],datefrom=dateFrom,too=dateToo))
                re , head = sqllib.select(selector.format(ip= i[0],datefrom=dateFrom,too=dateToo))
                res = mergeResultHead(re,head)
                # print("list array",res)
                # array of status op ip
                # store time of down 
                downlist = []
                
                downlist.clear()
                start = []
                pre = []
                end = []
                sumDuration = datetime.timedelta(seconds=0)
                # for find downlist
                for item in res:
                    if start != []:
                        if item['icmpstatus'] == '0':
                            end = item
                        elif item['icmpstatus'] == '1':
                            downlist.append({"start":start,"end":end,"duration":str(end['timedate'] - start['timedate'])})
                            sumDuration += end['timedate'] - start['timedate']
                            start = []
                            end = []                 
                        elif item == res[-1]:
                            end = item
                            downlist.append({"start":start,"end":end,"duration":str(end['timedate'] - start['timedate'])})
                            sumDuration += end['timedate'] - start['timedate']
                            start = []
                            end = []
                            
                    else:
                        if item['icmpstatus'] == '0':
                            pre = item
                            start = item
                            end = item
                        if item == res[-1]:
                            start = item
                            end = item
                            downlist.append({"start":start,"end":end,"duration":str(end['timedate'] - start['timedate'])})
                            sumDuration += end['timedate'] - start['timedate']
                            start = []
                            end = []
                
                if len(downlist) != 0:
                    dataJ.append({"data":downlist,"sumDuration":str(sumDuration)})
                sumDurationL += sumDuration
            if len(dataJ) != 0:
                finalData.append(
                    {
                        'location':r[0],
                'data':dataJ,
                'sumDuration':str(sumDurationL)
                }
                )
        return jsonify(finalData) 
    
api.add_resource(report1, "/report1")
api.add_resource(report2, "/report2")
api.add_resource(report3, "/report3")
api.add_resource(report4, "/report4")
api.add_resource(report5, "/report5")

# * ----------------------------------------------------------------
# * ------------------------  Web page Service
# * ---------------------------------------------------------------


# * ------------------------  Dashboard
class dashBoard(Resource):
    # get all device  show ip ,location , and lastest Status
    def get(self):
        selector = """SELECT  devicelocation.locationID,devicelocation.build,devicelocation.location,devicelocation.node,devicelocation.rack ,devicedetail.active, a2.lastCheck ,a2.deviceid, a2.ip , a2.icmpstatus , a2.timedate FROM devicedetail
                LEFT JOIN devicelocation ON devicedetail.deviceid = devicelocation.locationID
                INNER JOIN (SELECT myjoin.lastCheck,icmpstatus.deviceid,devicedetail.ip,icmpstatus.icmpstatus,icmpstatus.timedate FROM icmpstatus
                INNER JOIN (SELECT MAX(icmpstatus.icmpid) AS LastCheck,icmpstatus.deviceid FROM icmpstatus
                GROUP BY icmpstatus.deviceid) AS myjoin ON icmpstatus.icmpid = myjoin.LastCheck AND icmpstatus.deviceid = myjoin.deviceid
                INNER JOIN devicedetail ON devicedetail.deviceid = icmpstatus.deviceid) a2 ON devicedetail.deviceid = a2.deviceid;"""

        results, headTables = sqllib.select(selector)
        myLists = []
        myLists.clear()
        for res in results:
            res = list(res)
            # print("Get dashboard : ",res)
            res[10] = res[10].strftime('%Y-%m-%d %H:%M:%S')
            myLists.append(dict(zip(headTables, res)))
        results.clear()
        headTables.clear()
        return jsonify(myLists)


class getUpDownAmout(Resource):
    selector = """SELECT COUNT(icmpstatus.icmpstatus) AS amont FROM icmpstatus
				INNER JOIN (SELECT icmpstatus.deviceid,MAX(icmpstatus.icmpid) AS id FROM icmpstatus GROUP BY icmpstatus.deviceid) AS top 
				ON icmpstatus.icmpid = top.id
				INNER JOIN devicedetail ON devicedetail.deviceid = top.deviceid
				WHERE devicedetail.active =1 AND icmpstatus.icmpstatus ={};"""

    def get(self, status):
        sql = sqlTool()
        sql.connectDB()
        self.selector = self.selector.format(status)
        print(self.selector)
        result, headTable = sql.select(self.selector)
        myList = []
        myList.clear()
        for re in result:
            re = list(re)
            myList.append(dict(zip(headTable, re)))
        result.clear()
        headTable.clear()
        sql.disconnectDB()
        return jsonify(myList)
    
class getLocationDistrict(Resource):
    def get(self):
        myList1 = []
        myList2 = []
        myList3 = []
        myList4 = []
        myList5 = []
        selector = """SELECT DISTINCT devicelocation.build FROM devicelocation;"""
        re1 , head1 = sqllib.select(selector)
        selector = """SELECT DISTINCT devicelocation.node FROM devicelocation;"""
        re2 , head2 = sqllib.select(selector)
        selector = """SELECT DISTINCT devicelocation.rack FROM devicelocation;"""
        re3 , head3 = sqllib.select(selector)
        selector = """SELECT DISTINCT devicelocation.location FROM devicelocation;"""
        re4 , head4 = sqllib.select(selector)
        selector = """SELECT DISTINCT devicedetail.contractnumber FROM devicedetail;"""
        re5 , head5 = sqllib.select(selector)
        for res in re1:
            
            myList1.append(res[0])
        for res in re2:
            myList2.append(res[0])
        for res in re3:
            myList3.append(res[0])
        for res in re4:
            myList4.append(res[0])
        for res in re5:
            myList5.append(res[0])
        
        dJson = {
            "node":myList2,
            "rack":myList3,
            "location":myList4,
            "build":myList1,
            "contractnumber":myList5
        }
        return jsonify(dJson)
    
class getHorizonChart(Resource):
    def get(self):
        dataJ = {}
        location = ['build','location','node']
        for item in location:
            myData = []
            selector = """SELECT DISTINCT devicelocation.{loca} FROM devicelocation;"""
            re,head = sqllib.select(selector.format(loca=item))
            for r in re:
                iplist = []
                up = 0
                down = 0
                upList = []
                downList = []
                try:
                    se = """SELECT DISTINCT devicedetail.ip FROM devicedetail
                            INNER JOIN devicelocation ON devicelocation.deviceid = devicedetail.deviceid
                            WHERE devicelocation.{loca} = '{l}' AND devicedetail.active = '1';"""
                    i , he = sqllib.select(se.format(loca=item,l=r[0]))
                    for a in i:
                        iplist.append(a[0])
                except:
                    pass
                if len(iplist) != 0:
                    try:
                        for ip in iplist:
                            s = """SELECT  icmpstatus.icmpstatus FROM icmpstatus
                            WHERE icmpstatus.deviceid = (SELECT DISTINCT devicedetail.deviceid FROM devicedetail WHERE devicedetail.ip = "{iip}")
                            ORDER BY icmpstatus.icmpid DESC
                            LIMIT 1;"""
                            status , hea = sqllib.select(s.format(iip=ip))
                            # print(status[0][0])
                            # print(type(status[0][0]))
                            if status[0][0] == '1':
                                up += 1
                            else:
                                down += 1
                            s2 = """SELECT 
                                        devicedetail.deviceid,
                                        devicedetail.ip,
                                        devicedetail.community,
                                        devicedetail.active,
                                        devicedetail.brand,
                                        devicedetail.`type`,
                                        devicedetail.serialnumber,
                                        devicedetail.contractnumber,
                                        devicelocation.build,
                                        devicelocation.location,
                                        devicelocation.node,
                                        devicelocation.rack
                                    FROM device.devicedetail
                                    INNER JOIN devicelocation ON devicelocation.deviceid = devicedetail.deviceid
                                    WHERE devicedetail.ip = '{iip}';"""
                            status2 , hea2 = sqllib.select(s2.format(iip=ip))
                            if status[0][0] == '1':
                                upList.append(mergeResultHead(status2,hea2)[0])
                            else:
                                downList.append(mergeResultHead(status2,hea2)[0])
                    except:
                        pass
                myData.append({'location':r[0],
                               'up':up,
                               'down':down,
                               'upList' :upList,
                               'downList' :downList})
                # print("mydata",myData)
                dataJ[item] = myData
            # print("dataJ",dataJ[item])
            # dataJ[item].append(myData)
                
        
        return jsonify(dataJ)
    
class getTimestampLog(Resource):
    def get(self, amount):
        json = []
        selector = """SELECT DISTINCT icmpstatus.timedate FROM icmpstatus
                        ORDER BY icmpstatus.timedate DESC
                        LIMIT {amount}
                        ;"""
        re , head = sqllib.select(selector.format(amount=amount))
        # print(re)
        for i in re:
            print(i)
            i = list(i)
            i = i[0].strftime('%Y-%m-%d %H:%M:%S')
            selector2 = """SELECT COUNT(icmpstatus.icmpstatus) FROM icmpstatus
                            WHERE icmpstatus.timedate = "{date}" AND icmpstatus.icmpstatus = "0";"""
            re2 , head2 = sqllib.select(selector2.format(date=i))
            up = re2
            selector2 = """SELECT COUNT(icmpstatus.icmpstatus) FROM icmpstatus
                            WHERE icmpstatus.timedate = "{date}" AND icmpstatus.icmpstatus = "1";"""
            re2 , head2 = sqllib.select(selector2.format(date=i))
            down = re2
            json.append({
                'timestamp':i,
                'up':up[0][0],
                'down':down[0][0],
            })
        return jsonify(json)
        

api.add_resource(getUpDownAmout, "/getupdownamout/<string:status>")
api.add_resource(getTimestampLog, "/getTimestampLog/<string:amount>")
api.add_resource(dashBoard, "/dashboard")
api.add_resource(getLocationDistrict, "/getLocationDistrict")
api.add_resource(getHorizonChart, "/getHorizonChart")


# !----------------------------------------------------------------
# !----------------------------------------------------------------
# !----------------------------------------------------------------


# *----------------------------------------------------------------
# *------------------------  About back end Script hear
# *---------------------------------------------------------------


def job():
    script.main()


def alert_job():
    alert.main()


class toggleScript(Resource):
    def get(self):
        if scheduler.state == 2:
            scheduler.resume()
            return jsonify({'state' : 'on'})
        else:
            scheduler.pause()
            return jsonify({'state' : 'off'})


class getScriptState(Resource):
    def get(self):
        if scheduler.state == 0:
            return jsonify({'state' : 'STATE_STOPPED'})
        elif scheduler.state == 1:
            return jsonify({'state' : 'STATE_RUNNING'})
        else:
            return jsonify({'state' : 'STATE_PAUSED'})


class toggleAlert(Resource):
    def get(self):
        if scheduler2.state == 2:
            scheduler2.resume()
            return jsonify({'state' : 'on'})
        else:
            scheduler2.pause()
            return jsonify({'state' : 'off'})


class getAlertState(Resource):
    def get(self):
        if scheduler2.state == 0:
            return jsonify({'state' : 'STATE_STOPPED'})
        elif scheduler2.state == 1:
            return jsonify({'state' : 'STATE_RUNNING'})
        else:
            return jsonify({'state' : 'STATE_PAUSED'})
import configparser
config = configparser.ConfigParser()
config.read('appsetting.ini')
api.add_resource(toggleScript, "/toggleScript")
api.add_resource(getScriptState, "/getScriptState")
api.add_resource(toggleAlert, "/toggleAlert")
api.add_resource(getAlertState, "/getAlertState")
scheduler = BackgroundScheduler()
scheduler2 = BackgroundScheduler()
scheduler.add_job(func=job, name="icmpSnmp", id='1',
                  trigger="interval", seconds=int(config.get('DEFAULT','looptime')))
scheduler2.add_job(func=alert_job, name="alert", id='2',
                   trigger="interval", seconds=int(config.get('DEFAULT','looptime')))
scheduler.start(paused=True)
scheduler2.start(paused=True)
atexit.register(lambda: scheduler.shutdown())
atexit.register(lambda: scheduler2.shutdown())

# !----------------------------------------------------------------
# !----------------------------------------------------------------
# !----------------------------------------------------------------


class routes(Resource):
    def get(self):
        import urllib
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = urllib.parse.unquote(
                "{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
            output.append(line)
        return jsonify(sorted(output))
        # for line in sorted(output):
        #     print(line)


api.add_resource(routes, "/getAllRoutes")


#  ! app setting

class getHello(Resource):
    def get(self):
        return jsonify({'status':"success",
                        'data':"Hello"})
class getLoopTime(Resource):
    def get(self):
        config = configparser.ConfigParser()
        config.read('appsetting.ini')
        return jsonify({'time':config.get('DEFAULT','looptime')}) 
class getCSV(Resource):
    def get(self):
        import base64

        with open("tamplate.csv", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        
        return jsonify({
            "blob" : str(encoded_string)
        })

class setLoopTime(Resource):
    def get(self,va):
        config = configparser.ConfigParser()
        config.read('appsetting.ini')
        config.set('DEFAULT','looptime',va)
        with open('./alertconfig.ini', 'w') as configfile:
            config.write(configfile)
        return {"task":"success"} 

api.add_resource(getHello, "/")
api.add_resource(setLoopTime, "/setLoopTime/<string:status>")
api.add_resource(getLoopTime, "/getLoopTime")
api.add_resource(getCSV, "/getCSV")


_debug = True
if __name__ == '__main__':
    if _debug == True:
        app.run(debug=True,host="0.0.0.0")
    else:
        app.run(debug=False,host="0.0.0.0")
