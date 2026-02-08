# tango-solver
**Automatic solver** of LinkedIn's game [**Tango**](https://www.linkedin.com/games/tango)
using:
- **image analysis** of the game displayed on the browser (OpenCV),
- rule-based procedural **solution**,
- and completion of the game by **mouse automation** over the browser.


## Context and Disclaimer
This is a fun project by me `@lorenzopale` to get down to more object-oriented programming and dip my toes in to basic image recognition.

The code is not optimised, nor robust to graphics changes. I will try to mantain it as much as possible, but a game GUI variation will break the image recognition and break the solver completely. A more robust method _may_ be implemented _eventually_.

> [!WARNING]
> This solver **is not meant to be used to cheat** on the online LinkedIn game: what would be the fun of it?

> _Last time tested: 04-feb-2026 --> Passed_

## Installation
```sh
git clone https://github.com/lorenzopale/tango-solver.git
```
Check if all requirements are met by running `pip install --dry-run -r requirements.txt` (or `pip install -r requirements.txt` to install/upgraded up to the requirements)
## Usage
1. Launch the `tango_solver.main()` script using one of the following methods:

   - **As script from shell**
   
    ```sh
    python tango_solver.py
    ```
    
    - **As function in python console**
  
    ```python
    from tango_solver import main as tango_solver
    tango_solver()
    ```
2. Wait for the code to initialize. The following (or analogous) will be displayed:

   ```sh
   ============================================================
   =                       TANGO SOLVER                       =
   =                    v1.1 - 2026.02.04                     =
   =                     Lorenzo Paleari                      =
   ============================================================
   [2026-02-04 18:46:46] Script started.
   [2026-02-04 18:46:46] Object initializated successfully.
   [2026-02-04 18:46:46] GUI acquisition started.
   [2026-02-04 18:46:46] Ready to start.
   ```
3. **Without right-clicking anywhere** (i.e. a right-click would be interpreted as a start command), open the browser and **open** a [Tango game](https://www.linkedin.com/games/tango).
4. As soon as the gameboard is displayed:
   - quickly **right-click** anywhere to **start** the mouse tracking,
   - then rapidly **left-click** on the **top-left** corner of the game grid
   - and then **left-click** on the **bottom-right** corner
5. The solver will start automatically. It will:
   - Acquire the grid location from the left-click positions;
   - Perform image recognition based on template images to locate empty cells, moons, suns, equal symbols and cross symbols;
   - Create an aligned reference grid based on the recognised cells;
   - Translate the recognised features into a codified game;
   - Solve the codified game by iterating over rows and columns and procedurally filling in empty cells;
   - Once a solution is found, translates the solution into the moves to perform;
   - Perform right/left clicks to input the found solution into the browser grid.
  
## Media

## License
GNU General Public License v3.0 (See [LICENSE](LICENSE))

## Authors
- Lorenzo Paleari [github.com/lorenzopale/](github.com/lorenzopale/)
