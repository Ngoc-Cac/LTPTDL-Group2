from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import PyQt6.QtWidgets as QtWidgets


import matplotlib
matplotlib.use('QtAgg')

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


import random as rand, math

from algorithm import Position, astar_vacuum, chebyshev_move


from typing import Literal


TITLE_FONT = QFont('Times', 12)
TITLE_FONT.setBold(True)
INSTRUCTION_FONT = QFont('Times', 12)

EDIT_TAB_INSTRUCTION_TXT = """1. Add Cell - Thêm ô dơ 
    Cú pháp nhập: (x, y) - x, y lần lượt là vị trí hàng và cột trong ma trận của ô dơ. 
    Thao tác: Nhập tọa độ, sau đó nhấn vào nút Add Cell.

2. Remove Cell - Xóa ô dơ đã thêm
    Cú pháp nhập: (x, y) - x, y lần lượt là vị trí hàng và cột trong ma trận của ô dơ cần xóa.
    Thao tác: Nhập tọa độ, sau đó nhấn vào nút Remove Cell.

3. Randomize - Khởi tạo số lượng ô dơ ngẫu nhiên
    Cú pháp nhập: n - n là số ô dơ, n >= 1.
    Thao tác: Nhập số lượng ô dơ, sau đó nhấn đúp vào nút Randomize.

4. Change Dimension - Thay đổi kích thước ma trận
    Cú pháp nhập: (x, y) - x, y là số dòng và số cột của ma trận.
    Thao tác: Nhập kích thước mới, sau đó nhấn vào nút Change Dimension.
    
5. Clear - Xóa tất cả ô dơ trong ma trận"""
HOME_INSTRUCTION_TXT = """1. Place - Đặt vị trí bắt đầu của robot
    Cú pháp nhập: (x, y) - x, y lần lượt là vị trí hàng và cột trong ma trận của robot.
    Thao tác: Nhập tọa độ, sau đó nhấn vào nút Add Cell. Người dùng có thể nhập 'r' để chỉ định vị trí ngẫu nhiên.

2. Run - Chạy A* và hiển thị đường đi ngắn nhất để dọn các ô dơ"""


DIRTY_CELL_COLOUR: tuple[float] = (1, 0, 0, .5)
DIRTY_CELL_MARKER: str = 'X'
DIRTY_CELL_MARKERSIZE: float = 15

ROBOT_COLOUR: tuple[float] = (34 / 255, 139 / 255, 34 / 255, 1)
ROBOT_MARKER: str = 's'
ROBOT_MARKERSIZE: float = 10

PATH_COLOUR: tuple[float] = (0, 0, 1, .2)
PATH_MARKER: str = '--'

MAX_ITER = 200_000


move_rate: float = 500

grid_dim: list[int, int] = [5, 5]
dirty_cells: set[Position] = set()
start: list[int, int] = [0, 0]
path: list[Position] = []
min_cost: int = 0


def format_cost_text(clean_cost: int, current_cost: int, total_cost: int) -> str:
    return f"Clean cost: {clean_cost:<15}" +\
           f"Current cost: {current_cost:<15}" +\
           f"Minimum cost: {total_cost}"

def update_markersize(canvas: 'MplCanvas')\
    -> dict[Literal['robot', 'dirty'], float]:
    global ROBOT_MARKERSIZE, DIRTY_CELL_MARKERSIZE

    # get size in inches
    bbox = canvas.axes.get_window_extent().transformed(canvas.fig.dpi_scale_trans.inverted())
    # 1 in = 72 pts
    width, height = bbox.width * 72, bbox.height * 72
    width, height = width / grid_dim[1], height / grid_dim[0]
    cell_area = width * height

    ROBOT_MARKERSIZE = math.sqrt(.05 * cell_area)
    DIRTY_CELL_MARKERSIZE = math.sqrt(.13 * cell_area)

