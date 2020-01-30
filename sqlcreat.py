# database device
# table devicedetail devicestatus deviceinterface


class sqlCreat:
    databasename = "device"
    creatDatabase = "CREATE DATABASE device;"

    creatTableDeviceDetail = """CREATE TABLE devicedetail (
                    deviceid int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    ip VARCHAR(15) NOT NULL,
                    community VARCHAR(20) NOT NULL,
                    active tinyint(4) NOT NULL);"""

    creatTableIcmpStatus = """CREATE TABLE icmpstatus (
                    icmpid int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    icmpstatus varchar(20) NOT NULL,
					deviceid int,
                    timedate DATETIME DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
					FOREIGN KEY(deviceid) REFERENCES devicedetail(deviceid));"""

    creatTableSnmpStatus = """CREATE TABLE snmpstatus (
                    deviceid int,
                    icmpid int,
                    hostname VARCHAR(20),
                    upTime int,
                    description VARCHAR(255),
					FOREIGN KEY(deviceid) REFERENCES devicedetail(deviceid),
					FOREIGN KEY(icmpid) REFERENCES icmpstatus(icmpid));"""

    creatTablePortSnmpStatus = """CREATE TABLE portsnmpstatus (
                    deviceid int,
                    icmpid int,
                    portIndex VARCHAR(20),
                    porttype VARCHAR(20),
                    portstatus varchar(20),
                    portpotocol varchar(20),
					FOREIGN KEY(deviceid) REFERENCES devicedetail(deviceid),
					FOREIGN KEY(icmpid) REFERENCES icmpstatus(icmpid));"""
    # status 1 is Up 2 is Down

    # TODO : insert sql
    insertDevice = """INSERT INTO Customers (CustomerName, ContactName, Address, City, PostalCode, Country) VALUES """
    insertIcmp = """INSERT INTO icmpstatus (deviceid, icmpid, icmpstatus , timedate) VALUES (%s, NULL, %s ,%s)"""
    insertSnmp = """INSERT INTO snmpstatus (deviceid, icmpid, hostname, upTime , description) VALUES (%s, %s, %s, %s, %s)"""
    insertPortSnmp = """INSERT INTO portsnmpstatus (deviceid, icmpid, portIndex, porttype , portstatus , portpotocol) VALUES ( %s, %s, %s, %s, %s ,%s)"""

    updateSnmp = """UPDATE snmpstatus
    SET icmpid = %s, hostname = %s,upTime= %s , description = %s
    WHERE deviceid = %s;"""
    updatePortSnmp = """UPDATE portsnmpstatus
    SET icmpid = %s , porttype= %s , portstatus = %s , portpotocol = %s
    WHERE deviceid = %s AND portIndex = %s;"""
