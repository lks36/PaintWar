from robot import *
import math
import random

nb_robots = 0
debug = False

class Robot_player(Robot):

    team_name = "RandomSearch_Final"
    robot_id = -1
    iteration = 0

    param = []
    trial = 0
    
    # Suivi de la meilleure performance
    bestParam = []
    best_score = -1.0 # Initialisé bas pour capturer le premier résultat
    best_trial = 0

    # Score accumulé pour l'essai en cours
    current_trial_score = 0

    # Variables pour calculer les différentielles (valeurs effectives)
    last_log_translation = 0
    last_log_rotation = 0

    it_per_evaluation = 400
    x_0 = 0
    y_0 = 0
    theta_0 = 0 

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a", evaluations=0, it_per_evaluation=400):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        self.x_0 = x_0
        self.y_0 = y_0
        self.theta_0 = theta_0

        # Initialisation aléatoire du premier comportement
        self.param = [random.randint(-1, 1) for i in range(8)]
        self.it_per_evaluation = it_per_evaluation if it_per_evaluation > 0 else 400
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # 1. Calcul de la performance effective de ce pas de temps
        # On soustrait la valeur cumulée précédente de la valeur actuelle
        effective_translation = self.log_sum_of_translation - self.last_log_translation
        effective_rotation = self.log_sum_of_rotation - self.last_log_rotation

        # Formule demandée : translation * (1 - abs(rotation))
        step_performance = effective_translation * (1.0 - abs(effective_rotation))
        self.current_trial_score += step_performance

        # Mise à jour des logs pour le prochain pas
        self.last_log_translation = self.log_sum_of_translation
        self.last_log_rotation = self.log_sum_of_rotation

        # 2. Gestion de la fin d'une évaluation
        if self.iteration > 0 and self.iteration % self.it_per_evaluation == 0:
            
            # PHASE DE RECHERCHE (jusqu'à 500 essais)
            if self.trial < 500:
                if self.current_trial_score > self.best_score:
                    self.best_score = self.current_trial_score
                    self.bestParam = self.param.copy()
                    self.best_trial = self.trial
                    print(f"Trial {self.trial}: Nouveau record ! Score = {self.best_score:.2f}")
                
                self.trial += 1

            # TRANSITION VERS LE MODE REPLAY
            if self.trial >= 500:
                if self.trial == 500:
                    print("\n" + "*"*40)
                    print(f"RECHERCHE TERMINEE. Meilleur score: {self.best_score:.2f}")
                    print(f"Meilleurs paramètres: {self.bestParam}")
                    print("MODE REPLAY ACTIVE (1000 itérations)")
                    print("*"*40 + "\n")
                    self.trial = 501 # Empêche de répéter le message

                # Charger définitivement la meilleure stratégie trouvée
                self.param = self.bestParam.copy()
                self.it_per_evaluation = 1000 
            else:
                # Générer un nouveau comportement aléatoire pour l'essai suivant
                self.param = [random.randint(-1, 1) for i in range(8)]
                if self.trial % 50 == 0:
                    print(f"Progression: Essai n°{self.trial}/500...")

            # Réinitialisation pour le cycle suivant
            self.current_trial_score = 0
            self.last_log_rotation = 0
            self.last_log_translation = 0
            self.iteration = 0 # Crucial pour que le modulo fonctionne au tour suivant
            return 0, 0, True # Demande de reset de position au simulateur

        # 3. Fonction de contrôle (Perceptron simple)
        translation = math.tanh(self.param[0] + self.param[1] * sensors[0] + self.param[2] * sensors[1] + self.param[3] * sensors[2])
        rotation = math.tanh(self.param[4] + self.param[5] * sensors[0] + self.param[6] * sensors[1] + self.param[7] * sensors[2])

        self.iteration += 1        
        return translation, rotation, False