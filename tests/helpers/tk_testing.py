"""
Helper functions for testing guizero applications.

This module provides utilities to interact with guizero components in tests:
- push(): Simulate button clicks
- type_in(): Enter text into TextBox components

These functions access the underlying Tkinter widgets to simulate user interactions,
allowing for automated testing of guizero applications.
"""
from guizero import PushButton, TextBox


def push(button: PushButton) -> None:
    """
    Simulate a button click in a guizero application.
    
    Args:
        button: The PushButton to click
    """
    button.tk.invoke()


def type_in(text_box: TextBox, text: str, position=None):
    """
    Type text into a TextBox in a guizero application.
    
    Args:
        text_box: The TextBox to type into
        text: The text to type
        position: The position to insert the text (default: end)
    """
    position = position or "end"
    text_box.tk.insert(position, text)
    if hasattr(text_box, "_command") and callable(text_box._command):
        text_box._command()
    text_box.tk.update()
