from multiping import MultiPing
from multiping import multi_ping

class icmpTool():

    timeout = 1
    
    def __init__(self,ipList): 
        self.icmpList = []
        for i in ipList:
            self.icmpList.append(i[1])
    
    def icmpSend(self):    
        mp = MultiPing(self.icmpList)
        mp.send()
        self.responses, self.no_responses = mp.receive(self.timeout)
        return self.responses, self.no_responses
    
    # With a 1 second timout, wait for responses (may return sooner if all
    # results are received).
    
    #func for testing
    def show(self):
        for addr, rtt in self.responses.items():
            print("%s responded in %f seconds" % (addr, rtt))
            if self.no_responses:
                print("These addresses did not respond: %s" % ", ".join(self.no_responses))
            