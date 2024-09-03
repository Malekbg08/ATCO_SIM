 #
 # ENAC Internship - Abstracting A-SMGCS Display
 # Malek Ben Ghachem (malek.08@hotmail.fr)
 # Representation of the Paris Roissy-CDG airport's south section in an oriented graph
 #

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from view import MainWindow

#  ----------------------------------------------------------------------------        IMPORTANT       --------------------------------------------------------------------------
#
#  1)                                                                   Please note that the speed mustn't exceed 50 knots
#
#  2)                   You must follow this strict order while editing aircraft motion data : First change its position with set_position_manual
#                       then change its route with modify_route_manual. The position must be set prior to modifying the route to allow the program
#                       to identify the correct edge with the corresponding source node. There are edges with the same name but not the same source
#                       nodes
#
#  3)     When assigning a route (or new route) to an aircraft, the route must be formatted like this: taxiway1, speed1, taxiway2, speed2, ... , taxiway-n, speed-n
#
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    view = MainWindow()
    # Importer the json file that contains the spatial configuration of the Paris Roissy CDG airport
    view.import_json_manual("./jsondatacdg.json")
    view.show()
    # Using QTimer to delay the launch of the scenario so the graph loads properly and we have time to scroll down
    # QTimer.singleShot(10000,lambda: view.start_motion_manual("./scenarito.json"))
    # Using QTimer to delay the creation of the aircraft so the graph loads properly and we have time to scroll down
    # QTimer.singleShot(11000, lambda: view.create_aircraft_manual("AF780", "LA_RWY", ["V1", "4", "S2", "5"], "TO_RWY"))
    # Several change of positions and routes for the same aircraft
    # QTimer.singleShot(15000, lambda: view.set_position_manual("AF780", "FromC"))
    # QTimer.singleShot(18000, lambda: view.set_position_manual("AF780", "LA_RWY"))
    # QTimer.singleShot(20000, lambda: view.modify_route_manual("AF780", ["V1","3","S2","2"]))
    # QTimer.singleShot(21000, lambda: view.set_position_manual("AF780", "FromC"))
    # QTimer.singleShot(22000, lambda: view.modify_route_manual("AF780", ["TA3","3","R","2"]))
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
