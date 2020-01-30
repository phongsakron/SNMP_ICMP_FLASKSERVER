from icmpTool import icmpTool
from snmpTool import snmpTool
from sqltool import sqlTool
import snmpNameOid
import datetime
import time
import logging

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")


def main():
    logging.info("main() : Start")
   
    
    # TODO : make thred then do this every ... Time
    sql = sqlTool()
    sql.connectDB()
    # list any active ip
    iplist = []
    active = sql.selectActive()
    for id, ip, commu in active:
        iplist.append([id, ip, commu])
    # #let ping any active device
    for i in iplist:
        logging.info("main() : List active %s",i)
    icmp = icmpTool(iplist)
    logging.info("main() : send ICMP wait for respon")
    res, no_res = icmp.icmpSend()
    #
    time = datetime.datetime.now()
    logging.info("main() : TimeStamp %s",time.strftime("%Y-%m-%d %H:%M:%S"))
    if(res):
        logging.info("main() : res : %s",res)
        
        for ip in res:
            for listone in iplist:
                if ip in listone:
                    #upload ICMP
                    sql.uploadStatusICMP(listone[0], '1' , time.strftime("%Y-%m-%d %H:%M:%S"))
                    logging.info("main() : res : %s upload ICMP",ip)
                    #DO SNMP
                    mydevice = snmpTool(listone[2],listone[1])
                
                    mydevice.setOid(snmpNameOid.deviceHostName)
                    hostname = mydevice.getSNMPbyOid()
                    # print(hostname)


                    mydevice.setOid(snmpNameOid.deviceUpTime)
                    uptime = mydevice.getSNMPbyOid()
                    seconds  = int(uptime)/100
                    # print(datetime.timedelta(seconds=seconds ))


                    mydevice.setOid(snmpNameOid.deviceDesc)
                    desc = mydevice.getSNMPbyOid()
                    # print(desc)
                    sql.uploadStatusSNMP(listone[0],hostname,uptime,desc)
                    
                    #  port status
                    mydevice.setOid(snmpNameOid.portIndex)
                    portIndex = mydevice.bulkSNMPbyOid()
                    
                    mydevice.setOid(snmpNameOid.portType)
                    portType = mydevice.bulkSNMPbyOid()
                    
                    mydevice.setOid(snmpNameOid.portStatus)
                    portStatus = mydevice.bulkSNMPbyOid()
                    
                    mydevice.setOid(snmpNameOid.portPotocol)
                    portPotocol = mydevice.bulkSNMPbyOid()
                    
                    sql.uploadPortStatusSNMP(listone[0],portIndex,portType,portStatus,portPotocol)
                    
                    

    if(no_res):
        logging.info("main() : no_res : %s",no_res)
        # print(no_res)
        for ip in no_res:
            # logging.info("main() : no_res : %s",ip)
            for listone in iplist:
                if ip in listone:
                    #upload ICMP
                    sql.uploadStatusICMP(listone[0], '0',time.strftime("%Y-%m-%d %H:%M:%S"))
                    # print("ICMP no res ", no_res, " : status uploaded")
                    logging.info("main() : no_res :  %s upload ICMP",ip)
    res.clear()
    no_res.clear()
    iplist.clear()
    active.clear()
    sql.disconnectDB();
    del sql

if __name__ == '__main__':
    main()
    


# make scheduler
# make thread
    # dowork
# done and wait for next time


