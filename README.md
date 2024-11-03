# FastWand

A CLI tool to initialize FastHTML + Tailwind + DaisyUI projects. FastWand automatically downloads and installs the Tailwind CSS CLI bundled with DaisyUI for your operating system and architecture.

⚠️ **ALPHA STATUS**: This project is in early development. Expect bugs and breaking changes.

## Prerequisites

- Python 3.11 or higher

## Installation

    pip install fastwand

## Usage

### Initialize a New Project

    fastwand init [DIRECTORY]

This will:
1. Download the appropriate Tailwind CLI and DaisyUI plugin for your system
2. Create a basic FastHTML project structure
3. Set up Tailwind CSS with DaisyUI

### Development Mode
Run these commands in separate terminal windows:

    # Terminal 1: Watch for CSS changes
    fastwand watch

    # Terminal 2: Run the Python server
    python main.py

### Production Mode
Build the minified CSS and run the server in a single command:

    fastwand run

This command:
1. Builds a minified version of your CSS for better performance
2. Automatically starts the Python server (main.py)


## System Compatibility

Automatically detects your operating system and architecture, supporting:
- Linux (x64, arm64, armv7)
- macOS (x64, arm64)
- Windows (x64, arm64)

## Known Issues

- This is an alpha release - functionality may be incomplete or buggy
- Error handling is minimal
- Documentation is work in progress

## Contributing

This project is in active development. Issues and pull requests are welcome!

## License

MIT