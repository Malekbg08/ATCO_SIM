 #
 # ENAC Internship - Abstracting A-SMGCS Display
 # Malek Ben Ghachem (malek.08@hotmail.fr)
 # Representation of the Paris Roissy-CDG airport's south section in an oriented graph
 #

import json
import random
SEUIL_MIN = -10000
SEUIL_MAX = +10000
class GraphModel:
    def __init__(self):
          self.nodes=[]
          self.links=[]

    # This function iterates over the list of nodes in self.nodes and converts the value of the 'defrosting' key to a lowercase string for each node (to avoid complications in the js code). It then returns the list of nodes
    def get_nodes(self):
        for elem in self.nodes:
            elem['defrosting']=str(elem["defrosting"]).lower()
        return self.nodes

    #To retrieve a node by its id
    def get_node_by_id(self,id):
        for elem in self.nodes:
            if elem['id'] == id:
                return elem
        return None

    #To retrieve a link by its id
    def get_link_by_id(self,id):
        for elem in self.links:
            if elem['id'] == id:
                return elem
        return None

    # This function simply returns the list of links stored in self.links without making any modifications
    def get_links(self):
        return self.links

    # This function converts a JSON to a dictionary while separating nodes and links respectively into self.nodes and self.links. It iterates over the JSON, identifying nodes by their content and constructs separate dictionaries for nodes and links, and assigns these lists to self.nodes and self.links.
    def json_to_dict(self,json_data):
        data_dict = json.loads(json_data)
        nested_dict = {}
        nodes = []
        links = []
        for key, value in data_dict.items():
            if isinstance(value, dict) and 'taxiway' in value and 'type' in value:
                links.append({"taxiway":value.get('taxiway'),"type":value.get('type'),"longueur":value.get('longueur'),"source":value.get('source'),"target":value.get('target')})
                current_dict = nested_dict.setdefault(value['taxiway'], {}).setdefault(value['type'], {})
                current_dict['longueur'] = value.get('longueur')
                current_dict['source'] = value.get('source')
                current_dict['target'] = value.get('target')
            elif isinstance(value, dict) and 'id' in value and 'liste_twy' in value:
                if 'position' in value:
                    nodes.append({"id":value.get('id'),"liste_twy":value.get('liste_twy'),"diameter":value.get('diameter'),"defrosting":value.get('defrosting'),"position":value.get('position')})
                else:
                    nodes.append({"id":value.get('id'),"liste_twy":value.get('liste_twy'),"diameter":value.get('diameter'),"defrosting":value.get('defrosting'),"position":{'x': random.uniform(SEUIL_MIN, SEUIL_MAX), 'y': random.uniform(SEUIL_MIN,SEUIL_MAX)}})
                current_dict = nested_dict.setdefault(value['id'], {})
                current_dict['liste_twy'] = value.get('liste_twy')
                current_dict['diameter'] = value.get('diameter')
                current_dict['defrosting'] = value.get('defrosting')
                #Following statement risky, it might create the 'position' field and affect it None value
                if 'position' in current_dict:
                    current_dict['position'] = value.get('position')
                else:
                    current_dict['position'] = {'x': 0.0, 'y': 0.0}

            else:
                #Traitement pour autre type de données
                pass
        self.nodes=nodes
        self.links=links
        return nested_dict


    def json_to_dict_aircraft(self,json_data):
        data_dict = json.loads(json_data)
        nested_dict = {}
        aircraft = []
        links = []
        for key, value in data_dict.items():
                current_dict = nested_dict.setdefault(value['aircraft_id'], {})
                current_dict['starting_node'] = value.get('starting_node')
                current_dict['route'] = value.get('route')
                current_dict['end_node'] = value.get('end_node')

        return nested_dict

    # This function converts the current state of self.nodes and self.links back into a JSON string. It creates dictionaries for nodes and links, then combines them into a single dictionary. It serializes this combined dictionary into a JSON
    def dict_to_json(self):
        nodes_dict = {}
        i_node=0
        for i, node in enumerate(self.nodes):
            nodes_dict[str(i)] = node
            i_node=i
        i_node+=1
        links_dict = {}
        for i, link in enumerate(self.links):
            links_dict[str(i+i_node)] = link
        #To combine two dicts
        combined_dict = {**nodes_dict, **links_dict}
        json_data = json.dumps(combined_dict, indent=4)
        return json_data
