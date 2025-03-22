# Testing Fonny

This document describes the testing approach and strategies used in the Fonny project.

## Testing Philosophy

Fonny follows a "baby steps" approach to development and testing, with a focus on:

1. Writing tests before or alongside code
2. Committing to Git after each passing test
3. Using a hexagonal architecture to facilitate testing
4. Testing at multiple levels (unit, integration, end-to-end)

## Test Structure

The tests are organized as follows:

```
tests/
├── e2e/               # End-to-end tests
│   └── test_forth_gui.py  # GUI tests with real hardware
├── helpers/           # Test helpers and utilities
│   └── tk_testing.py  # Utilities for testing guizero components
├── integration/       # Integration tests
└── unit/              # Unit tests
```

## Test Types

### Unit Tests

Unit tests focus on testing individual components in isolation, using mocks for dependencies when necessary. This is facilitated by the hexagonal architecture of Fonny, which defines clear interfaces (ports) that can be mocked.

### Integration Tests

Integration tests verify that multiple components work together correctly. For example, testing that the ForthRepl correctly interacts with the SerialAdapter and ArchivistPort implementations.

### End-to-End Tests

End-to-end tests verify the entire system works correctly from the user interface to the hardware. These tests:

1. Launch the actual Fonny GUI
2. Connect to a real Raspberry Pi Pico running FORTH
3. Send commands and verify responses
4. Test error handling

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

## Test Requirements

- Python 3.10 or higher
- pytest
- A Raspberry Pi Pico running FORTH (for end-to-end tests)
