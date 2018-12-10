import math
import pygal

class room:

    def __init__(self, name):
        self.name = name
        #self.ID = ID
        self.Price = [0, 0, 0] #[negative, mid, positive]
        self.Environment = [0, 0, 0]
        self.Location = [0, 0, 0]
        self.Service = [0, 0, 0]
        self.Others = [0, 0, 0]
        self.P_grade = 0
        self.E_grade = 0
        self.L_grade = 0
        self.S_grade = 0
        self.O_grade = 0

    def Load(self, dict_1):
        self.Price = dict_1['Price']
        self.Environment = dict_1['Environment']
        self.Location = dict_1['Location']
        self.Service = dict_1['Service']
        self.Others = dict_1['Others']

    def Calc_Grade(self):
        self.P_grade = 100 * (self.Price[2]/sum(self.Price) + 0.5 * self.Price[1]/sum(self.Price))
        self.E_grade = 100 * (self.Environment[2]/sum(self.Environment) + 0.5 * self.Environment[1]/sum(self.Environment))
        self.L_grade = 100 * (self.Location[2]/sum(self.Location) + 0.5 * self.Location[1]/sum(self.Location))
        self.S_grade = 100 * (self.Service[2]/sum(self.Service) + 0.5 * self.Service[1]/sum(self.Service))
        self.O_grade = 100 * (self.Others[2]/sum(self.Others) + 0.5 * self.Others[1]/sum(self.Others))

    def Radar_Chart(self):
        radar_chart = pygal.Radar(fill = True, range = (0,100))
        radar_chart.title = self.name + ' Grading'
        radar_chart.x_labels = ['Price', 'Environment', 'Location', 'Service', 'Others']
        radar_chart.add(self.name, [self.P_grade, self.E_grade, self.L_grade, self.S_grade, self.O_grade])
        # return radar_chart.render_response()
        

