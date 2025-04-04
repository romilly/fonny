from guizero import App, Text, TextBox, PushButton, Box, TitleBox

from fonny.adapters.serial_adapter import SerialAdapter
from fonny.adapters.rqlite_archivist import RQLiteArchivist
from fonny.core.repl import ForthRepl
from queue import Empty


def is_ok(char):
    # skip ascii colour control chars
    return char in "\n\r" or ord(char) > 31


class ForthGui(App):
    """
    GUI application for interacting with a FORTH system.
    Uses guizero for the UI components.
    """

    def __init__(self, repl: ForthRepl, title="Fonny - FORTH REPL", width=1200, height=900, **kwargs):
        """
        Initialize the GUI application with a FORTH REPL.

        Args:
            repl: The FORTH REPL to use for communication
            title: The window title
            width: The window width
            height: The window height
            **kwargs: Additional arguments to pass to guizero.App
        """
        super().__init__(title=title, width=width, height=height, **kwargs)
        self._repl = repl

        # # Create a console archivist to capture responses
        # self._console_archivist = self._create_console_archivist()
        # self._repl.add_archivist(self._console_archivist)

        # Create the GUI components
        self._create_gui_components()

        # Set up event handler for when the app is closed
        self.when_closed = self.cleanup

        # Set up a repeating task to process the character queue
        self.repeat(50, self._process_character_queue)  # Check every 50ms

        # Buffer for accumulating characters
        self._char_buffer = ""

    def _process_character_queue(self):
        """
        Process characters from the queue on the main thread.
        This avoids threading issues when updating the GUI.
        """

        # Process all available characters in the queue
        while self._repl.character_queue.qsize() > 0:
            try:
                char = self._repl.character_queue.get_nowait()
                if is_ok(char):
                # Add the character to our buffer
                    self._char_buffer += char
                    self.update()
                # If we have a newline or carriage return, update the display
                if char == '\n' or char == '\r':
                    if self._char_buffer.strip():  # Only append non-empty lines
                        # Use the same approach as append_to_output
                        self._output.value += self._char_buffer
                        # Scroll to the bottom
                        self._output.tk.see("end")
                    self._char_buffer = ""  # Reset the buffer

                self._repl.character_queue.task_done()
            except Empty:
                break  # No more items in queue

    def _create_gui_components(self):
        """Create the GUI components."""
        # Connection controls
        connection_box = TitleBox(self, text="Connection")
        port_box = Box(connection_box, align="left")
        Text(port_box, text="Port:", align="left")
        self._port_input = TextBox(port_box, text="/dev/ttyACM0", width=20, align="left")
        self._connect_button = PushButton(
            connection_box,
            text="Connect",
            command=self._toggle_connection,
            align="right"
        )

        # Output display
        output_box = TitleBox(self, text="Output")
        self._output = TextBox(
            output_box,
            text="",
            multiline=True,
            height="fill",
            width="fill",
            scrollbar=True
        )
        self._output.bg = "black"
        self._output.text_color = "white"

        # Command input
        input_box = TitleBox(self, text="Command")
        command_container = Box(input_box, align="left", width="fill")
        self._command_input = TextBox(
            command_container,
            text="",
            width="fill",
            align="left",
            multiline=True,
            height=6,
            scrollbar=True
        )
        self._command_input.when_key_pressed = self._handle_key_press
        self._send_button = PushButton(
            input_box,
            text="Send",
            command=self._send_command,
            align="right"
        )

    def _toggle_connection(self):
        """Toggle the _connection to the FORTH system."""
        if self._repl._comm_port.is_connected():
            self._repl.stop()
            self._connect_button.text = "Connect"
            self.append_to_output("Disconnected from FORTH system")
        else:
            # Update the port in case it was changed
            self._repl._comm_port._port = self._port_input.value

            if self._repl.start():
                self._connect_button.text = "Disconnect"
                self.append_to_output("Connected to FORTH system")
            else:
                self.append_to_output("Failed to connect to FORTH system")

    def _send_command(self):
        """Send the command to the FORTH system."""
        command = self._command_input.value
        if not command:
            return

        # Check if we're connected first
        if not self._repl._comm_port.is_connected():
            self.append_to_output("Error: Not connected to FORTH system. Please connect first.")
            return

        try:
            self._repl.process_command(command)
        except Exception as e:
            self.append_to_output(f"Error: {e}")

        # Clear the command input
        self._command_input.value = ""

    def _handle_key_press(self, event):
        """Handle key press events in the command input."""
        if event.key == "Return":
            self._send_command()

    def append_to_output(self, text):
        """Append text to the output display."""
        self._output.value += text + "\n"
        # Scroll to the bottom
        self._output.tk.see("end")

    def clear_output(self):
        self._output.value = ""

    def cleanup(self):
        """Clean up resources when the application is closed."""
        if self._repl._comm_port.is_connected():
            self._repl.stop()
        self.destroy()  # Properly close the application window


def run():
    """
    Run the FORTH GUI application.
    """

    # Create a ForthRepl instance
    archivist = RQLiteArchivist(port=4001)
    repl = ForthRepl(archivist)
    
    # Create a SerialAdapter and set it as the communication port
    # The character handler will be set when the SerialAdapter is created
    serial_adapter = SerialAdapter(character_handler=repl, port='/dev/ttyACM0')
    repl.set_communication_port(serial_adapter)
    
    # Create and display the GUI
    app = ForthGui(repl)
    app.display()
