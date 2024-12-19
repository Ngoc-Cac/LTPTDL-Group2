# LTPTDL-Group2
This is a final group project implementing Dijkstra's Algorithm and A-star Algorithm in Python.

## Dijkstra's Algorithm
Source code for Dijkstra's Algorithm as well as demonstration can be found in LTPTDL-Group2/Dijkstra/algorithm.ipynb\
You can freely edit cells in 'Demo' section of the notebook to experiment with the group's algorithm.\
We also provide a function to read in graph data from a csv file. Note that the data in the csv file must be of the form node_from, node_to, weight.

## A-star Algorithm
Source code for A-star Algorithm and demonstration can be found in LTPTDL-Group2/A-star/algorithm.ipynb
### Robot Vacuum Problem
This implementation is applied in the Robot Vacuum problem, where the robot exists in a grid of dimension m $\times$ n with an arbitrary amount of dirty cells and has to clean every dirty cells in that grid.\
The cost of moving is 1 and the cost of cleaning a dirty cell starts at 1 but increments everytime the robot moves.\
The A-star implementation aims to find the path that the robot has to go along to clean every dirty cells with the smallest cost.
### Demonstration
You can run the cells beyond 'Chương trình' section in the notebook to test out the group's algorithm.\
There is a user input zone where you can specify information about the grid that the robot exists in.\
For visualisation purposes, we also provide an animation of the robot moving.
### GUI
For better ease of use, we provide a GUI for editting the grid, running the algorithm and visualising the results.\
To run the program, run the executable at LTPTDL-Group2/A-star GUI/Vacuum Robot Astar.exe\
If the executable does not work, you can instead run the source code directly, provided at LTPTDL-Group2/A-star GUI/main.py. **Note: you need to install PyQt6 in order to successfully run the script.**

---------------
## Our contributors:
Nguyễn Tấn Gia Bảo\
Trịnh Ngọc Các\
Nguyễn Thị Ngọc Diệp\
Nguyễn Đôn Đức
