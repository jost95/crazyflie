import controller.pid_parameters as pidp

class pid(:

    def __init__(self):
        self.p = pidp.PIDParameters()
        pass


    #self
    #PIDParameters
    #p = new
    #PIDParameters();
    #p.Beta = 1.0;
    #p.H = 0.1;
    #p.integratorOn = false;
    #p.K = -0.13;
    #p.Ti = 0.0;
    #p.Tr = 10.0;
    #p.Td = 1.6;
    #p.N = 5;


    def calculateOutput(self):
        pass

    def updateState(self):
        pass

    def getHmillis(self):
        pass

    def setParameters(self):
        pass

c = pid ()