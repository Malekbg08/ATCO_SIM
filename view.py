 #
 # ENAC Internship - Abstracting A-SMGCS Display
 # Malek Ben Ghachem (malek.08@hotmail.fr)
 # Representation of the Paris Roissy-CDG airport's south section in an oriented graph
 #

import sys
from PySide6.QtWidgets import *
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import *
from viewmodel import GraphViewModel
import json, time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abstract Control V4")
        self.setGeometry(1000, 2000, 2000, 2000)
        self.setup_ui()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)  # Main layout for the entire window

        self.view_model = GraphViewModel()

        # Left panel for webview
        self.webview = QWebEngineView()
        webview_layout = QVBoxLayout()
        webview_layout.addWidget(self.webview)
        webview_widget = QWidget()
        webview_widget.setLayout(webview_layout)
        main_layout.addWidget(webview_widget, 4)  # Takes 80% of the width

        # Right panel for controls
        self.control_panel = QWidget()
        self.control_panel.setFixedWidth(380)
        control_layout = QVBoxLayout(self.control_panel)
        main_layout.addWidget(self.control_panel, 1)  # Takes 20% of the width

        # Buttons for file operations
        file_buttons_layout = QHBoxLayout()
        import_button = QPushButton("Import")
        import_button.clicked.connect(self.import_json_button_clicked)
        file_buttons_layout.addWidget(import_button)

        save_button = QPushButton("Save Graph")
        save_button.clicked.connect(self.save_graph_state)
        file_buttons_layout.addWidget(save_button)

        save_scenario_button = QPushButton("Save Scenario")
        save_scenario_button.clicked.connect(self.save_scenario_state)
        file_buttons_layout.addWidget(save_scenario_button)

        play_button = QPushButton("Play")
        play_button.clicked.connect(self.start_motion)
        file_buttons_layout.addWidget(play_button)

        control_layout.addLayout(file_buttons_layout)

        self.add_controls(control_layout)

        self.channel = QWebChannel()
        self.webview.page().setWebChannel(self.channel)
        self.channel.registerObject("mainWindow", self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_aircraft_positions)


    def add_controls(self, control_layout):
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)  # Align labels to the left

        # Input for creating aircraft
        self.aircraft_id_input = QLineEdit(self)
        self.aircraft_id_input.setMinimumWidth(50)
        form_layout.addRow(QLabel("Aircraft ID: "), self.aircraft_id_input)
        self.start_node_input = QLineEdit(self)
        self.start_node_input.setMinimumWidth(50)
        form_layout.addRow(QLabel("Start Node ID:"), self.start_node_input)
        self.route_input = QLineEdit(self)
        self.route_input.setMinimumWidth(220)
        form_layout.addRow(QLabel("Route:"), self.route_input)
        self.end_node_input = QLineEdit(self)
        self.end_node_input.setMinimumWidth(50)
        form_layout.addRow(QLabel("End Node ID:"), self.end_node_input)

        create_aircraft_button = QPushButton("Create Aircraft", self)
        create_aircraft_button.clicked.connect(self.create_aircraft)
        form_layout.addRow(create_aircraft_button)

        # Input for setting aircraft position
        self.position_aircraft_id_input = QLineEdit(self)
        self.position_aircraft_id_input.setMinimumWidth(50)
        form_layout.addRow(QLabel("Aircraft ID for Position:"), self.position_aircraft_id_input)
        self.position_node_input = QLineEdit(self)
        self.position_node_input.setMinimumWidth(50)
        form_layout.addRow(QLabel("Node:"), self.position_node_input)

        set_position_button = QPushButton("Set Position", self)
        set_position_button.clicked.connect(self.set_position)
        form_layout.addRow(set_position_button)

        # Input for modifying aircraft route
        self.modify_aircraft_id_input = QLineEdit(self)
        self.modify_aircraft_id_input.setMinimumWidth(50)
        form_layout.addRow(QLabel("Aircraft ID to Modify:"), self.modify_aircraft_id_input)
        self.new_route_input = QLineEdit(self)
        self.new_route_input.setMinimumWidth(220)
        form_layout.addRow(QLabel("New Route:"), self.new_route_input)

        modify_route_button = QPushButton("Modify Route", self)
        modify_route_button.clicked.connect(self.modify_route)
        form_layout.addRow(modify_route_button)

        control_layout.addLayout(form_layout)


    # Manually create an aircraft by providing its name,route,start and end node
    # Please note that the route must follow the [edge(1),edge(1)_speed, edge(2),edge(2)_speed, ... , edge(n),edge(n)_speed] format !
    # Example : create_aircraft_manual(AF780, LA_RWY, [V1,4,S2,5], TO_RWY)
    def create_aircraft_manual(self, aircraft_id, start_node, route, end_node):
        existing = False
        for aircraft in self.view_model.traffic.aircrafts:
            if aircraft.id == aircraft_id:
                print(f"There is already an Aircraft {aircraft_id}")
                existing = True

        if not existing and aircraft_id and start_node and route and end_node:
            self.view_model.add_new_aircraft(aircraft_id,start_node,route,end_node)
            print(f"Aircraft {aircraft_id} created")

    # Create an aircraft using GUI inputs
    def create_aircraft(self):
        existing = False
        # Get aircraft ID from the input field
        aircraft_id = self.aircraft_id_input.text()
        # Get start node from the input field
        start_node = self.start_node_input.text()
        # Get route and split it into a list
        route = self.route_input.text().split(',')
        # Get end node from the input field
        end_node = self.end_node_input.text()
        # Check if the aircraft already exists
        for aircraft in self.view_model.traffic.aircrafts:
            if aircraft.id == aircraft_id:
                print(f"There is already an Aircraft {aircraft_id}")
                existing = True
        # If the aircraft does not exist and all fields are filled
        if not existing and aircraft_id and start_node and route and end_node:
            self.view_model.add_new_aircraft(aircraft_id,start_node,route,end_node)
            print(f"Aircraft {aircraft_id} created")

    # Set the position of an aircraft using GUI inputs
    def set_position(self):
        aircraft_id = self.position_aircraft_id_input.text()
        id_node = self.position_node_input.text()
        node = self.view_model.traffic.get_node_by_id(id_node)
        aircraft = self.view_model.traffic.get_aircraft(aircraft_id)
        if aircraft and node:
            # Set current node
            aircraft.current_node = node
            # Set start node
            aircraft.start_node = node
            # Clear route
            aircraft.route = []
            # Update position
            aircraft.position = aircraft.current_node['position']
            # For colours purpose ...
            if id_node.startswith("LA"):
                aircraft.set_status("ARRIVED")
            else:
                aircraft.set_status("SCHEDULED")
            print(f"Aircraft {aircraft_id} position set to {aircraft.position}")

    # Set the position of an aircraft manually
    def set_position_manual(self, aircraft_id, id_node):
        # Get node object by ID
        node = self.view_model.traffic.get_node_by_id(id_node)
        # Get aircraft object by ID
        aircraft = self.view_model.traffic.get_aircraft(aircraft_id)
        if aircraft and node:
            aircraft.current_node = node
            aircraft.start_node = node
            aircraft.route = []
            aircraft.position = aircraft.current_node['position']
             # Set status to ARRIVED if node starts with "LA"
            if id_node.startswith("LA"):
                aircraft.set_status("ARRIVED")
            else:
                aircraft.set_status("SCHEDULED")
            print(f"Aircraft {aircraft_id} position set to {aircraft.position}, with status {aircraft.status}")
        else:
            raise RuntimeError("An error occurred => Either the specified aircraft_id or the node_id were not found in the database, please make sure you enter valid ids")

    # Modify the route of an aircraft manually
    def modify_route_manual(self,aircraft_id,route):
        # List that will contain several dicts
        list_route = []
        # The route must be an even length list of (edge, speed) pairs
        if((len(route)%2) == 0):
            for i in range(len(route)-1):
                if i%2==0:
                    # Add dict to list
                    list_route.append({"id":route[i], "speed": route[i+1]})
            aircraft = self.view_model.traffic.get_aircraft(aircraft_id)
            if aircraft and list_route:
                current_edge = self.view_model.traffic.get_link_by_id(list_route[0]['id'],aircraft.current_node['id'])
                if(not current_edge):
                    print("Erreur")
                    raise RuntimeError("Incompatibilité noeud courant - route")
                # Set new route
                aircraft.route = list_route
                # Reset route index
                aircraft.current_route_index = 0
                # Reset motion edge index
                aircraft.i_motion_edge = 0
                print(f"Aircraft {aircraft_id} route modified")

    # Modify the route of an aircraft using GUI inputs
    def modify_route(self):
        aircraft_id = self.modify_aircraft_id_input.text()
        new_route = self.new_route_input.text().split(',')
        list_route = []
        #Il faut avoir une liste de chemins de longueur paire car il s'agit de couples (edge,speed)
        if((len(new_route)%2) == 0):
            for i in range(len(new_route)-1):
                if i%2==0:
                    list_route.append({"id":new_route[i], "speed": new_route[i+1]})
            aircraft = self.view_model.traffic.get_aircraft(aircraft_id)
            if aircraft and list_route:
                current_edge = self.view_model.traffic.get_link_by_id(list_route[0]['id'],aircraft.current_node['id'])
                if(not current_edge):
                    print("Erreur")
                    raise RuntimeError("Incompatibilité noeud courant - route")
                aircraft.route = list_route
                aircraft.current_route_index = 0
                aircraft.i_motion_edge = 0
                aircraft.set_status("SCHEDULED")
                print(f"Aircraft {aircraft_id} route modified")

    def load_d3_graph(self):
        nodes = json.dumps(self.view_model.get_nodes())
        links = json.dumps(self.view_model.get_links())
        html_content = f"""
        <html>
        <head>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        </head>
        <body>
            <svg width="4000" height="4000"></svg>
            <script>
                var nodes = {nodes};
                var links = {links};

                nodes.forEach(node => {{
                    node.fx = node.position.x;
                    node.fy = node.position.y;
                }});

                function preprocessLinks(links) {{
                    var linkMap = {{}};
                    links.forEach(link => {{
                        var key = link.source + "-" + link.target;
                        if (!linkMap[key]) {{
                            linkMap[key] = {{ ...link, taxiway: [link.taxiway] }};
                        }} else {{
                            linkMap[key].taxiway.push(link.taxiway);
                        }}
                    }});
                    return Object.values(linkMap).map(link => {{
                        link.taxiway = link.taxiway.join("; ");
                        return link;
                    }});
                }}

                var processedLinks = preprocessLinks(links);

                var svg = d3.select("svg"),
                    width = +svg.attr("width"),
                    height = +svg.attr("height");

                var g = svg.append("g");

                // Draw links
                var link = g.append("g")
                    .attr("stroke", "#999")
                    .attr("stroke-opacity", 0.6)
                    .selectAll("line")
                    .data(processedLinks)
                    .join("line")
                    .attr("stroke-width", 2);

                // Draw nodes
                var node = g.append("g")
                    .attr("stroke", "#fff")
                    .attr("stroke-width", 1.5)
                    .selectAll("circle")
                    .data(nodes)
                    .join("circle")
                    .attr("r", 12)
                    .attr("fill", color)
                    .call(drag());

                // Draw labels for nodes
                var label = g.append("g")
                    .attr("class", "label")
                    .selectAll("text")
                    .data(nodes)
                    .join("text")
                    .attr("text-anchor", "middle")
                    .attr("dy", -10)
                    .attr("font-size", "10px")
                    .attr("fill", "black")
                    .text(d => d.id);

                // Draw labels for links
                var labels = g.append("g")
                    .attr("class", "labels")
                    .selectAll("text")
                    .data(processedLinks)
                    .enter().append("text")
                    .attr("text-anchor", "middle")
                    .attr("font-size", "10px")
                    .attr("fill", "black")
                    .text(d => d.taxiway);

                node.append("title")
                    .text(d => d.id);

                // Function to move the aircraft along the route
                function moveAircraft(aircraftId, position,priority,status) {{
                    var aircraft = svg.select("#" + aircraftId);
                    if (aircraft.empty()) {{
                        aircraft = g.append("circle")
                            .attr("id", aircraftId)
                            .attr("r", 8)
                            .attr("fill", "purple");
                    }}

                    if(priority == 0){{
                        aircraft.attr("fill", "yellow");
                    }}
                    else{{
                        if (status == "ARRIVED"){{
                            aircraft.attr("fill", "orange");
                        }}
                        else if (status == "SCHEDULED"){{
                            aircraft.attr("fill", "purple");
                        }}
                    }}


                    aircraft
                        .attr("cx", position.x)
                        .attr("cy", position.y);
                }}

                function deleteAircraft(aircraftId) {{
                    var aircraft = svg.select("#" + aircraftId);
                    aircraft.remove()
                }}

                function updateAircraftPositions() {{
                    if (window.mainWindow) {{
                        window.mainWindow.getAircraftPositions(function(positions) {{
                            positions = JSON.parse(positions);
                            for (var id in positions) {{
                                moveAircraft(id, positions[id]);
                            }}
                        }});
                    }}
                }}

                function updateAircraftPositions() {{
                    if (window.mainWindow) {{
                        window.mainWindow.getAircraftPositions(function(positions) {{
                            positions = JSON.parse(positions);
                            for (var id in positions) {{
                                moveAircraft(id, positions[id]);
                            }}
                        }});
                    }}
                }}
                // Checks the node's type and colors the node accordingly
                function color(d) {{
                    if (d.id === "TO_RWY" || d.id === "LA_RWY") {{
                        return "red";
                    }}
                    if (d.id.startsWith("From")) {{
                        return "green";
                    }} else {{
                        return d3.scaleOrdinal(d3.schemeCategory10)(1);
                    }}
                }}

                var simulation = d3.forceSimulation(nodes)
                    .force("link", d3.forceLink(processedLinks).id(d => d.id).distance(200))
                    .force("charge", d3.forceManyBody().strength(-100))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .on("tick", ticked);

                function drag() {{
                    return d3.drag()
                        .on("start", function(event, d) {{
                            // When the node is selected ...
                            if (!event.active) simulation.alphaTarget(0.3).restart();
                            d.fx = d.x;
                            d.fy = d.y;
                        }})
                        .on("drag", function(event, d) {{
                            // When the node is being dragged ...
                            d.fx = event.x;
                            d.fy = event.y;
                            updateNodePosition(d.id, {{x: event.x, y: event.y}});
                            ticked();
                        }})
                        .on("end", function(event, d) {{
                            // When the node has been dragged ... we store the coordinates of where it's been dragged in its fx and fy attributes
                            if (!event.active) simulation.alphaTarget(0);
                            d.fx = event.x;
                            d.fy = event.y;
                        }});
                }}

                function updateNodePosition(nodeId, position) {{
                    if (window.mainWindow) {{
                        window.mainWindow.updateNodePosition(nodeId, position);
                    }}
                }}

                function ticked() {{
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);

                    node
                        .attr("cx", d => d.x)
                        .attr("cy", d => d.y);

                    label
                        .attr("x", d => d.x)
                        .attr("y", d => d.y);

                    labels
                        .attr("x", d => (d.source.x + d.target.x) / 2)
                        .attr("y", d => (d.source.y + d.target.y) / 2 - 10);

                }}


                new QWebChannel(qt.webChannelTransport, function(channel) {{
                    window.mainWindow = channel.objects.mainWindow;
                }});
                var zoom = d3.zoom()
                    .scaleExtent([0.1, 10])
                    .on("zoom", (event) => {{
                        g.attr("transform", event.transform);
                    }});

                svg.call(zoom);

                setInterval(updateAircraftPositions, 1000);
            </script>
        </body>
        </html>
        """
        self.webview.setHtml(html_content)

    # Import a spatial configuration from a JSON file manually
    def import_json_manual(self,file_path):
        # Emptying the list of aircrafts every time we import a spatial configuration
        self.view_model.traffic.aircrafts=[]
        self.view_model.import_json_data(file_path)
        # Reload the graph to reflect the new configuration
        self.load_d3_graph()

    # Handle the event when the import JSON button is clicked
    def import_json_button_clicked(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("JSON Files (*.json)")
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        # Emptying the list of aircrafts every time we import a spatial configuration
        self.view_model.traffic.aircrafts=[]
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.view_model.import_json_data(file_path)
            self.load_d3_graph()

    # Save the current state of the graph to a JSON file
    def save_graph_state(self):
        text, ok = QInputDialog.getText(self, "Save Graph", "Enter filename:")
        if ok and text:
            # Create file path with .json extension
            file_path = f"{text}.json"
            self.view_model.save_graph_state_to_json(file_path)

    # Save the current scenario state to a JSON file
    def save_scenario_state(self, file_path):
        text, ok = QInputDialog.getText(self, "Save Scenario", "Enter filename:")
        if ok and text:
            # Create file path with .json extension
            file_path = f"{text}.json"
            self.view_model.save_scenario_to_json(file_path)

    # Start aircraft motion using a JSON file for aircraft data
    def start_motion_manual(self, file_path):
        # Taking planes coming from previous scenarios out of the graph
        for plane in self.view_model.traffic.aircrafts:
                if self.webview:
                    self.webview.page().runJavaScript(f"deleteAircraft('{plane.id}')")
        # Clear the list of aircrafts
        self.view_model.traffic.aircrafts = []
         # Start a timer to update positions every second
        self.timer.start(1000)
        dico = self.view_model.import_json_data_aircraft(file_path)
        for k in dico:
            # Add each aircraft to the view model
            self.view_model.add_aircraft(k, dico[k]['starting_node'], dico[k]['route'], dico[k]['end_node'])

    # Start aircraft motion using a file dialog to select the JSON file
    def start_motion(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("JSON Files (*.json)")
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            # Taking planes coming from previous scenarios out of the graph
            for plane in self.view_model.traffic.aircrafts:
                    if self.webview:
                        self.webview.page().runJavaScript(f"deleteAircraft('{plane.id}')")
            self.view_model.traffic.aircrafts = []
            file_path = file_dialog.selectedFiles()[0]
            self.timer.start(1000)  # Update every second
            dico = self.view_model.import_json_data_aircraft(file_path)
            for k in dico:
                self.view_model.add_aircraft(k, dico[k]['starting_node'], dico[k]['route'], dico[k]['end_node'])
                time.sleep(1)

            #self.timer.start(1000)  # Update every second

    # Update the positions of all aircrafts in the graph
    def update_aircraft_positions(self):
        try:
            # Get the traffic priorities and update aircrafts structure
            traffic = self.view_model.traffic.priorities_algo()
            for plane in self.view_model.traffic.aircrafts:
                if plane.position == None and (plane.status == "DEPARTED" or plane.status == "PARKED"):
                # Skip updating position if aircraft is not in motion or parked
                    pass

                if plane.current_route_index >= 0 and len(plane.route)>0:
                    # Move the aircraft and get its new position
                    position = self.view_model.move_aircraft(plane.id)
                    #print("\n \n el trafico : ",traffic)
                    #for aircraft in self.view_model.traffic.aircrafts:
                        #print(aircraft.id," : ", aircraft.priority, " on .. ",aircraft.current_node['id'])
                    if self.webview and position:
                         # Update the aircraft position on the web view
                         #print(plane.id, " here and at ",plane.get_current_speed()," i ---> ",plane.i_motion_edge, " with priority : ",plane.priority)
                         self.webview.page().runJavaScript(f"moveAircraft('{plane.id}', {json.dumps(position)},'{plane.priority}','{plane.status}')")
        except RuntimeError:
            print("End of execution, RuntimeError")
            self.timer.stop()

    # Update the position of a node in the view model
    @Slot(str, dict)
    def updateNodePosition(self, node_id, position):
        self.view_model.update_node_position(node_id, position)

    # Get the current positions of all aircrafts
    @Slot(result='QVariant')
    def getAircraftPositions(self):
        positions = {}
        for plane in self.view_model.traffic.aircrafts:
            if plane.position != None:
                positions[plane.id] = plane.position
        return json.dumps(positions)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
