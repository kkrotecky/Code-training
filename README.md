# My Programming & Cybersecurity Training Repository
*Learning Python, Bash, and security fundamentals through bite‑size projects.*

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Table of Contents
- [Project Structure](#project-structure)
- [Learning Areas](#learning-areas)
  - [Python Programming](#python-programming)
  - [Cybersecurity](#cybersecurity)
  - [Bash Scripting](#bash-scripting)
- [Projects](#projects)
  - [Shopping Cart Application](#shopping-cart-application)
  - [Text‑Based Games](#text-based-games)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Project Structure
```
Test/
├─ shop_app/
│  ├─ shopping_app.py
│  ├─ items.csv
│  ├─ mailing.py
│  └─ README.md
├─ games/
│  ├─ basic_text_game.py
│  └─ dice_text_game.py
└─ scripts/
   ├─ tuple.py
   ├─ simple_calculator.py
   ├─ numbers.py
   └─ lists.py
```

## Learning Areas

### Python Programming
- **GUI Development** – Tkinter, event handling, Sun Valley theme
- **Object‑Oriented Programming** – classes, inheritance, polymorphism
- **File Operations** – CSV, JSON, path handling

### Cybersecurity
- **Secure Coding Practices** – environment variables, credential handling, input validation
- **Email Security** – SMTP, secure notifications, password protection

### Bash Scripting
- File‑system navigation, automation, system commands

## Projects

### Shopping Cart Application
A Tkinter‑based GUI that demonstrates:
- User profile management
- Shipping calculation
- Email notifications (via `mailing.py`)
- Simple CSV‑based “database”

### Text‑Based Games
Console games that focus on:
- User input handling
- Game‑loop logic
- Score tracking

## Getting Started

### Prerequisites
- Python 3.11+ (the repo was created with 3.13)
- `pip` for optional dependencies

### Installation (optional)
```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows
# source .venv/bin/activate   # macOS / Linux

# If you later add a requirements.txt, install with:
# pip install -r requirements.txt
```

### Running examples
```bash
# Play the dice game
python Test/games/dice_text_game.py

# Use the calculator
python Test/scripts/simple_calculator.py

# Launch the shop GUI
python Test/shop_app/shopping_app.py
```

## Contributing
Contributions are welcome! Please:
- Follow the existing code style (`ruff`/`black` recommended).
- Provide a concise PR title and description.
- Add docstrings for new functions/classes.

## License
This repository is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

## Contact
Feel free to open an issue or reach out via email (your-email@example.com).