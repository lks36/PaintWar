
from robot import * 
import math

nb_robots = 0
debug = False

class Robot_player(Robot):

    team_name = "Optimizer"
    robot_id = -1
    iteration = 0

    param = []
    parent_param=[]
    fils_param=[]
    bestParam = []
    it_per_evaluation = 400
    trial = 0
    
    parent_score=0
    fils_score=0
    x_0 = 0
    y_0 = 0
    theta_0 = 0 # in [0,360]
    best_score=0

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a",evaluations=0,it_per_evaluation=0):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        self.x_0 = x_0
        self.y_0 = y_0
        self.theta_0 = theta_0
        self.param = [random.randint(-1, 1) for i in range(8)]
        self.parent_param = self.param.copy()
        self.fils_param = self.param.copy()
        self.it_per_evaluation = it_per_evaluation
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def reset(self):
        super().reset()


    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # cet exemple montre comment générer au hasard, et évaluer, des stratégies comportementales
        # Remarques:
        # - la liste "param", définie ci-dessus, permet de stocker les paramètres de la fonction de contrôle
        # - la fonction de controle est une combinaison linéaire des senseurs, pondérés par les paramètres (c'est un "Perceptron")

        # toutes les X itérations: le robot est remis à sa position initiale de l'arène avec une orientation aléatoire
        if self.iteration % ((self.it_per_evaluation)*2) == 0:
            self.fils_score=self.log_sum_of_translation * ( 1 - abs(self.log_sum_of_rotation) )
            self.fils_param=self.param.copy()
            print("\tf_score                =",self.fils_score)
            print("\tf_param               =",self.fils_param)
            if(self.fils_score>self.parent_score):
                self.bestParam=self.fils_param.copy()
                self.best_score=self.fils_score
                self.param=self.fils_param.copy()
                print("\tbest_score                 =",self.best_score)
                print("\tbest_param                 =",self.bestParam)
            if(self.fils_score<self.parent_score):
                self.param=self.parent_param.copy()

                self.trial = self.trial + 1
                print ("Trying strategy no.",self.trial)
                self.iteration = self.iteration + 1
                return 0, 0, True # ask for reset

        elif self.iteration % self.it_per_evaluation == 0:
                self.parent_score = self.log_sum_of_translation * ( 1 - abs(self.log_sum_of_rotation) )
                print("\tp_score                =",self.parent_score)
                print("\tp_param               =",self.parent_param)
                self.parent_param=self.param.copy()

                index=random.randint(0,4)
                old_value = self.param[index]

                # choisir une nouvelle valeur différente
                choices = [-1, 0, 1]
                choices.remove(old_value)
                new_value = random.choice(choices)
                self.param[index]=new_value
                self.iteration = self.iteration + 1
                return 0, 0, True # ask for reset

        # fonction de contrôle (qui dépend des entrées sensorielles, et des paramètres)
        translation = math.tanh ( self.param[0] + self.param[1] * sensors[sensor_front_left] + self.param[2] * sensors[sensor_front] + self.param[3] * sensors[sensor_front_right] )
        rotation = math.tanh ( self.param[4] + self.param[5] * sensors[sensor_front_left] + self.param[6] * sensors[sensor_front] + self.param[7] * sensors[sensor_front_right] )

        if debug == True:
            if self.iteration % 100 == 0:
                print ("Robot",self.robot_id," (team "+str(self.team_name)+")","at step",self.iteration,":")
                print ("\tsensors (distance, max is 1.0)  =",sensors)
                print ("\ttype (0:empty, 1:wall, 2:robot) =",sensor_view)
                print ("\trobot's name (if relevant)      =",sensor_robot)
                print ("\trobot's team (if relevant)      =",sensor_team)

        self.iteration = self.iteration + 1        

        return translation, rotation, False
