import smtplib, ssl
import configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqltool import sqlTool
import time
import sqllib



def mergeResultHead(re,head):
    myLists = []
    for res in re:
            res = list(res)
            myLists.append(dict(zip(head, res)))
    return myLists

def getDownlist():
    
    downList = []
    downList.clear()
    selector = """SELECT DISTINCT devicedetail.ip FROM devicedetail
                WHERE devicedetail.active = 1;
                """
		
    ip,head = sqllib.select(selector)
    
    for i in ip:
        # print(i[0])
        selector = """SELECT devicelocation.locationID,devicelocation.build,devicelocation.location,devicelocation.node,devicelocation.rack,devicedetail.active, icmpstatus.icmpid AS lastCheck ,icmpstatus.deviceid, devicedetail.ip , icmpstatus.icmpstatus , icmpstatus.timedate FROM devicedetail
                        INNER JOIN devicelocation ON devicelocation.deviceid = devicedetail.deviceid
                        INNER JOIN icmpstatus ON icmpstatus.deviceid = devicedetail.deviceid
                        WHERE devicedetail.ip = '{ip}' 
                        ORDER BY icmpstatus.icmpid DESC
                        LIMIT 1;"""
        
        re , he = sqllib.select(selector.format(ip=i[0]))
        r = mergeResultHead(re,he)

        if(len(r) != 0):
            if(r[0]['icmpstatus']=='0'):
                downList.append(r)
                print(r[0]['icmpstatus'],r[0]['ip'])
       
        
  
    # print(downList)
    return downList
    


    
def sendmail(sendmsg,receiver):
    named_tuple = time.localtime() # get struct_time
    time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
    
    config = configparser.ConfigParser()
    config.read('./alertconfig.ini')
    # print(config.sections())
    smtp_server = config['mail']["mailServer"]
    port = config['mail']["port"]  # For starttls
    sender_email = config['sender']["username"]
    password = config['sender']["password"]
    receiver_email = receiver
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "[Alert] NetworkMonitoringSystem " + time_string
    body = sendmsg
    msg.attach(MIMEText(body, 'plain'))
    # Create a secure SSL context
    context = ssl.create_default_context()
    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.starttls(context=context) # Secure the connection
        server.login(sender_email, password)
        # TODO: Send email here
        server.sendmail(sender_email, receiver_email, msg.as_string())
        # print("success")
    except Exception as e:
        # print any error messages to stdout
        print(e)
    finally:
        server.quit() 
    # config.set('mail','port','586')
    # with open('./alertconfig.ini', 'w') as configfile:
    # 	config.write(configfile)


def main():
    myList = getDownlist()
    msg = "Please Check Device Below:\n\n---------------------------------------------------------------------\n\n"
    ip = ""

    # print(myList)
    for li in myList:
        ip += "IP: " + str(li[0]['ip']) + " ,Location :"+ str(li[0]['location']) + " ,Building :"+ str(li[0]['build']) + " ,Node :"+ str(li[0]['node']) + " ,LastCheckTime :"+ str(li[0]['timedate']) + "\n"

    msg += ip
    # print(msg)
    selector = """SELECT DISTINCT user.email FROM user
    WHERE user.emailAlert = 1;"""
    re , head = sqllib.select(selector)
    print(re)
    for r in re:
        user = r[0]
        # sendmail(msg,user)
        if(len(myList)!=0):
            try:
                sendmail(msg,user)
                print("success send email to",user)
            except Exception as err:
                print("cannt send email to",user)
                print(err)
            
        
        
if __name__ == '__main__':
    main()
    