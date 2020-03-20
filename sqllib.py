import mysql.connector
from mysql.connector import errorcode
from sqlcreat import sqlCreat
import json
import datetime
import configparser

s = sqlCreat()
config = configparser.ConfigParser()
config.read('appsetting.ini')
host = config.get('MYSQL','host')
port = config.get('MYSQL','port')
user = config.get('MYSQL','user')
passwd = config.get('MYSQL','passwd')
database = config.get('MYSQL','databasename')

def connectDB():  # connect to database
    try:
        mydb = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            passwd=passwd,
            database=database
        )
        mycursor = mydb.cursor()
        print("connected DB")
        return mydb,mycursor
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist. create one name " + database)
            mydb = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                passwd=passwd,)
            mycursor = mydb.cursor()
            mycursor.execute(s.createDatabase) #creat database device
            mydb.close()
            mydb = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                passwd=passwd,
                database=database
            )
            mycursor = mydb.cursor()
            return mydb,mycursor
        else:
            print(err)
def disconnectDB(db):  # disconnect from DB
    db.close()
    # print("disconnected")

def selectActive():  # select only avtive device
    try:
        mydb , mycursor = connectDB()
        mycursor.execute("select deviceid,ip,community from devicedetail where active = 1")
        myresult = mycursor.fetchall()
        disconnectDB(mydb)
        resultList = []
        for x in myresult:
            resultList.append(x)
        return resultList #myresult -> resultList
    except Exception as e:
        print(e)

def selectCommon(selectColume,fromTable,condition): #common select sql
    try:
        mycursor.execute("SELECT " + selectColume + " FROM " + fromTable + " " + condition)
        myresult = mycursor.fetchall()
        for x in myresult:
            resultList.append(x)
        return resultList
    except Exception as e:
        print(e) 

def select(selector):
    try:
        mydb , mycursor = connectDB()
        
        mycursor.execute(selector)
        row_headers=[x[0] for x in mycursor.description] #this will extract row headers
        myresults = mycursor.fetchall()
        resultLists = []
        for x in myresults:
            resultLists.append(x)
        disconnectDB(mydb)
        return resultLists , row_headers
    except Exception as e:
        print(e)   

def insertor(insertor):
    try:
        mydb , mycursor = connectDB()
        mycursor.execute(insertor)
        mydb.commit()
        disconnectDB(mydb)
    except mysql.connector.Error as err:
            print(err)
            
def updator(updator):
    try:
        mydb , mycursor = connectDB()
        mycursor.execute(updator)
        mydb.commit()
        disconnectDB(mydb)
        return True
    except mysql.connector.Error as err:
            print(err)
            return False
            
def deletor(deletor):
    try:
        mydb , mycursor = connectDB()
        mycursor.execute(deletor)
        mydb.commit()
        disconnectDB(mydb)
        return True
    except mysql.connector.Error as err:
            print(err)
            return False
            
def executor(executor):
    try:
        mydb , mycursor = connectDB()
        mycursor.execute(executor)
        mydb.commit()
        count = mycursor.rowcount
        disconnectDB(mydb)
        if count == 0:
            return False
        else:
            return True
    except mysql.connector.Error as err:
            print(err)   
            
def uploadDevice():
    try:
        #TODO : insert
        mycursor.execute(s.creatTableSnmpStatus)
    except mysql.connector.Error as err:
        if err.errno == 1146:
            mycursor.execute(s.creatTableDeviceDetail)
            
        else:
            print(err)

def uploadStatusICMP(deviceId,status,time):
    try:
        val = (deviceId,status,time)
        mycursor.execute(s.insertIcmp,val)
        mydb.commit()
    except mysql.connector.Error as err:
        if err.errno == 1146:
            mycursor.execute(s.creatTableIcmpStatus)
            val = (deviceId,status,time)
            mycursor.execute(s.creatTableIcmpStatus,val)
            mydb.commit()
        else:
            print(err)

