#!/usr/bin/env python
# coding: utf-8

from fonny.adapters.serial_adapter import SerialAdapter
from fonny.core.repl import ForthRepl


def main():
    """
    Main entry point for the FORTH REPL application.
    """
    # Create the serial adapter
    adapter = SerialAdapter()
    
    # Create the REPL
    repl = ForthRepl(adapter)
    
    # Run the interactive session
    repl.run_interactive_session()


if __name__ == "__main__":
    main()
