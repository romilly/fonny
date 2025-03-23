# Testing Fonny

This document describes the testing approach and strategies used in the Fonny project.

## Testing Philosophy

Fonny follows a "baby steps" approach to development and testing, with a focus on:

1. Writing tests before or alongside code
2. Committing to Git after each passing test
3. Using a hexagonal architecture to facilitate testing
4. Testing at multiple levels (unit, integration, end-to-end)
5. Preferring real implementations over mocks when practical
6. Creating explicit test doubles instead of using mocking libraries
7. Clearly separating unit tests from integration tests

## Test Structure

The tests are organized as follows:

```
tests/
├── e2e/               # End-to-end tests
│   └── test_forth_gui.py  # GUI tests with real hardware
├── helpers/           # Test helpers and utilities
│   └── tk_testing.py  # Utilities for testing guizero components
├── integration/       # Integration tests
│   ├── test_serial_adapter.py  # Tests using real hardware connections
│   └── test_serial_adapter_integration.py  # Additional integration tests
└── unit/              # Unit tests
```

## Test Types

### Unit Tests

Unit tests focus on testing individual components in isolation, using test doubles for dependencies when necessary. This is facilitated by the hexagonal architecture of Fonny, which defines clear interfaces (ports) that can be implemented by test doubles.

Key principles for unit tests:
- Create proper test doubles (with "Mock" prefix) that implement the required interfaces
- Avoid using mocking libraries like MagicMock which can lead to brittle tests
- Focus on testing behavior rather than implementation details

### Integration Tests

Integration tests verify that multiple components work together correctly. For example, testing that the ForthRepl correctly interacts with the SerialAdapter and ArchivistPort implementations.

The SerialAdapter tests have been moved from unit tests to integration tests, as they should test with a real Pico device rather than using mocks. These tests:
1. Use a real connection to a Pico device at `/dev/ttyACM0`
2. Are skippable with a pytest marker if the Pico is not connected
3. Test sending Forth commands and verify the responses

### Communication Interface Simplification

The CommunicationPort interface has been simplified to focus on the character-by-character processing approach:

1. The `receive_response` method has been removed from the CommunicationPort interface
2. SerialAdapter now only implements the essential methods: connect, disconnect, send_command, and is_connected
3. Character processing is handled directly via the CharacterHandlerPort interface
4. This simplification aligns with the project's preference for direct, real-time character processing over batch response handling

### End-to-End Tests

End-to-end tests verify the entire system works correctly from the user interface to the hardware. These tests:

1. Launch the actual Fonny GUI
2. Connect to a real Raspberry Pi Pico running FORTH
3. Send commands and verify responses
4. Test error handling

#### Threading in GUI Tests

The end-to-end GUI tests use a hybrid approach for communication between the background serial reading thread and the GUI thread:

1. SerialAdapter reads characters from the serial port in a background thread
2. Characters are directly passed to the ForthRepl's handle_character method
3. ForthRepl places these characters in a thread-safe queue
4. The GUI polls this queue on the main thread using guizero's `repeat()` method
5. Characters are accumulated in a buffer and displayed when complete lines are received
6. The GUI calls update() after each character to ensure timely display updates

This approach ensures all GUI updates happen on the main thread, avoiding the "main thread is not in main loop" error, while maintaining a clean separation between the communication layer and the GUI.

## Running Tests

### All Tests

To run all tests:

```bash
python -m pytest
```

### Specific Test Categories

To run specific categories of tests:

```bash
# Run end-to-end tests
python -m pytest tests/e2e/

# Run integration tests
python -m pytest tests/integration/

# Run unit tests
python -m pytest tests/unit/

# Run a specific test file
python -m pytest tests/e2e/test_forth_gui.py

# Run with verbose output
python -m pytest tests/e2e/test_forth_gui.py -v
```

## Test Helpers

### tk_testing.py

This module provides utilities for testing guizero components:

- `push(button)`: Simulates clicking a PushButton
- `type_in(text_box, text, position)`: Types text into a TextBox

Example usage:

```python
from tests.helpers.tk_testing import push, type_in

# Click a button
push(gui._connect_button)

# Type text into a TextBox
type_in(gui._command_input, "2 2 + .")
```

## Writing New Tests

When writing new tests for Fonny, follow these guidelines:

1. Place tests in the appropriate directory based on test type
2. Use descriptive test method names that explain what is being tested
3. Include docstrings that describe the test's purpose
4. For GUI tests, use the helper functions in tk_testing.py
5. For end-to-end tests, ensure a Raspberry Pi Pico is connected and properly set up
6. When creating mock classes, use the "Mock" prefix (e.g., MockCharacterHandler) for clarity
7. Prefer real implementations over mocks when practical

## Test Requirements

- Python 3.10 or higher
- pytest
- A Raspberry Pi Pico running FORTH (for integration and end-to-end tests)
