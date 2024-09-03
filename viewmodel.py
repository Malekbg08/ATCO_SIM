 #
 # ENAC Internship - Abstracting A-SMGCS Display
 # Malek Ben Ghachem (malek.08@hotmail.fr)
 # Representation of the Paris Roissy-CDG airport's south section in an oriented graph
 #

from model import GraphModel
from traffic import Traffic
from aircraft import Aircraft
from typing import Dict, List
import json

class GraphViewModel:
    def __init__(self):
        self.filepathinmemory = None
        self.model = GraphModel()
        self.nodes = self.model.get_nodes()
        self.links = self.model.get_links()
        self.traffic = Traffic()

    # Returns the list of nodes
    def get_nodes(self):
        return self.nodes

    # Returns the list of edges
    def get_links(self):
        return self.links

    # By calling this function, we force the json file to contain position coordinates set to 0 for every node in case the json doesn't already have any spatial information
    def initialize_node_positions(self):
            for node in self.nodes:
                if 'position' not in node:
                    node['position'] = {'x': 0.0, 'y': 0.0}

    # This functions enables saving the graph state in the json file that was initally used to load the graph. We save the state of the graph by saving the coordinates of every node as of the last dragging event
    def save_graph_state_to_json(self, file_name):
        jsondata = self.model.dict_to_json()
        f = open(file_name, "w")
        f.write(jsondata)
        print("Saved!!!")
        f.close()

        return jsondata

    # It updates the position of each nodes according to their latest affectation by the user
    def update_node_position(self, node_id: str, position: Dict[str, float]):
        for node in self.nodes:
            if node['id'] == node_id:
                node['position'] = position
                break

    # It imports the json data from a file path, access it and store it's content in a dictionary by calling the json_to_dict function
    def import_json_data(self, file_path):
        with open(file_path, 'r') as file:
            self.filepathinmemory = file_path
            json_data = file.read()

        nested_dict = self.model.json_to_dict(json_data)
        self.nodes = self.model.get_nodes()
        self.links = self.model.get_links()
        self.initialize_node_positions()
        self.traffic.set_nodes(self.nodes)
        self.traffic.set_links(self.links)

    def import_json_data_aircraft(self, file_path):
        with open(file_path, 'r') as file:
            json_data = file.read()

        nested_dict = self.model.json_to_dict_aircraft(json_data)
        return nested_dict

    #Function to create and give a specific name to the file that is related to the import file but that will contain the updated information
    def rewrite_file_name(self, file_path, string):
        for i in range(len(file_path)):
            if file_path[i:] == ".json":
                return file_path[:i] + "_" + string + file_path[i:]
    def add_aircraft(self, aircraft_id, start_position, route, end_position):
            aircraft = Aircraft(aircraft_id, start_position, route, end_position,self.traffic)
            if start_position.startswith("LA"):
                aircraft.set_status("ARRIVED")
            else:
                aircraft.set_status("SCHEDULED")
            self.traffic.add_aircraft(aircraft)

    def add_new_aircraft(self, aircraft_id, start_position, route, end_position):
        list_route = []
        for i in range(len(route)-1):
            if i%2==0:
                list_route.append({"id":route[i], "speed": route[i+1]})
        aircraft = Aircraft(aircraft_id, start_position, list_route, end_position,self.traffic)
        if start_position.startswith("LA"):
            aircraft.set_status("ARRIVED")
        else:
            aircraft.set_status("SCHEDULED")
        self.traffic.add_aircraft(aircraft)

    def move_aircraft(self, aircraft_id):
        aircraft = self.traffic.get_aircraft(aircraft_id)
        if aircraft:
            return aircraft.move()
        return None

    def move_all_aircrafts(self):
        return self.traffic.move_all_aircrafts()

    # To update an existing scenario with new data or to save a newly created scenario
    def save_scenario_to_json(self, file_path):
        i=0
        scenario_data = {
            str(self.traffic.aircrafts.index(aircraft)):
                {
                    'aircraft_id': aircraft.id,
                    'starting_node': aircraft.start_node['id'],
                    'route': aircraft.route,
                    'end_node': aircraft.end_node['id']
                }
                for aircraft in self.traffic.aircrafts

        }
        with open(file_path, 'w') as f:
            json.dump(scenario_data, f, indent=4)
            print("Scenario saved!!!")

        return json.dumps(scenario_data, indent=4)
