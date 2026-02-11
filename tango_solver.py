import sys, math, winsound
from backend_solver import Game as Game
from gui_functions import GUI as GUI
from utilities import timestamp as timestamp, debug as debug, log as log

VERSION = "1.3"
DATE = "2026.02.11"

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


def main(manual_n: int = 0, sensitivity: float = 0.91):
    print("="*60)
    print("=" + f"{"TANGO SOLVER":^58}" +"=")
    print("=" + f"{f"v{VERSION} - {DATE}":^58}" + "=")
    print("=" + f"{f"Lorenzo Paleari":^58}" + "=")
    print("=" * 60 + "\n")
    if log: print(f"{timestamp()} Script started.")
    gui = GUI(manual_n = manual_n, sensitivity = sensitivity)
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
    manual_n = 0
    sensitivity = 0.91
    for arg in  sys.argv[1:]:
        if arg.startswith("-n="):
            manual_n = int(arg.split("=")[1])
        if arg.startswith("-s="):
            sensitivity = float(arg.split("=")[1])
    main(manual_n = manual_n, sensitivity = sensitivity)