def uploadStatusSNMP(deviceId,hostName,upTime,desc):
    try:    
        ## check This deviceId already have in snmpStatuis? 
        checker = """SELECT EXISTS(SELECT * FROM snmpstatus WHERE snmpstatus.deviceid = %s)"""
        # print(checker %deviceId)
        mycursor.execute(checker %deviceId)
        myresult = mycursor.fetchall()
        isHaveId = myresult[0][0]
        
        
        ##get icmpId to be ForKEY for snmp
        lastId ="""SELECT MAX(icmpstatus.icmpid) FROM icmpstatus;"""
        mycursor.execute(lastId)
        lastIds = mycursor.fetchall()
        icmpId = lastIds[0][0]
        
        
        if isHaveId == 1:
            # print("*UploadSNMP : this device already have in snmp -> update data*")
            # print(type(deviceId),type(icmpId),type(hostName),type(upTime),type(desc))
            val = (icmpId,hostName,upTime,desc,deviceId)
            mycursor.execute(s.updateSnmp,val)
            mydb.commit()
        else:
            # print("*UploadSNMP : this device not have in snmp -> insert new*")
            # print(type(deviceId),type(icmpId),type(hostName),type(upTime),type(desc))
            val = (deviceId,icmpId,hostName,upTime,desc)
            mycursor.execute(s.insertSnmp,val)
            mydb.commit()
    except mysql.connector.Error as err:
        if err.errno == 1146:
            print("***ERROR : UPloadSNMP : no table -> creat one***")
            mycursor.execute(s.creatTableSnmpStatus)
            mycursor.execute(s.creatTablePortSnmpStatus)
            print(err)
        else:
            print("***ERROR : UPloadSNMP***")
            print(err)
            
def uploadPortStatusSNMP(deviceId,portIndex,portType,portStatus,portPotocol):
    try:    
        ## check This deviceId already have in PortStatusSNMP? 
        checker = """SELECT EXISTS(SELECT * FROM portsnmpstatus WHERE portsnmpstatus.deviceid = %s)"""
        # print(checker %deviceId)
        mycursor.execute(checker %deviceId)
        myresult = mycursor.fetchall()
        isHaveId = myresult[0][0]
        # print(isHaveId)
        # print(type(isHaveId))
        
        
        ##get icmpId to be ForKEY for snmp
        lastId ="""SELECT MAX(icmpstatus.icmpid) FROM icmpstatus;"""
        mycursor.execute(lastId)
        lastIds = mycursor.fetchall()
        icmpId = lastIds[0][0]
        
        
        if isHaveId == 1:
            print("*UploadSNMP : this device already have in snmp -> update data*")
            # print(type(deviceId),type(icmpId),type(hostName),type(upTime),type(desc))
            for i in range(len(portIndex)):
                val = (icmpId,portType[i],portStatus[i],portPotocol[i],deviceId,portIndex[i])
                mycursor.execute(s.updatePortSnmp,val)
                mydb.commit()  
        else:
            print("*UploadSNMP : this device not have in snmp -> insert new*")
            # print(type(deviceId),type(icmpId),type(hostName),type(upTime),type(desc))
            for i in range(len(portIndex)):
                val = (deviceId,icmpId,portIndex[i],portType[i],portStatus[i],portPotocol[i])
                mycursor.execute(s.insertPortSnmp,val)
                mydb.commit() 
    except mysql.connector.Error as err:
        if err.errno == 1146:
            print("***ERROR : UPloadPortSNMP : no table -> creat one***")
            mycursor.execute(s.creatTablePortSnmpStatus)
            print(err)
        else:
            print("***ERROR : UPloadPortSNMP***")
            print(err)

def main():
    selector = "SELECT * FROM user WHERE user.username ='admin' AND user.password = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92';"
    # selector = selector.format(user,passW)
    results , head = select(selector)
    print(results)
    
        
        


if __name__ == '__main__':
    main()