def setup_grid(ax, rows: int, columns: int):
    ax.clear()

    ax.set_xlim(.5, columns + .5)
    ax.set_ylim(.5, rows + .5)
    ax.set_xticks(range(1, columns + 1))
    ax.set_yticks(range(1, rows + 1))
    ax.tick_params(left=False, bottom=False)

    ax.vlines([i + .5 for i in range(0, columns + 1)],
              ymin=0, ymax=rows + 1, colors=(0, 0, 0, 0.2))
    ax.hlines([i + .5 for i in range(0, rows + 1)],
              xmin=0, xmax=columns + 1, colors=(0, 0, 0, 0.2))


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)


class ErrorDialog(QtWidgets.QDialog):
    def __init__(self,  msg: str, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setFixedSize(300, 100)
        self.setWindowTitle("An Error Occured!")
        icon = self.style().\
                    standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical)
        self.setWindowIcon(icon)


        self.button = QtWidgets.QPushButton('Ok', parent=self)
        self.button.setFixedWidth(50)
        self.button.clicked.connect(self.close)

        message = QtWidgets.QLabel(msg)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(message)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

class InfoDialog(QtWidgets.QDialog):
    def __init__(self, title: str, msg: str, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setFixedSize(300, 100)
        self.setWindowTitle(title)
        icon = self.style().\
                    standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxInformation)
        self.setWindowIcon(icon)


        self.button = QtWidgets.QPushButton('Ok', parent=self)
        self.button.setFixedWidth(50)
        self.button.clicked.connect(self.close)

        message = QtWidgets.QLabel(msg)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(message)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)


