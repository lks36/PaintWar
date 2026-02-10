
from robot import * 
import math

nb_robots = 0
debug = False

class Robot_player(Robot):

    team_name = "RansomSearch_2test"
    robot_id = -1
    iteration = 0

    param = []
    trial = 0
    
    #les meilleures stratégies trouvés
    bestParam = []
    best_score = -1000000
    best_trial = 0

    #score de la stratégie courante
    current_trial_score = 0

    #variables pour ccalculer l'effectif à chauque pas
    last_log_translation = 0
    last_log_rotation = 0

    it_per_evaluation = 400
    x_0 = 0
    y_0 = 0
    theta_0 = 0 # in [0,360]

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a",evaluations=0,it_per_evaluation=0):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        self.x_0 = x_0
        self.y_0 = y_0
        self.theta_0 = theta_0

        #initialisation du premier essai
        self.param = [random.randint(-1, 1) for i in range(8)]
        self.it_per_evaluation = it_per_evaluation
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def reset(self):
        super().reset()

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # 1. Calcul du score effectif du pas précédent
        effective_translation = self.log_sum_of_translation - self.last_log_translation
        effective_rotation = self.log_sum_of_rotation - self.last_log_rotation

        # formule de score 
        step_performance = effective_translation*(1.0 - abs(effective_rotation))
        self.current_trial_score += step_performance

        self.last_log_translation = self.log_sum_of_translation
        self.last_log_rotation = self.log_sum_of_rotation

        # toutes les X itérations: le robot est remis à sa position initiale de l'arène avec une orientation aléatoire
        if self.iteration > 0 and self.iteration % self.it_per_evaluation == 0:
                if self.trial < 500:
                    if self.current_trial_score > self.best_score:
                        self.best_score = self.current_trial_score
                        self.bestParam = self.param.copy()
                        self.best_trial = self.trial
                        print("Le nouveux meilleurs score est de '"+str(self.best_score)+"' obtenu à l'essai no."+str(self.best_trial))
                    self.trial = self.trial + 1

                if self.trial >= 500:
                    if(self.trial == 500):
                        print("**********************************************************\n")
                        print("Fin des essais après 500 tentatives.")
                        print("Meilleur score: '"+str(self.best_score)+"' à l'essai no."+str(self.best_trial))
                        print("Meilleure stratégie (paramètres) =",self.bestParam)
                        print("**********************************************************\n")
                        self.trial = 501

                    self.param = self.bestParam.copy()
                    self.it_per_evaluation = 1000
                else:
                    #nouveaux paramètres pour le prochain essai
                    self.param = [random.randint(-1, 1) for i in range(8)]
                    if(self.trial % 50 == 0):
                        print ("Trying strategy no.",self.trial)

                self.current_trial_score = 0
                self.last_log_rotation = 0
                self.last_log_translation = 0
                self.iteration = 0
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
