from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen


class snmpTool:

    comStr = ""
    ipAdd = ""
    oidAdd = ""

    def __init__(self, communityString, ipAddress):
        self.comStr = communityString
        self.ipAdd = ipAddress

    def setOid(self, oid):
        self.oidAdd = oid

    def show(self):
        print("Com = "+ self.comStr + " ip = " + self.ipAdd + " oid = " +self.oidAdd)

    def getSNMPbyName(self, mibName):
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(self.comStr, mpModel=0),
                   UdpTransportTarget((self.ipAdd, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', mibName, 0)))
        )

        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                # print(' == '.join([x.prettyPrint() for x in varBind]))
                a = [x.prettyPrint() for x in varBind]
                return a[1]

    def getSNMPbyOid(self):
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(self.comStr, mpModel=0),
                   UdpTransportTarget((self.ipAdd, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(self.oidAdd)))
        )
        for varBind in varBinds:
            a = [x.prettyPrint() for x in varBind]
            return a[1]

    def bulkSNMPbyOid(self):
        a = []
        errorIndication, errorStatus, errorIndex, \
            varBindTable = cmdgen.CommandGenerator().bulkCmd(
                cmdgen.CommunityData(self.comStr),
                cmdgen.UdpTransportTarget((self.ipAdd, 161)),
                0,
                25,
                (self.oidAdd),
            )
        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s\n' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
                ))
            else:
                for varBindTableRow in varBindTable:
                    for name, val in varBindTableRow:
                        # print ('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
                        a.append(val.prettyPrint())
        return a
