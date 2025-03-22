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

This architecture makes it easy to mock components for testing and to swap out implementations as needed.

## Current Status

The project is currently in early development with the following components implemented:

- **CommunicationPort**: Interface for communicating with FORTH systems
- **SerialAdapter**: Implementation of CommunicationPort for serial communication
- **ArchivistPort**: Interface for recording events (commands, responses, errors)
- **SQLiteArchivist**: Implementation of ArchivistPort that stores events in an SQLite database
- **ForthRepl**: Core REPL for interacting with FORTH systems

Next steps include:
- Implementing a GUI using guizero
- Adding more advanced debugging features
- Enhancing the archiving and analysis capabilities

## Getting Started

### Prerequisites

- Python 3.10 or higher
- A virtual environment (recommended)
- A Raspberry Pi Pico running FORTH (for actual usage)

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

### Running Tests

Run the tests using pytest:
```
python -m pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
