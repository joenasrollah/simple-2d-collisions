# 2D Rigid-Body Physics & Collision Simulator

A lightweight 2D rigid-body dynamics simulator built from first principles in Python using Pygame. It implements continuous velocity integration, 2D vector elastic impulse resolution, and live conservation diagnostics without external physics libraries.

> **Project Background:** Originally developed as a Non-Exam Assessment (NEA) software project. Preserved and structured to showcase foundational mechanics, vector collision mathematics, and interactive simulation design.

---

## Core Features

* **Analytical 2D Collision Resolution:** Calculates impulse response between circular bodies of arbitrary mass using vector projection along the collision normal:
  $$\mathbf{v}_1' = \mathbf{v}_1 - \frac{2 m_2}{m_1 + m_2} \frac{\langle \mathbf{v}_1 - \mathbf{v}_2, \, \mathbf{r}_1 - \mathbf{r}_2 \rangle}{\Vert{}\mathbf{r}_1 - \mathbf{r}_2\Vert{}^2} (\mathbf{r}_1 - \mathbf{r}_2)$$
* **Position Overlap Correction:** Displaces intersecting bodies by their normal penetration depth to prevent sticking or tunnelling during low-velocity collisions.
* **Conservation Diagnostics (HUD):** Calculates instantaneous system momentum ($\sum \vert{}\mathbf{p}\vert{}$) and kinetic energy ($\sum E_k$) every frame to monitor numerical dissipation, damping, and drag.
* **Simulation Modes:**
  * **Billiards (Mode `P`):** Features standard 16-ball rack positioning, cue ball impulse charging via mouse click-and-drag, pocket detection, and side-basket collection.
  * **Particle Sandbox (Modes `A` / `M`):** Automatic or manual particle spawning with live UI controls for mouse attraction forces, aerodynamic drag, gravity toggles, and velocity vector overlays.

---

## Project Structure

```text
2d-physics-engine/
├── README.md
├── requirements.txt
├── .gitignore
└── src/
    ├── engine.py       # Physics mathematics, Circle entity, Button UI class
    └── main.py         # Pygame display loop, event handling, HUD, and modes
```

---

## Installation & Execution

### 1. Requirements
Ensure Python 3.8+ is installed. Install Pygame via pip:

```bash
pip install -r requirements.txt
```

### 2. Running the Simulation
Launch the entry point from the project root:

```bash
python src/main.py
```

When prompted in the terminal:
* Enter **`P`** for the interactive Billiards table.
* Enter **`A`** for an automatic particle sandbox.
* Enter **`M`** to manually configure particle counts, velocities, and radii.

---

## Controls

* **Billiards Mode:** Click and hold the left mouse button anywhere on screen to charge cue shot power; release to strike the cue ball.
* **Sandbox Mode:**
  * **Left Mouse Button (Hold & Drag):** Attracts and flings the nearest particle with a spring force.
  * **`D` Key:** Spawns a new particle at the cursor position.
  * **UI Buttons:** Click sidebar toggles to adjust mouse pull strength, aerodynamic drag, gravity, or display velocity indicator vectors.