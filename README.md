# Fonny

Fonny is a FORTH-oriented tool inspired by Thonny, designed to interact with a running FORTH on a Raspberry Pi Pico.

## Project Goals

The primary goals of Fonny are:

1. Provide a user-friendly interface for interacting with FORTH systems, particularly those running on Raspberry Pi Pico microcontrollers
2. Enable easy monitoring and debugging of FORTH code execution
3. Archive and analyze user commands and system responses
4. Offer a modern GUI experience for FORTH programming

## Architecture

Fonny follows a hexagonal architecture pattern, which allows for easy testing and flexibility:

- **Core**: Contains the main business logic, including the REPL (Read-Eval-Print Loop)
- **Ports**: Define interfaces for external interactions (communication, archiving)
- **Adapters**: Implement the port interfaces for specific technologies (serial communication, SQLite)
- **GUI**: Provides a graphical user interface using guizero

This architecture makes it easy to mock components for testing and to swap out implementations as needed.

## Current Status

The project is currently in active development with the following components implemented:

- **CommunicationPort**: Interface for communicating with FORTH systems
- **SerialAdapter**: Implementation of CommunicationPort for serial communication
- **ArchivistPort**: Interface for recording events (commands, responses, errors)
- **SQLiteArchivist**: Implementation of ArchivistPort that stores events in an SQLite database
- **ForthRepl**: Core REPL for interacting with FORTH systems
- **ForthGui**: Graphical user interface for interacting with the FORTH system

## Getting Started

### Prerequisites

- Python 3.10 or higher
- A virtual environment (recommended)
- A Raspberry Pi Pico running FORTH (for actual usage)
- guizero package for the GUI

### Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the GUI

To run the Fonny GUI application:

```bash
cd /path/to/fonny
source venv/bin/activate
cd src
python -m fonny.run_gui
```

The GUI provides:
- Connection controls to connect to your FORTH system
- Command input for sending FORTH commands
- Output display for viewing responses and errors

### Running Tests

Test strategy is described in [testing.md](docs/testing.md)

Run the tests using pytest:
```
python -m pytest
```

#### End-to-End Tests

The project includes end-to-end tests that verify the GUI functionality with an actual Raspberry Pi Pico running FORTH. These tests:

1. Connect to the Pico
2. Send FORTH commands
3. Verify responses
4. Test error handling

To run the end-to-end tests specifically:
```
python -m pytest tests/e2e/test_forth_gui.py -v
```

Note: End-to-end tests require a Raspberry Pi Pico connected to your computer and running a FORTH system.

#### Test Helpers

The `tests/helpers` directory contains utilities to assist with testing:

- `tk_testing.py`: Functions for interacting with guizero components in tests
  - `push()`: Simulate button clicks
  - `type_in()`: Enter text into TextBox components

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
