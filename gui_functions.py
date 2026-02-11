import cv2
import numpy as np
import math
import pyautogui
import winsound
from utilities import timestamp as timestamp, debug as debug, log as log
from pynput import mouse
import time

class GUI:
    folder = "linkedin/"
    #folder = "8tango/"
    img_moon    = folder + "cell_moon.png"
    img_sun     = folder + "cell_sun.png"
    img_empty   = folder + "cell_empty.png"
    img_cross   = folder + "symbol_cross.png"
    img_equal   = folder + "symbol_equal.png"
    img_game    = folder + "initial_grid.png"
    # Convention:
    # x,y = ABSOLUTE COORDINATES ON SCREEN;
    # u,v = RELATIVE COORDINATES ON GRID IMAGE
    # a,b = RELATIVE COORDINATES NORMALIZED BY GRID SPACING
    # (x,u,a = vertical; y,v,b = horizontal; origin = top left)

    def __init__(self, manual_n: int = 0, sensitivity: float = 0.91):
        self.x0             = 0
        self.y0             = 0
        self.region         = []
        self.grid_spacing   = 0
        self.grid_size      = 0
        self.grid_n         = 6
        self.grid_uv_coord  = np.empty([0,0,2])
        self.grid_xy_coord  = np.empty([0,0,2])
        self.manual_n       = manual_n
        self.sensitivity    = sensitivity


    def start(self):
        print(f"{timestamp()} Ready to start. ")
        print("    Without right-clicking anywhere:\n"
              "    - Open your browser\n"
              "    - Click on a new game of Tango\n"
              "    - As soon as the game is shown on screen, RIGHT-click anywhere to start the script\n"
              "    - QUICKLY: LEFT-click on the top-left corner of the game grid,\n"
              "               and then LEFT-click on the bottom-right corner.\n"
              "    - Enjoy the magic ;) ")
        self.snapshot()
        print(f"{timestamp()} Image acquired successfully")
        self.detect_all()
        print(f"{timestamp()} Game read successfully")

    def complete(self, raw_clicklist):
        self.import_clicklist(raw_clicklist)
        print(f"{timestamp()} Clicklist imported")
        print(f"{timestamp()} Solution clicking started")
        self.clicker2()
        print(f"{timestamp()} Solution clicking completed.")

    def snapshot(self):
        # Wait until a right click is detected (it gives the user the time to change window)
        _          = GUI.where_clicked('right')
        winsound.Beep(2000,500)
        print(f"{timestamp()} Started! Click top-left corner and bottom-right corner now.")
        # Top-left click = origin, Bottom-right click = endpoint
        origin     = GUI.where_clicked('left')
        endpoint   = GUI.where_clicked('left')
        print(f"{timestamp()} Clicked!")
        self.x0     = origin[0]
        self.y0     = origin[1]
        width  = abs(endpoint[0] - self.x0)
        height = abs(endpoint[1] - self.y0)
        self.region = [self.x0, self.y0, width, height]
        # Acquire image and saves it
        im = pyautogui.screenshot(GUI.img_game, region=self.region)

    @staticmethod
    def where_clicked(key = "left"):

        def _on_click(x, y, button, pressed):
            if key == 'left' and button == mouse.Button.left and pressed:
                return False  # Returning False if you need to stop the program when Left clicked.
            if key == 'right' and button == mouse.Button.right and pressed:
                return False  # Returning False if you need to stop the program when Left clicked.

        listener = mouse.Listener(on_click=_on_click)
        listener.start()
        listener.join()
        return mouse.Controller().position

    def detect_all(self):
        # Preloads template image
        cv2_image = cv2.imread(GUI.img_game,  cv2.IMREAD_GRAYSCALE)
        # Finds occurrencies in the snapshot
        moons_uv  = GUI.find_template(cv2_image, GUI.img_moon,  threshold = self.sensitivity)
        suns_uv   = GUI.find_template(cv2_image, GUI.img_sun,   threshold = self.sensitivity)
        empty_uv  = GUI.find_template(cv2_image, GUI.img_empty, threshold = self.sensitivity)
        equals_uv = GUI.find_template(cv2_image, GUI.img_equal, threshold = self.sensitivity)
        cross_uv  = GUI.find_template(cv2_image, GUI.img_cross, threshold = self.sensitivity)
        if debug: print(f"Objects found: {len(moons_uv)} moons, {len(suns_uv)} suns, {len(empty_uv)} empty cells, "
              f"{len(equals_uv)} equal symbols, {len(cross_uv)} cross symbols. ")

        if debug: print(f"{timestamp()} Start extrapolation grid-space info")
        # Extrapolates grid-space information from detected cells
        self.detect_grid(moons_uv + suns_uv + empty_uv)
        if debug: print(f"Grid size: {self.grid_n}x{self.grid_n} ")
        # Locates the found cells in the grid-space and builds Game Grid
        if debug: print(f"{timestamp()} Start location grid")
        GameGrid = np.int8(np.zeros((self.grid_n,self.grid_n)))
        GameGrid[self.locate_cells_on_grid(moons_uv)] = -1
        GameGrid[self.locate_cells_on_grid(suns_uv)]  =  1

        # Locates dependency symbols in the grid-space and builds Game Depend list
        if debug: print(f"{timestamp()} Start depend location")
        GameDepend = np.append(
            self.locate_symbol_on_grid(equals_uv,1),
            self.locate_symbol_on_grid(cross_uv,-1),
            axis=0 )

        # Stores Game Grid and Game Depend in class variables
        self.GameGrid = GameGrid
        self.GameDepend = GameDepend

    def detect_grid(self, cells):
        size = min(self.region[2], self.region[3])
        if self.manual_n:
            if debug: print(f"Manual grid n = {manual_n}. Find_grid_spacing is skipped.")
            n = self.manual_n
            spacing = int(size/n)
        else:
            spacing = GUI.find_grid_spacing(cells)
            n = int(size / spacing)
        uv_centers_1D = np.int32(np.linspace(0 + spacing/2, size - spacing/2, n))
        u, v = np.meshgrid(uv_centers_1D, uv_centers_1D, indexing="ij")
        uv_centers = np.stack((u,v), axis=-1)
        xy_centers = self.uv2xy(uv_centers)

        self.grid_spacing   = spacing
        self.grid_size      = size
        self.grid_n         = n
        self.grid_uv_coord  = uv_centers
        self.grid_xy_coord  = xy_centers

    def locate_cells_on_grid(self, objects):
        output = np.bool(np.zeros((self.grid_n,self.grid_n)))
        for item in objects:
            # Centers of the detected item, in spacing coordinates ab
            u = int(item[0] + item[2] / 2)
            v = int(item[1] + item[3] / 2)
            a, b = self.uv2ab((u, v))
            # Difference between detected and expected position (0.5,0.5), in spacing units
            # WARNING: x,y and row,col are swapped! (x=col, v=row)
            col = round(a - 0.5)
            row = round(b - 0.5)
            output[row,col] = True
        return output

    def locate_symbol_on_grid(self, objects, value):
        output = []
        for item in objects:
            # Centers of the detected item, in spacing coordinates ab
            u = int(item[0] + item[2] / 2)
            v = int(item[1] + item[3] / 2)
            a, b = self.uv2ab((u, v))
            if debug: print(f"Symbol with (a,b) = {a},{b}")
            # If  a is closer to 0%spacing than a 0.5%spacing,
            # and b is closer to 0.5%spacing than a 0%spacing
            # then the symbol is on a horizontal grid-line, in between two vertical grid-line,
            # and thus the symbol is between two vertically-adjacent cells
            if (round(a * 2) / 2) % 1 == 0 and (round(b * 2) / 2) % 1 == 0.5:
                if debug: print(f"is between two cells on top of each other.")
                # Cell below the symbol
                col = round(a)
                row = round(b - 0.5)
                output.append([row, col-1, row, col, value])
            # If  a is closer to 0.5%spacing than a 0%spacing,
            # and b is closer to 0%spacing than a 0.5%spacing
            # then the symbol is on a vertical grid-line, in between two horizontal grid-line,
            # and thus the symbol is between two horizontally-adjacent cells
            elif (round(a * 2) / 2) % 1 == 0.5 and (round(b * 2) / 2) % 1 == 0:
                if debug: print(f"is between two cells next to each other.")
                # Cell right to the symbol
                col = round(a - 0.5)
                row = round(b - 0)
                output.append([row-1, col, row, col, value])
        if debug: print(output)
        return np.array(output)

    def uv2xy(self, uv_matrix):
        uv_matrix = np.array(uv_matrix)
        if len(uv_matrix.shape)==1:
            uv_matrix = uv_matrix.reshape([1,1,2])
        n,m = uv_matrix.shape[0:2]
        xy_matrix = np.int32(np.zeros((n,m,2)))
        for i in range(n):
            for j in range(m):
                xy_matrix[i,j,:] = [ uv_matrix[i,j,0]+self.x0, uv_matrix[i,j,1]+self.y0 ]
        return xy_matrix

    def uv2ab(self, uv_matrix):
        uv_matrix = np.array(uv_matrix)
        original_shape = uv_matrix.shape
        if len(uv_matrix.shape)==1:
            uv_matrix = uv_matrix.reshape([1,1,2])
        n,m = uv_matrix.shape[0:2]
        ab_matrix = np.empty((n,m,2))
        for i in range(n):
            for j in range(m):
                ab_matrix[i,j,:] = [ uv_matrix[i,j,0] / self.grid_spacing, uv_matrix[i,j,1] / self.grid_spacing ]
        return ab_matrix.reshape(original_shape)


    @staticmethod
    def find_grid_spacing(occurrences):
        threshold = 10
        # Occurrences lists top-left corner, while I want to find spacing between centers for robustness
        u_centr = [int(item[0] + item[2]/2) for item in occurrences]
        v_centr = [int(item[1] + item[3]/2) for item in occurrences]
        u_centr.sort()
        v_centr.sort()
        du = [(u_centr[i+1]-u_centr[i]) for i in range(len(u_centr)-1) if (u_centr[i+1]-u_centr[i]) > threshold]
        dv = [(v_centr[i+1]-v_centr[i]) for i in range(len(v_centr)-1) if (v_centr[i+1]-v_centr[i]) > threshold]
        delta = du + dv
        spacing = int(sum(delta) / len(delta))
        return spacing

    @staticmethod
    def find_template(image, template, threshold = 0.91):

        def _suppress_duplicates(detections, min_dist=10):
            # sort by score (best first)
            detections = sorted(detections, key=lambda x: x[2], reverse=True)
            to_keep = []
            for item in detections:
                x, y = item[0], item[1]
                too_close = False
                for k in to_keep:
                    if math.hypot(x - k[0], y - k[1]) < min_dist:
                        too_close = True
                        break
                if not too_close:
                    to_keep.append(item)
            return to_keep

        #image       = cv2.imread(image,     cv2.IMREAD_GRAYSCALE)
        template    = cv2.imread(template,  cv2.IMREAD_GRAYSCALE)

        detections = []

        for scale in np.linspace(0.5, 2.0, 40):
            resized_template = cv2.resize(template, None, fx=scale, fy=scale)
            rh, rw = resized_template.shape

            if rh > image.shape[0] or rw > image.shape[1]:
                continue

            result      = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)
            locations   = np.where(result >= threshold)

            for pt in zip(*locations[::-1]):
                detections.append( [pt[0], pt[1], rw, rh, scale] )
        detections = _suppress_duplicates(detections, 10)
        return detections

    def import_clicklist(self, ab_clicklist):
        xy_clicklist = []
        for click in ab_clicklist:
            a, b, num_clicks = click[0:3]
            x, y = self.grid_xy_coord[a,b]
            xy_clicklist.append( [x, y, num_clicks] )
        self.xy_clicklist = xy_clicklist
        return

    def clicker(self):
        dt = 0
        for click in self.xy_clicklist:
            x, y, num_clicks = click[0:3]
            if dt != 0:
                pyautogui.moveTo(x, y, dt)
                for _ in range(num_clicks):
                    pyautogui.click()
                    time.sleep(dt)
            else:
                pyautogui.click(x = x, y = y, clicks=num_clicks)
            if debug:  print(f"Clicked {num_clicks} time(s) on position {x},{y}")
            else:       print("", end="")

    def clicker2(self):
        dt = 0
        for click in self.xy_clicklist:
            x, y, num_clicks = click[0:3]
            button = "left" if num_clicks == 1 else "right"
            if dt != 0:
                pyautogui.moveTo(x, y, dt)
                pyautogui.click(button=button)
            else:
                pyautogui.click(x=x, y=y, button=button)
            if debug:
                print(f"Clicked {num_clicks} time(s) on position {x},{y}")
            else:
                print("", end="")





