# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : _________
#  Prénom Nom No_étudiant/e : _________
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import *
import math


nb_robots = 0

class Robot_player(Robot):

    team_name = "Challenger"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a",evaluations=0,it_per_evaluation=0):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        self.x_0 = x_0
        self.y_0 = y_0
        self.theta_0 = theta_0
        self.param = [random.randint(-1, 1) for i in range(8)]
        self.it_per_evaluation = it_per_evaluation
        super().__init__(x_0, y_0, theta_0, name=name, team=team)
    
        def reset(self):
            super().reset()

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # 1. Mise à jour de la mémoire (Compteur de temps pour changement de zone)
        self.memory = (self.memory + 1) % 200
        
        # indices senseurs (selon tetracomposibot.py)
        # 0: front, 1: front_left, 7: front_right
        f = sensors[0]
        fl = sensors[1]
        fr = sensors[7]

        # --- Architecture de Subsumption ---

        # PRIORITÉ 1: Anti-stuck / Changement de zone stratégique
        # Toutes les X itérations, on force un virage pour explorer une autre partie de la carte
        if 200 < self.memory < 220:
            # Virage forcé basé sur l'ID pour que chaque robot parte dans une direction différente
            return 0.5, (1.0 if self.robot_id % 2 == 0 else -1.0), False

        # PRIORITÉ 2: Évitement d'urgence (Murs ou Robots)
        # Si un obstacle est très proche devant, on tourne sur place
        if f < 0.15:
            # On tourne du côté le plus libre
            rotation = 1.0 if fl > fr else -1.0
            return 0.1, rotation, False

        # PRIORITÉ 3: Répulsion des coéquipiers (Multi-agent Spreading)
        # Si on voit un allié, on s'en éloigne pour ne pas gâcher de temps sur les mêmes cases
        for i in range(len(sensors)):
            if sensor_view[i] == 2 and sensor_team[i] == self.team_name:
                if sensors[i] < 0.5: # Si un allié est proche
                    # Rotation inverse à la position de l'allié
                    return 0.8, (-1.0 if i < 4 else 1.0), False

        # PRIORITÉ 4: Navigation optimisée (Poids issus de l'Algo Génétique)
        # Ces poids favorisent la translation maximale (p0=1) et la fluidité (p6=-1, p7=-1)
        # p = [trans_bias, trans_L, trans_F, trans_R, rot_bias, rot_L, rot_F, rot_R]
        p = [1.0, -0.2, -0.5, -0.2, 0.0, 0.8, 0.0, -0.8]
        
        # Bruit de comportement pour éviter les trajectoires infinies (diversification)
        bias_id = (self.robot_id - 1.5) * 0.05
        
        translation = p[0] + p[1] * sensors[sensor_front_left] + p[2] * sensors[sensor_front] + p[3] * sensors[sensor_front_right] 
        rotation = p[4] + p[5] * sensors[sensor_front_left] + p[6] * sensors[sensor_front] + p[7] * sensors[sensor_front_right] 

        return translation, rotation, False