class Guide(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        home_title = QtWidgets.QLabel(parent=self)
        home_title.setText("Các nút trong thẻ Home")
        home_title.setFont(TITLE_FONT)
        home_title.setGeometry(10, 10, 1000, 20)

        home_instruct = QtWidgets.QLabel(parent=self)
        home_instruct.setText(HOME_INSTRUCTION_TXT)
        home_instruct.setFont(INSTRUCTION_FONT)
        home_instruct.setAlignment(Qt.AlignmentFlag.AlignJustify)
        home_instruct.setGeometry(10, 35, 1000, 100)

        edit_title = QtWidgets.QLabel(parent=self)
        edit_title.setText("Các nút trong thẻ Edit")
        edit_title.setFont(TITLE_FONT)
        edit_title.setGeometry(10, 225, 1000, 20)

        edit_instruct = QtWidgets.QLabel(parent=self)
        edit_instruct.setText(EDIT_TAB_INSTRUCTION_TXT)
        edit_instruct.setFont(INSTRUCTION_FONT)
        edit_instruct.setAlignment(Qt.AlignmentFlag.AlignJustify)
        edit_instruct.setGeometry(10, 250, 1000, 400)

class Input_Zone(QtWidgets.QWidget):
    def __init__(self, parent: 'Edit' = ...,) -> None:
        super().__init__(parent)

        self.vbox = QtWidgets.QVBoxLayout()
        
        self.input_box = QtWidgets.QLineEdit(parent=self)
        self.vbox.addWidget(self.input_box)

        self.init_buttons()
        self.init_labels()

        self.setLayout(self.vbox)

    def init_buttons(self):
        hbox = QtWidgets.QHBoxLayout()
        hbox2 = QtWidgets.QHBoxLayout()

        add_cell_button = QtWidgets.QPushButton('Add Cell', parent=self)
        remove_cell_button = QtWidgets.QPushButton('Remove Cell', parent=self)
        random_cell_button = QtWidgets.QPushButton('Randomize', parent=self)
        change_dim_button = QtWidgets.QPushButton('Change Dimension', parent=self)
        clear_button = QtWidgets.QPushButton('Clear', parent=self)

        add_cell_button.clicked.connect(lambda: self.handle_input('add'))
        remove_cell_button.clicked.connect(lambda: self.handle_input('remove'))
        random_cell_button.clicked.connect(lambda: self.handle_input('random'))
        change_dim_button.clicked.connect(lambda: self.handle_input('dimension'))
        clear_button.clicked.connect(self.parent().clear_cell)

        change_dim_button.setFixedWidth(130)

        hbox.addWidget(add_cell_button)
        hbox.addWidget(remove_cell_button)
        hbox.addWidget(random_cell_button)
        hbox2.addWidget(change_dim_button)
        hbox2.addWidget(clear_button)

        self.vbox.addLayout(hbox)
        self.vbox.addLayout(hbox2)

    def init_labels(self):
        ins_title = QtWidgets.QLabel(parent=self)
        ins_title.setText("Cú Pháp:")
        ins_title.setFont(TITLE_FONT)

        instructions = QtWidgets.QLabel(parent=self)
        instructions.setText("""Add Cell: (x, y)
Remove Cell: (x, y)
Randomize: số nguyên n >=1
Change dimension: (rows, cols)""")
        instructions.setFont(INSTRUCTION_FONT)

        self.vbox.addWidget(ins_title)
        self.vbox.addWidget(instructions)

    def handle_input(self, function: Literal['random', 'add', 'remove', 'dimension']):
        user_in = self.input_box.text()
        self.input_box.clear()
        if function == 'random':
            if not user_in.isdigit():
                ErrorDialog(f"""Randomize function needs to know the number of dirty cell!
{user_in} was given""").exec()
            else:
                self.parentWidget().randomize(int(user_in))
            return

        try:
            x, y = user_in.split(',')
            x, y = int(x[1:]), int(y[:-1])
        except ValueError:
            if function != 'dimension':
                msg = f"""Input grid coordinates as (x, y) in order to {function} dirty cell!"""
            else:
                msg = f"""Input number of rows and columns as (rows, columns) in order to change grid dimenion!"""
            ErrorDialog(msg).exec()
            return

        if function == 'add':
            self.parentWidget().add_cell(x, y)
        elif function == 'remove':
            self.parentWidget().remove_cell(x, y)
        else:
            self.parentWidget().change_dim(x, y)

class Edit(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.input_zone = Input_Zone(parent=self)
        self.init_canvas()


    def init_canvas(self):
        self.canvas = MplCanvas(width=5, height=4)
        setup_grid(self.canvas.axes, *grid_dim)
        update_markersize(self.canvas)
        self.dirty_cells, = self.canvas.axes.plot([], [],
                                                  DIRTY_CELL_MARKER,
                                                  color=DIRTY_CELL_COLOUR,
                                                  markersize=DIRTY_CELL_MARKERSIZE)

        plot_box = QtWidgets.QVBoxLayout()
        plot_box.addWidget(self.canvas)

        placeholder_wid = QtWidgets.QWidget(parent=self)
        placeholder_wid.setLayout(plot_box)
        placeholder_wid.setGeometry(280, 35, 770, 540)


    def randomize(self, no_cells: int):
        if no_cells + len(dirty_cells) > grid_dim[0] * grid_dim[1]:
            ErrorDialog(f"Not enough cells to place {no_cells} more dirty cells!").exec()
            return

        avail_spaces = []
        for i in range(1, grid_dim[1] + 1):
            for j in range(1, grid_dim[0] + 1):
                if not (temp := Position(i, j)) in dirty_cells: avail_spaces.append(temp)
        
        for new_cell in rand.sample(avail_spaces, no_cells):
            dirty_cells.add(new_cell)

        self.dirty_cells.set_xdata([pos.x for pos in dirty_cells])
        self.dirty_cells.set_ydata([pos.y for pos in dirty_cells])
        self.canvas.draw()

        path.clear()

    def add_cell(self, x: int, y: int):
        if (x < 1) or (y < 1) or\
           (x > grid_dim[1]) or (y > grid_dim[0]):
            ErrorDialog(f"Position of dirty must be within the grid dimension!\n({x}, {y}) was given").exec()
        elif (cell := Position(x, y)) in dirty_cells:
            InfoDialog(f"There is already a dirty cell at ({x, y})").exec()
        else:
            dirty_cells.add(cell)

            self.dirty_cells.set_xdata([pos.x for pos in dirty_cells])
            self.dirty_cells.set_ydata([pos.y for pos in dirty_cells])
            self.canvas.draw()

        path.clear()

    def remove_cell(self, x: int, y: int):
        if not (cell := Position(x, y)) in dirty_cells:
            ErrorDialog(f"There is no dirty cell at position {cell} to remove!").exec()

        dirty_cells.remove(cell)
        self.dirty_cells.set_xdata([pos.x for pos in dirty_cells])
        self.dirty_cells.set_ydata([pos.y for pos in dirty_cells])
        self.canvas.draw()

        path.clear()

    def change_dim(self, rows: int, columns: int):
        if rows < 1 or columns < 1:
            ErrorDialog(f"Rows and columns must be non-zero! ({rows}, {columns}) was given").exec()
            return
        
        global dirty_cells
        grid_dim[0], grid_dim[1] = rows, columns

        changed = False
        if (start[1] > grid_dim[0]) or (start[0] > grid_dim[1]):
            start[0], start[1] = 0, 0
            changed = True
        
        new_dirty = set()
        for cell in dirty_cells:
            if (cell.x <= grid_dim[1]) and (cell.y <= grid_dim[0]):
                new_dirty.add(cell)
                changed = True
        dirty_cells = new_dirty

        if changed: path.clear()
        
        setup_grid(self.canvas.axes, rows, columns)
        update_markersize(self.canvas)
        self.dirty_cells, = self.canvas.axes.plot([pos.x for pos in dirty_cells], [pos.y for pos in dirty_cells],
                                                  DIRTY_CELL_MARKER, color=DIRTY_CELL_COLOUR,
                                                  markersize=DIRTY_CELL_MARKERSIZE)
        self.canvas.draw()

    def clear_cell(self):
        dirty_cells.clear()
        path.clear()
        self.dirty_cells.set_xdata([pos.x for pos in dirty_cells])
        self.dirty_cells.set_ydata([pos.y for pos in dirty_cells])
        self.canvas.draw()

class Home(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.vbox = QtWidgets.QVBoxLayout()

        self.init_input()
        self.init_canvas()
        self.update_canvas()

        self.setLayout(self.vbox)

    def init_canvas(self):
        self.canvas = MplCanvas(width=5, height=4)
        self.cost_text = self.canvas.fig.text(.28, .93, '')

        plot_box = QtWidgets.QVBoxLayout()
        plot_box.addWidget(self.canvas)

        placeholder_wid = QtWidgets.QWidget(parent=self)
        placeholder_wid.setLayout(plot_box)
        placeholder_wid.setFixedSize(900, 540)
        self.vbox.addWidget(placeholder_wid, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def update_canvas(self):
        setup_grid(self.canvas.axes, *grid_dim)
        self.dirty_cells, = self.canvas.axes.plot([pos.x for pos in dirty_cells], [pos.y for pos in dirty_cells],
                                                  DIRTY_CELL_MARKER, color=DIRTY_CELL_COLOUR,
                                                  markersize=DIRTY_CELL_MARKERSIZE)
        self.robot, = self.canvas.axes.plot([], [], ROBOT_MARKER, color=ROBOT_COLOUR,
                                            markersize=ROBOT_MARKERSIZE)
        self.path, = self.canvas.axes.plot([], [], PATH_MARKER, color=PATH_COLOUR)

        if (start[0] != 0) and  (start[1] != 0):
            self.robot.set_xdata([start[0]])
            self.robot.set_ydata([start[1]])

        if path:
            self.path.set_xdata([pos.x for pos in path])
            self.path.set_ydata([pos.y for pos in path])
        else:
            global total_cost
            total_cost = 0
        
        self.cost_text.set_text(format_cost_text(1, 0, total_cost))

        self.canvas.draw()

    def init_input(self):
        self.input_box = QtWidgets.QLineEdit()

        self.run_button = QtWidgets.QPushButton('Run')
        self.place_button = QtWidgets.QPushButton('Place')

        self.run_button.setFixedWidth(50)
        self.place_button.setFixedWidth(50)

        self.run_button.clicked.connect(self.run_algo)
        self.place_button.clicked.connect(self.set_pos)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.place_button)
        hbox.addWidget(self.run_button)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.input_box)
        vbox.addLayout(hbox)

        placeholder_wid = QtWidgets.QWidget()
        placeholder_wid.setLayout(vbox)
        placeholder_wid.setFixedWidth(150)

        self.vbox.addWidget(placeholder_wid, alignment=Qt.AlignmentFlag.AlignCenter)


    def run_algo(self):
        if (start[0] == 0) and (start[1] == 0):
            ErrorDialog("Please specify a start position for the robot before running!").exec()
            return
        
        self.run_button.setDisabled(True)

        if not path:
            path_exists = self.find_min_path()
            if path_exists:
                self.path.set_xdata([pos.x for pos in path])
                self.path.set_ydata([pos.y for pos in path])
            else:
                InfoDialog("Could not find optimal path for current cofiguration :(").exec()
                self.run_button.setDisabled(False)
                return
        

        clean_costs, cur_costs = [1], [0]
        prev = None
        for cell in path[1:]:
            if prev == cell:
                cur_costs.append(cur_costs[-1] + clean_costs[-1])
                clean_costs.append(clean_costs[-1])
            else:
                clean_costs.append(clean_costs[-1] + 1)
                cur_costs.append(cur_costs[-1] + 1)
            prev = cell

        local_dirty = dirty_cells
        prev = None
        frame = 0
        def animate(timer):
            nonlocal frame, prev, local_dirty, clean_costs, cur_costs

            if prev == path[frame]:
                local_dirty = local_dirty - {path[frame]}
                self.dirty_cells.set_data([cell.x for cell in local_dirty],
                                          [cell.y for cell in local_dirty])

            prev = path[frame]
            self.cost_text.set_text(format_cost_text(clean_costs[frame], cur_costs[frame], total_cost))
            self.robot.set_data([path[frame].x], [path[frame].y])
            self.canvas.draw()

            if (frame := frame + 1) >= len(path):
                timer.stop()
                self.update_canvas()
                self.run_button.setDisabled(False)

        timer = QTimer()
        timer.setInterval(move_rate)
        timer.timeout.connect(lambda: animate(timer))
        timer.start()

    def set_pos(self):
        user_in = self.input_box.text()
        self.input_box.clear()

        try:
            if user_in.lower() != 'r':
                x, y = user_in.split(',')
                x, y = int(x[1:]), int(y[:-1])
                if x < 1 or y < 1 or\
                   x > grid_dim[1] or y > grid_dim[0]:
                    raise ValueError()
            else:
                x, y = rand.choice([(i, j) for i in range(1, grid_dim[1] + 1)
                                           for j in range(1, grid_dim[0] + 1)])
        except ValueError:
            ErrorDialog("Input grid coordinates as (x, y) to specify robot's position!\n"+\
                        "Note: x and y must be >= 1 and <= (grid dimension)").exec()
            return
        
        start[0], start[1] = x, y
        self.robot.set_xdata([x])
        self.robot.set_ydata([y])
        self.canvas.draw()

    def find_min_path(self):
        global path, total_cost
        goal = astar_vacuum(dirty_cells, Position(*start),
                            max_iter=MAX_ITER, do_traceback=True)
        if not goal[0] is None:
            total_cost = goal[0].cost
            path = []
            for i, cell in enumerate(goal[1][:-1]):
                path.extend(chebyshev_move(cell.position, goal[1][i + 1].position))
            path.append(goal[0].position)
        
        return bool(path)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Vacuum Robot")
        self.setGeometry(220, 80, 1000, 600)
        self.setFixedSize(1100, 650)

        self.home_page = Home(self)

        global __prev_tab_index
        __prev_tab_index = 1

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(Guide(), 'User Guide')
        self.tabs.addTab(self.home_page, 'Home')
        self.tabs.addTab(Edit(), 'Edit Tab')
        self.tabs.setCurrentIndex(__prev_tab_index)
        self.tabs.tabBarClicked.connect(self.change_tab)

        self.setCentralWidget(self.tabs)

    def change_tab(self, index):
        global __prev_tab_index
        if (index == 1) and (__prev_tab_index == 2):
            self.home_page.update_canvas()
        __prev_tab_index = index



def main():
    vacuum_robot = QtWidgets.QApplication([])
    root = MainWindow()
    root.show()
    vacuum_robot.exec()

if __name__=="__main__":
    main()