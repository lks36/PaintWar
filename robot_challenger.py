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

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # On utilise memory comme un compteur cyclique de 0 à 100
        self.memory = (self.memory + 1) % 100

        # Normalisation des capteurs (0.0 = Mur touche, 1.0 = Vide infini)
        # Note: selon ton robot.py, vérifie si l'ordre est bien [Front, FrontLeft, ...]
        # Ici on suppose l'ordre standard : 0=Front, 1=FrontLeft, 2=Left... 
        # Si ton robot n'a que 3 senseurs, adapte les index si besoin.
        s_front = sensors[sensor_front]
        s_left  = sensors[sensor_front_left]
        s_right = sensors[sensor_front_right]

        # --- 1. SECURITÉ & BLOCAGE (Priorité Absolue) ---
        
        # Si on est COLLÉ au mur (< 0.15) ou à un robot, on recule violemment.
        # C'est vital pour les culs-de-sac de l'Arena 7.
        if s_front < 0.15:
            # On recule en tournant (pour ne pas refaire la même erreur)
            # L'ID définit le sens de rotation pour éviter que toute l'équipe fasse pareil
            rot_dir = 1.0 if self.robot_id % 2 == 0 else -1.0
            return -1.0, rot_dir, False

        # --- 2. EVITEMENT D'EQUIPE (Dispersion) ---
        
        # Si je vois un pote devant, je fais demi-tour IMMÉDIAT.
        # sensor_view[sensor_front] == 2 signifie "Je vois un robot"
        if sensor_view[sensor_front] == 2 and sensor_team[sensor_front] == self.team_name:
            return -0.5, 1.0, False # Demi-tour

        # --- 3. NAVIGATION INTELLIGENTE ---

        translation = 1.0 # Par défaut: Vitesse Max
        rotation = 0.0

        # CAS A : COULOIR OU MUR (Pacman / Labyrinthe)
        # Si les murs latéraux sont proches, on active le "Centrage"
        if s_left < 0.8 or s_right < 0.8:
            # Formule magique : (Gauche - Droite)
            # Si Gauche < Droite (mur à gauche), le résultat est négatif -> On tourne à Droite.
            # Le facteur 1.5 assure la réactivité sans osciller trop fort.
            rotation = (s_left - s_right) * 1.5
            
            # Si un mur arrive devant, on tourne plus fort
            if s_front < 0.6:
                translation = 0.6 # On ralentit un peu
                # On accentue la rotation vers la sortie
                if s_left > s_right: 
                    rotation = 1.0 # Gauche est libre
                else: 
                    rotation = -1.0 # Droite est libre

        # CAS B : ESPACE VIDE (Arena 0 / Arena 1)
        # Si on est en plein milieu de rien (tout > 0.8), on ne va pas tout droit !
        # Une ligne droite est inefficace. On fait une SINUSOÏDE (zigzag).
        else:
            # Utilisation de memory pour créer une onde
            # Le robot ondule pour peindre une bande large au lieu d'une ligne fine
            if self.memory < 50:
                rotation = 0.3 # Virage léger gauche
            else:
                rotation = -0.3 # Virage léger droite
                
            # Petit boost de dispersion au début basé sur l'ID
            if self.robot_id == 0: rotation += 0.1
            if self.robot_id == 1: rotation -= 0.1

        # --- 4. OPTIMISATION DE LA VITESSE ---
        
        # Si le chemin devant est dégagé, on force 1.0
        # Sinon, la vitesse est proportionnelle à la distance du mur
        if s_front > 0.5:
            translation = 1.0
        else:
            # On ne descend jamais en dessous de 0.2 pour ne pas caler
            translation = max(0.2, s_front)

        return translation, rotation, False