 #
 # ENAC Internship - Abstracting A-SMGCS Display
 # Malek Ben Ghachem (malek.08@hotmail.fr)
 # Representation of the Paris Roissy-CDG airport's south section in an oriented graph
 #

import math
from traffic import Traffic
class Aircraft:
    def __init__(self, id, start_nodee, route, end_nodee,t):
        self.id = id
        self.traffic = t
        self.start_node= self.traffic.get_node_by_id(start_nodee)
        if(not self.start_node):
            raise RuntimeError("An error occurred => Execution terminated")
        self.position = self.start_node['position']
        self.route = route
        self.current_route_index = 0
        self.current_node = self.start_node
        self.end_node = self.traffic.get_node_by_id(end_nodee)
        #Variable qui comptabilise le nombre de fois que l'avion va être déplacé sur la MÊME edge => sera remis à 0 à chaque changement d'edge
        self.i_motion_edge = 0
        #Seuil qui va définir le découpage en intervalles de passages de l'avion par edge
        self.threshold = 50
        #Définit le niveau de priorité : 1 => L'avion est prioritaire sur les autres et 0 l'avion doit attendre
        self.priority = 1
        self.past_speed = None

    def set_traffic(self, t):
        self.traffic = t

    def get_current_speed(self):
        return int(self.route[self.current_route_index]['speed'])
    def set_current_speed(self, s):
        self.route[self.current_route_index]['speed'] = str(s)

    # Status field (scheduled - departed - parked - towed - arrived)
    def set_status(self, s):
        new_status = s.upper()
        if new_status != "SCHEDULED" and new_status != "DEPARTED" and new_status != "PARKED" and new_status!= "TOWED" and new_status != "ARRIVED":
            raise RuntimeError("Wrong input of aircraft's status => ' ",new_status," '")
        else:
            self.status = new_status

    def move(self):
        if self.current_route_index < len(self.route):
            edgelocal = self.route[self.current_route_index]
            speed = self.get_current_speed()
            edgeglobal = self.traffic.get_link_by_id(edgelocal['id'],self.current_node['id'])
            if not edgeglobal:
                raise RuntimeError("The edge ",edgelocal['id']," source is not ",self.current_node['id'])

            source_node = self.traffic.get_node_by_id(edgeglobal['source'])
            target_node = self.traffic.get_node_by_id(edgeglobal['target'])
            self.position = self.calculate_new_position(self.current_node, target_node, self.position, speed)
            return self.position
        # Case of the aircraft's last move before joining the parking/runway
        elif self.current_route_index == len(self.route) and (self.current_node['id'].startswith("From") or self.current_node['id'].startswith("TO") or self.current_node['id'].startswith("LA")):
            self.position = self.end_node['position']
            self.current_route_index += 1
            self.i_motion_edge = 0
            if self.current_node['id'].startswith("From"):
                self.status = "PARKED"
            if self.current_node['id'].startswith("TO") or self.current_node['id'].startswith("LA"):
                self.status = "DEPARTED"

        # Case of the aircraft being moved manually (with inputs in the GUI)
        elif self.current_route_index == len(self.route) and self.status == "SCHEDULED":
            return self.position

        # Case of a plane that had his position changed and is yet to receive a new route
        elif self.status != "DEPARTED" and self.status != "PARKED" and self.position != None and len(self.route) == 0:
            return self.position
        else:
            self.position = None
            self.i_motion_edge = 0
            return None
        return None

    def update_i_motion_edge(self , i):
        return i * (self.past_speed / self.get_current_speed())

    def calculate_new_position(self, source_node, target_node, position, speed):
        # Calculate the new position based on the source & target node
        x_origin = source_node["position"]["x"]
        y_origin = source_node["position"]["y"]
        x_goal = target_node["position"]["x"]
        y_goal = target_node["position"]["y"]
        diffx = (x_goal - x_origin)/(self.threshold//speed)
        diffy = (y_goal - y_origin)/(self.threshold//speed)
        if speed != self.past_speed and self.past_speed != None:
            self.i_motion_edge = self.update_i_motion_edge(self.i_motion_edge)
        self.i_motion_edge += 1
        if(self.i_motion_edge >= (self.threshold//speed)):
            self.current_route_index += 1
            self.current_node = target_node
            self.position = self.current_node['position']
            self.i_motion_edge = 0
            return {'x':x_goal, 'y':y_goal}
        self.past_speed = speed
        return {'x':(x_origin + (self.i_motion_edge * diffx)), 'y':(y_origin + (self.i_motion_edge * diffy))}
