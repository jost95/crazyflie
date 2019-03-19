import controller.pid_parameters as pidp


class pid:

    def __init__(self, lock, name):
        # Assignment of PIDParameters
        self.__p = pidp.PIDParameters()
        self.__p.Beta = 1.0
        self.__p.H = 0.1
        self.__p.integratorOn = False
        self.__p.K = -0.13
        self.__p.Ti = 0.0
        self.__p.Tr = 10
        self.__p.Td = 1.6
        self.__p.N = 5
        # Initialization of Private Class Variables
        self.__D = 0
        self.__I = 0
        self.__oldY = 0
        self.__e = 0
        self.__v = 0

        self.lock = lock

    def calculateOutput(self, y, yref):
        self.lock.aquire()

        self.__D = (self.p.Td / (self.p.Td + self.p.N * self.p.H)) * self.__D - (
                self.__p.K * self.__p.Td * self.__p.N) * (y - self.__oldY) / (self.__p.Td + self.__p.N * self.__p.H)
        self.__e = yref - y
        self.__v = self.__p.K * (
                    self.__p.Beta * yref - y) + self.__p.I + self.__p.D  # I is 0.0 if integratorOn is false
        self.__oldY = y

        self.lock.release()
        return self.__v

    def updateState(self, u):
        if self.__p.integratorOn:
            self.__I = self.__I + (self.__p.K * self.__p.H / self.__p.Ti) * self.__e + (self.__p.H / self.__p.Tr) * (u -self.__v)
        else:
            self.__I = 0

    def getHmillis(self):
        return self.__p.H * 1000

    def setParameters(self):
    # Do later
        pass
