# ATCO_SIM
ATCo Simulator is an abstraction of the nowadays ASMGCs Displays.
The Paris Charles De Gaulle airport is represented as an oriented graph where a node is an intersection and a link is a taxiway.
By using my system, you would be able to monitor aircraft that are moving and the challenges that it implies, such as conflicts and concurrency.
This prototype has already been shown to ground controllers who see great promise in it, which suggests that there might be areas of improvement that can be explored in the A-SMGCS's display, and this would hopefully result in great outcomes !

## By Malek Ben Ghachem

## Project setup

1- Run `python3 main.py` to launch the system

2- Click `Import` and select a .json file that contains the airport configuration (Default file named jsondatacdg.json)

  2a- You are able to edit the graph by dragging the nodes in any way you want
  
  2b- You will therefore be able to save the current graph state by clicking the `Save Graph`button

3'- Click `Play` and select a .json file that contains a list of aircrafts with their routes

3"- Create an aircraft (or more) and make it move by filling the `Aircraft ID`, `Start Node ID`, `Route`, `End Node ID` textfields

4- You are also able to edit an aircraft that is already moving but you'll have to edit its position before assigning it a new route
 
  4a- When assigning a route (or new route) to an aircraft, the route must be formatted like this: taxiway1, speed1, taxiway2, speed2, ... , taxiway-n, speed-n 

5- You can save every aircraft you created along with the routes by clicking `Save Scenario`

5a- You would then be able to replay that scenario by clicking `Play'


(You will find more helpful comments in almost every python file)

## Important, please read carefully

Please note that the airport config default file is `jsondatacdg.json` and the scenario default file is `scenarito.json`

You can see how these files have been written to understand better the overall functioning 

Please note that you will have to scroll down after importing `jsondatacdg.json`, this is due to graphical issues that causes the graph to be off-centered
