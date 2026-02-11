# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : David Loth 21305884
#  Prénom Nom No_étudiant/e : _________
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import * 
import math

nb_robots = 0

def get_bit(memory, bit_index):
    return (memory >> bit_index) & 1

def set_bit(memory, bit_index):
    return memory | (1 << bit_index)

def clear_bit(memory, bit_index):
    return memory & ~(1 << bit_index)

def get_value(memory, start, size):
    value=0
    for i in range(size):
        value+=get_bit(memory,i+start)*2**i

    return value

def set_value(memory,start,size,new_value):
    for i in range(size):
        if new_value & 1==0:
            memory=clear_bit(memory, start+i)
        else:
            memory=set_bit(memory,start+i)
        new_value=new_value>>1
    
    return memory

def surface_max(sensors,id,memory):
    forward=min(sensors)+0.5

    if sensors[sensor_front]<1 or sensors[sensor_front_right]<0.3 or sensors[sensor_front_left]<0.3:
        if sensors[sensor_left] < sensors[sensor_right] and memory<=0:
            return forward,-1
        if sensors[sensor_left] > sensors[sensor_right] and memory>=0:
            return forward,1
        if sensors[sensor_front_left] < sensors[sensor_front_right] and memory<=0:
            return forward,-1
        if sensors[sensor_front_left] > sensors[sensor_front_right] and memory>=0:
            return forward,1
        if memory==0:
            return forward,1
        return forward,memory/abs(memory)

    if sensors[sensor_right]<0.3 or sensors[sensor_rear_right]<0.3:
        return forward,1
    elif sensors[sensor_left]<0.3 or sensors[sensor_rear_left]<0.3:
        return forward,-1
    return 1,(random.random()-0.5)/2

def navigation(sensors,memory,sens,peux_tourner):
    veux_tourner=False
    if sens==-1:
        front=sensor_rear
        right=sensor_left
        left=sensor_right
    else:
        front=sensor_front
        right=sensor_right
        left=sensor_left

    if memory!=0:
        return 0,memory,sens,False
    
    dé=random.randint(1,3)
    
    if sensors[right]==1 and sensors[left]==1:
        if peux_tourner and dé==1:
            return 0,random.choice([-1,1]), sens,False
        else:
            veux_tourner=1
    if sensors[right]==1:
        if peux_tourner and dé==1:
            return 0,-1, sens,False
        else:
            veux_tourner=1
    if sensors[left]==1:
        if peux_tourner and dé==1:
            return 0,1, sens,False
        else:
            veux_tourner=1
    

    if sensors[front]<0.15:
        if sensors[right]==sensors[left]==1:
            return 0,random.choice([-1,1]),sens,False
        if sensors[right]==1:
            return 0,(-1),sens,False
        elif sensors[left]==1:
            return 0,1,sens,False
        else:
            return -sens,0,-sens,False
    
    return sens,0,sens,veux_tourner



        

class Robot_player(Robot):

    team_name = "Challenger"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1          # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 2                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):

        if self.id<3:
        
            iteration=get_value(self.memory,20,11)
            self.memory+=2**20

            frame_avg=0
            for d in sensors:
                frame_avg+=(d/8)*100
            avg=get_value(self.memory,13,7)
            avg=round((avg*iteration+frame_avg)/(iteration+1))
            self.memory=set_value(self.memory,13,7,avg)
            if avg>67:
                signe=get_value(self.memory,3,2)-1 #signe= 1 si la dernière rotation était vers la gauche, -1 si elle était vers la droite et 0 sinon

                translation, rotation=surface_max(sensors,self.robot_id,signe)
                if rotation==-1:
                    self.memory=set_value(self.memory,3,2,0)
                    self.memory+=1
                elif rotation==1:
                    self.memory=set_value(self.memory,3,2,2)
                    self.memory+=1
                else:
                    self.memory=set_value(self.memory,0,5,8)
                
                if get_value(self.memory,0,3)>=5:
                    self.memory=set_value(self.memory,0,5,8)

            else:
                sens_translation=get_bit(self.memory,0)*2-1 #-1 si on recule, 1 sinon
                sens_rotation=get_value(self.memory,1,2)-1 #-1 si on tourne à droite, 1 si on tourne à gauche, 0 sinon
                peux_tourner=get_value(self.memory,3,2)
                veux_tourner=get_bit(self.memory,5)
                memory=get_value(self.memory,6,4)
                cooldown=get_value(self.memory,10,3)

                if not veux_tourner or peux_tourner==0:
                    peux_tourner=2

                if veux_tourner and cooldown==0:
                    peux_tourner-=1

                if cooldown>0:
                    cooldown-=1

                translation,rotation,sens_translation,veux_tourner = navigation(sensors,sens_rotation,sens_translation,(peux_tourner==0))

                if rotation==-1:
                    sens_rotation=-1
                    memory+=1
                elif rotation==1:
                    sens_rotation=1
                    memory+=1
                else:
                    memory=0
                    sens_rotation=0
                    
                if memory>=9:
                    cooldown=5
                    memory=0
                    sens_rotation=0


                self.memory=set_value(self.memory,0,1,(sens_translation+1)//2)
                self.memory=set_value(self.memory,1,2,sens_rotation+1)
                self.memory=set_value(self.memory,3,2,peux_tourner)
                self.memory=set_value(self.memory,5,1,veux_tourner)
                self.memory=set_value(self.memory,6,4,memory)
                self.memory=set_value(self.memory,10,3,cooldown)

        if self.id>=3:
        
            param= [0.36445977578638095, 2.235062106014654, 0.8838141736875778, 0.634270626015909, 1.0932829189099793, 1.1589474706401748, -0.8245446312650989, -0.9650554790363312, -1.8428574770985524]
            translation = math.tanh ( 0 + param[1] * sensors[sensor_front_left] + param[2] * sensors[sensor_front] + param[3] * sensors[sensor_front_right] )
            rotation = math.tanh ( param[4]*sensors[sensor_left] + param[5] * sensors[sensor_front_left] + param[6] * sensors[sensor_right] + param[7] * sensors[sensor_front_right] + param[8]* (random.random()-0.5) )

        return translation, rotation, False

