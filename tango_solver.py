import sys, math, winsound
from backend_solver import Game as Game
from gui_functions import GUI as GUI
from utilities import timestamp as timestamp, debug as debug, log as log

class sound:
    @staticmethod
    def lowbeep():
        winsound.Beep(4000, 500)
    @staticmethod
    def highbeep():
        winsound.Beep(4000, 50)
    @staticmethod
    def victory():
        winsound.MessageBeep(winsound.MB_OK)


def main():
    if log: print(f"{timestamp()} Script started.")
    gui = GUI()
    if log: print(f"{timestamp()} Object initializated successfully.")

    if log: print(f"{timestamp()} GUI acquisition started.")
    sound.lowbeep()
    gui.start()
    sound.highbeep()
    if log: print(f"{timestamp()} GUI acquisition completed successfully.")


    if log: print(f"{timestamp()} GAME compiling started.")
    game = Game(n = gui.grid_n)
    game.import_game_from_gui(gui)
    sound.highbeep()
    if log: print(f"{timestamp()} GAME compiling completed successfully.")

    if log: print(f"{timestamp()} GAME solution started.")
    game.solve()
    sound.highbeep()
    if log: print(f"{timestamp()} GAME solution completed successfully.")

    if log: print(f"{timestamp()} GUI solution clicking started.")
    gui.complete(game.export_solution_moves())
    sound.highbeep()
    if log: print(f"{timestamp()} GUI solution clicking completed successfully.")
    sound.victory()

# # # MAIN SCRIPT when executed as script from command line
if __name__ == "__main__":

    main()