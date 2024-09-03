#
# ENAC Internship - Abstracting A-SMGCS Display
# Malek Ben Ghachem (malek.08@hotmail.fr)
# Representation of the Paris Roissy-CDG airport's south section in an oriented graph
#

# This module allows to load a traffic file
import math
class Traffic:
    def __init__(self):
        self.aircrafts = []

    def set_nodes(self, nodes):
        self.nodes = nodes

    def set_links(self, links):
        self.links = links

    def add_aircraft(self,plane):
        if(plane.start_node['id'] == "LA_RWY"):
            plane.set_status("ARRIVED")
        else:
            plane.set_status("SCHEDULED")
        self.aircrafts.append(plane)



    def remove_aircraft(self,plane_id):
        for p in self.aircrafts:
            if p.id == plane_id:
                self.aircrafts.remove(p)

    def get_aircraft(self,id):
        for plane in self.aircrafts:
            if plane.id == id:
                return plane
    #To retrieve a node by its id
    def get_node_by_id(self,node_id):
        #print("on rentre ?")
        for elem in self.nodes:
            #print(id," = ? ",elem["id"])
            if elem['id'] == node_id:
                return elem
        return None
    #To print every aircraft id for the aircrafts in self.aircrafts
    #For debugging purpose only
    def print_aircrafts(self):
        print("\n----- aircrafts -----")
        for air in self.aircrafts:
            print(air.id," en position ")
        print("\n----- end -----")

    def get_node_by_id(self,node_id):
        for elem in self.nodes:
            if elem['id'] == node_id:
                return elem
        return None

    #To retrieve a link by its id
    def get_link_by_id(self,link_id,current_node_id):
        #print(self.links)
        for elem in self.links:
            #print(id," = ? ",elem["id"])
            if elem['taxiway'] == link_id and elem['source'] == current_node_id:
                return elem
        return None

    def move_all_aircrafts(self):
        positions = {}
        for aircraft in self.aircrafts:
            movement = aircraft.move()
            positions[aircraft.id] = aircraft.position

        return positions

    # Reset every planes' priority
    def reset_priorities(self):
        for air in self.aircrafts:
            air.priority = 1



    # To calculate and adjust priorities at the right time
    def priorities_algo(self):
        conflicts = {}
        # It is important to reset before we recalculate, because if we are in a conflict free context, every plane should have equal priority
        self.reset_priorities()
        for air1 in self.aircrafts:
            for air2 in self.aircrafts[self.aircrafts.index(air1):]:
                if air1 != air2:
                    if(air1.current_route_index < len(air1.route)) and (air2.current_route_index < len(air2.route)):
                        edge1 = self.get_link_by_id(air1.route[air1.current_route_index]['id'],air1.current_node['id'])
                        edge2 = self.get_link_by_id(air2.route[air2.current_route_index]['id'],air2.current_node['id'])
                        if edge1['target'] == edge2['target']:
                            # If the conflictual node is already present in the dictionnary we append, otherwise we create
                            if edge1['target'] in conflicts:
                                if not (air1.id in conflicts[edge1['target']]):
                                    conflicts[edge1['target']].append(air1.id)
                                if not (air2.id in conflicts[edge1['target']]):
                                    conflicts[edge1['target']].append(air2.id)
                            else:
                                conflicts[edge1['target']] = [air1.id]
                                conflicts[edge1['target']].append(air2.id)

                            #We start investigating which aircraft has more priority, in this case, we first look at which aircraft is more advance on the edge.
                            #The most advanced aircraft will have priority over the others whose speed will be decreased (on the conflictual edge)
                            #If the more advanced plane have higher speed, we do not decrease otherwise we decrease to ensure safety
                            if air1.i_motion_edge * air1.get_current_speed() > air2.i_motion_edge * air2.get_current_speed():
                                air2.priority = 0
                                air1_speed = air1.get_current_speed()
                                air2_speed = air2.get_current_speed()

                                if air2_speed > air1_speed:
                                    air2.set_current_speed(str(air1_speed))
                                else:
                                    air1.set_current_speed(str(air1_speed + 1))

                            elif air2.i_motion_edge * air2.get_current_speed() > air1.i_motion_edge * air1.get_current_speed():
                                air1.priority = 0
                                air1_speed = air1.get_current_speed()
                                air2_speed = air2.get_current_speed()

                                if air1_speed > air2_speed:
                                    air1.set_current_speed(str(air2_speed))
                                else:
                                    air2.set_current_speed(str(air2_speed + 1))
                            else:
                                # Aircrafts that just landed have higher priority
                                if air1.status == "ARRIVED" and air2.status == "SCHEDULED":
                                    air2.priority = 0
                                    air1_speed = air1.get_current_speed()
                                    air2_speed = air2.get_current_speed()

                                    if air1_speed > 1:
                                        air2.set_current_speed(str(air1_speed - 1))
                                        air1.set_current_speed(str(air1_speed + 1))
                                    else:
                                        air2.set_current_speed(str(air1_speed))
                                        air1.set_current_speed(str(air1_speed + 1))

                                elif air1.status == "SCHEDULED" and air2.status == "ARRIVED":
                                    air1.priority = 0
                                    air1_speed = air1.get_current_speed()
                                    air2_speed = air2.get_current_speed()


                                    if air2_speed > 1:
                                        air1.set_current_speed(str(air2_speed - 1))
                                        air2.set_current_speed(str(air2_speed + 1))

                                    else:
                                        air1.set_current_speed(str(air2_speed))
                                        air2.set_current_speed(str(air2_speed + 1))
                                # In case they are both willing to do the same thing
                                elif air1.status == air2.status:
                                    # The aircraft which is going at higher speed has priority over the other
                                    if air1.route[air1.current_route_index]['speed'] > air2.route[air2.current_route_index]['speed']:
                                        air2.priority = 0
                                        air1_speed = air1.get_current_speed()
                                        air2_speed = air2.get_current_speed()

                                        if air1_speed > 1:
                                            air2.set_current_speed(str(air1_speed - 1))
                                            air1.set_current_speed(str(air1_speed + 1))
                                    elif air2.route[air2.current_route_index]['speed'] > air1.route[air1.current_route_index]['speed']:
                                        air1.priority = 0
                                        air1_speed = air1.get_current_speed()
                                        air2_speed = air2.get_current_speed()
                                        if air2_speed > 1:
                                            air1.set_current_speed(str(air2_speed - 1))
                                            air2.set_current_speed(str(air2_speed + 1))
                                    else:
                                    # The pilot whose aircraft is the closest to it's route' objective has more priority
                                        if air1.current_route_index > air2.current_route_index:
                                            air2.priority = 0
                                            air1_speed = air1.get_current_speed()
                                            air2_speed = air2.get_current_speed()

                                            if air2_speed > 1:
                                                air2.set_current_speed(str(air2_speed - 1))
                                            else:
                                                air1.set_current_speed(str(air1_speed + 1))
                                        elif air2.current_route_index>air1.current_route_index:
                                            air1.priority = 0
                                            air1_speed = air1.get_current_speed()
                                            air2_speed = air2.get_current_speed()

                                            if air1_speed > 1:
                                                air1.set_current_speed(str(air1_speed - 1))

                                            else:
                                                air2.set_current_speed(str(air2_speed + 1))
                                        # If both are more or less at the same stage...
                                        else:
                                            # We prioritize the aircraft that had the longest route
                                            if len(air1.route)>len(air2.route):
                                                air2.priority = 0
                                                air1_speed = air1.get_current_speed()
                                                air2_speed = air2.get_current_speed()

                                                if air2_speed > 1:
                                                    air2.set_current_speed(str(air2_speed - 1))
                                                else:
                                                    air1.set_current_speed(str(air1_speed + 1))
                                            elif len(air2.route)>len(air1.route):
                                                air1.priority = 0
                                                air1_speed = air1.get_current_speed()
                                                air2_speed = air2.get_current_speed()

                                                if air1_speed > 1:
                                                    air1.set_current_speed(str(air1_speed - 1))

                                                else:
                                                    air2.set_current_speed(str(air2_speed + 1))
                                            elif edge1['source'].startswith("From"):
                                                air2.priority = 0
                                                air1_speed = air1.get_current_speed()
                                                air2_speed = air2.get_current_speed()

                                                if air2_speed > 1:
                                                    air2.set_current_speed(str(air2_speed - 1))
                                                else:
                                                    air1.set_current_speed(str(air1_speed + 1))
                                            else:
                                                air1.priority = 0
                                                air1_speed = air1.get_current_speed()
                                                air2_speed = air2.get_current_speed()

                                                if air1_speed > 1:
                                                    air1.set_current_speed(str(air1_speed - 1))
                                                else:
                                                    air2.set_current_speed(str(air2_speed + 1))
                                else:
                                    raise RuntimeError("The plane ",air1.id," and the plane ",air2.id, " priorities calculation couldn't be done")

        return conflicts
