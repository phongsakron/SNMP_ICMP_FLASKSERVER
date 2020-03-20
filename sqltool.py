import mysql.connector
from mysql.connector import errorcode
from sqlcreat import sqlCreat
import json
import datetime
import configparser

class sqlTool:
    s = sqlCreat()

    config = configparser.ConfigParser()
    config.read('appsetting.ini')
    host = config.get('MYSQL','host')
    user = config.get('MYSQL','user')
    passwd = config.get('MYSQL','passwd')
    database = config.get('MYSQL','databasename')

    resultList = []
  
    def connectDB(self):  # connect to database
        try:
            self.mydb = mysql.connector.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                database=self.database
            )
            self.mycursor = self.mydb.cursor()
            print("connected DB")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist. create one name " + self.database)
                self.mydb = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    passwd=self.passwd,)
                self.mycursor = self.mydb.cursor()
                self.mycursor.execute(self.s.createDatabase) #creat database device
                self.mydb.close()
                self.mydb = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    passwd=self.passwd,
                    database=self.database
                )
            else:
                print(err)

    def selectActive(self):  # select only avtive device
        try:
            self.mycursor.execute("select deviceid,ip,community from devicedetail where active = 1")
            self.myresult = self.mycursor.fetchall()
            for x in self.myresult:
                self.resultList.append(x)
            return self.resultList #myresult -> resultList
        except Exception as e:
            print(e)

    def selectCommon(self,selectColume,fromTable,condition): #common select sql
        try:
            self.mycursor.execute("SELECT " + selectColume + " FROM " + fromTable + " " + condition)
            myresult = self.mycursor.fetchall()
            for x in myresult:
                self.resultList.append(x)
            return self.resultList
        except Exception as e:
            print(e) 
    
    def select(self,selector):
        try:
            self.mycursor.execute(selector)
            self.row_headers=[x[0] for x in self.mycursor.description] #this will extract row headers
            self.myresults = self.mycursor.fetchall()
            for x in self.myresults:
                self.resultLists.append(x)
            return self.resultLists , self.row_headers
        except Exception as e:
            print(e)   
    
        
    def uploadDevice(self):
        try:
            #TODO : insert
            self.mycursor.execute(self.s.creatTableSnmpStatus)
        except mysql.connector.Error as err:
            if err.errno == 1146:
                self.mycursor.execute(self.s.creatTableDeviceDetail)
                
            else:
                print(err)

    def uploadStatusICMP(self,deviceId,status,time):
        try:
            val = (deviceId,status,time)
            self.mycursor.execute(self.s.insertIcmp,val)
            self.mydb.commit()
        except mysql.connector.Error as err:
            if err.errno == 1146:
                self.mycursor.execute(self.s.creatTableIcmpStatus)
                val = (deviceId,status,time)
                self.mycursor.execute(self.s.creatTableIcmpStatus,val)
                self.mydb.commit()
            else:
                print(err)

    def uploadStatusSNMP(self,deviceId,hostName,upTime,desc):
        try:    
            ## check This deviceId already have in snmpStatuis? 
            checker = """SELECT EXISTS(SELECT * FROM snmpstatus WHERE snmpstatus.deviceid = %s)"""
            print(checker %deviceId)
            self.mycursor.execute(checker %deviceId)
            myresult = self.mycursor.fetchall()
            isHaveId = myresult[0][0]
            
            
            ##get icmpId to be ForKEY for snmp
            lastId ="""SELECT MAX(icmpstatus.icmpid) FROM icmpstatus;"""
            self.mycursor.execute(lastId)
            lastIds = self.mycursor.fetchall()
            icmpId = lastIds[0][0]
            
            
            if isHaveId == 1:
                print("*UploadSNMP : this device already have in snmp -> update data*")
                # print(type(deviceId),type(icmpId),type(hostName),type(upTime),type(desc))
                val = (icmpId,hostName,upTime,desc,deviceId)
                self.mycursor.execute(self.s.updateSnmp,val)
                self.mydb.commit()
            else:
                print("*UploadSNMP : this device not have in snmp -> insert new*")
                # print(type(deviceId),type(icmpId),type(hostName),type(upTime),type(desc))
                val = (deviceId,icmpId,hostName,upTime,desc)
                self.mycursor.execute(self.s.insertSnmp,val)
                self.mydb.commit()
        except mysql.connector.Error as err:
            if err.errno == 1146:
                print("***ERROR : UPloadSNMP : no table -> creat one***")
                self.mycursor.execute(self.s.creatTableSnmpStatus)
                self.mycursor.execute(self.s.creatTablePortSnmpStatus)
                print(err)
            else:
                print("***ERROR : UPloadSNMP***")
                print(err)
                
    def uploadPortStatusSNMP(self,deviceId,portIndex,portType,portStatus,portPotocol):
        try:    
            ## check This deviceId already have in PortStatusSNMP? 
            checker = """SELECT EXISTS(SELECT * FROM portsnmpstatus WHERE portsnmpstatus.deviceid = %s)"""
            print(checker %deviceId)
            self.mycursor.execute(checker %deviceId)
            myresult = self.mycursor.fetchall()
            isHaveId = myresult[0][0]
            # print(isHaveId)
            # print(type(isHaveId))
            
            
            ##get icmpId to be ForKEY for snmp
            lastId ="""SELECT MAX(icmpstatus.icmpid) FROM icmpstatus;"""
            self.mycursor.execute(lastId)
            lastIds = self.mycursor.fetchall()
            icmpId = lastIds[0][0]
            
            
            if isHaveId == 1:
                print("*UploadSNMP : this device already have in snmp -> update data*")
                # print(type(deviceId),type(icmpId),type(hostName),type(upTime),type(desc))
                for i in range(len(portIndex)):
                    val = (icmpId,portType[i],portStatus[i],portPotocol[i],deviceId,portIndex[i])
                    self.mycursor.execute(self.s.updatePortSnmp,val)
                    self.mydb.commit()  
            else:
                print("*UploadSNMP : this device not have in snmp -> insert new*")
                # print(type(deviceId),type(icmpId),type(hostName),type(upTime),type(desc))
                for i in range(len(portIndex)):
                    val = (deviceId,icmpId,portIndex[i],portType[i],portStatus[i],portPotocol[i])
                    self.mycursor.execute(self.s.insertPortSnmp,val)
                    self.mydb.commit() 
        except mysql.connector.Error as err:
            if err.errno == 1146:
                print("***ERROR : UPloadPortSNMP : no table -> creat one***")
                self.mycursor.execute(self.s.creatTablePortSnmpStatus)
                print(err)
            else:
                print("***ERROR : UPloadPortSNMP***")
                print(err)

    def disconnectDB(self):  # disconnect from DB
        self.mydb.close()
        print("disconnected")
