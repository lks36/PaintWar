# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : clément Jiang 21223581
#  Prénom Nom No_étudiant/e : rohith RAMASSAMY 21202334
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import * 

nb_robots = 0

class Robot_player(Robot):

    team_name = "Les_vainqueurs!!!!!"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):

        self.memory += 1
        sensor_to_wall = []
        sensor_to_robot = []
        for i in range (0,8):
            if  sensor_view[i] == 1:
                sensor_to_wall.append( sensors[i] )
                sensor_to_robot.append(1.0)
            elif  sensor_view[i] == 2:
                sensor_to_wall.append( 1.0 )
                sensor_to_robot.append( sensors[i] )
            else:
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(1.0)
        

        if(sensor_to_wall[sensor_front]<0.15 or sensor_to_wall[sensor_front_left]<0.15 or sensor_to_wall[sensor_front_right]<0.15 or sensor_to_wall[sensor_right]<0.15 or sensor_to_wall[sensor_left]<0.15 or sensor_to_wall[sensor_rear]<0.15 or sensor_to_wall[sensor_rear_left]<0.15 or sensor_to_wall[sensor_rear_right]<0.15):

            translation = sensor_to_wall[sensor_front] * 0.2
            rotation = ((sensor_to_wall[sensor_front_left] + sensor_to_wall[sensor_left]) - (sensor_to_wall[sensor_front_right] + sensor_to_wall[sensor_right])) + (random.random()-0.5)

            if self.memory > 20:
                translation = 0
                rotation = random.randint(-1,1)
                self.memory = 0


        elif(sensor_to_robot[sensor_front]<0.5 or sensor_to_robot[sensor_front_left]<0.5 or sensor_to_robot[sensor_front_right]<0.5 or sensor_to_robot[sensor_right]<0.5 or sensor_to_robot[sensor_left]<0.5 or sensor_to_robot[sensor_rear]<0.5 or sensor_to_robot[sensor_rear_left]<0.5 or sensor_to_robot[sensor_rear_right]<0.5):
            

            translation = sensor_to_robot[sensor_front]*0.5
            rotation = (sensor_to_robot[sensor_left] + sensor_to_robot[sensor_front_left]) - (sensor_to_robot[sensor_right] + sensor_to_robot[sensor_front_right]) + (random.random()-0.5)
            
            if self.memory > 20:
                translation = 0
                rotation = random.randint(-1,1)
                self.memory = 0


        else:
            param = [1, 0.9948070854197746, 1, 0.9537018668899915, 1, -0.9363665062334459, -0.7649887986452448, 0.5241383698298889]
            translation = param[0] + param[1] * sensors[sensor_front_left] + param[2] * sensors[sensor_front] + param[3] * sensors[sensor_front_right] 
            rotation = param[4] + param[5] * sensors[sensor_front_left] + param[6] * sensors[sensor_front] + param[7] * sensors[sensor_front_right]

            if self.memory > 30:
                translation = 0
                rotation = random.choice([-1,1])
                self.memory = 0


        return translation, rotation, False