import platform
import urllib.request
import json
from pathlib import Path
import typer
import os
import subprocess

app = typer.Typer()

def get_system_info():
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        system = "macos"
    
    if machine == "x86_64":
        machine = "x64"
    elif machine == "aarch64":
        machine = "arm64"
        
    return system, machine

def get_tailwind_only_version():
    """Get latest version of vanilla Tailwind CSS"""
    with urllib.request.urlopen("https://api.github.com/repos/tailwindlabs/tailwindcss/releases/latest") as response:
        return json.loads(response.read())["tag_name"]

def get_tailwind_daisy_version():
    """Get latest version of Tailwind CSS with DaisyUI"""
    with urllib.request.urlopen("https://api.github.com/repos/dobicinaitis/tailwind-cli-extra/releases/latest") as response:
        return json.loads(response.read())["tag_name"]

def install_tailwind(directory: Path, use_daisy: bool) -> Path:
    """Download and install tailwindcss"""
    system, machine = get_system_info()
    
    if use_daisy:
        version = get_tailwind_daisy_version()
        filename = f"tailwindcss-extra-{system}-{machine}"
        url_base = "https://github.com/dobicinaitis/tailwind-cli-extra/releases/download"
        print(f"Installing Tailwind CSS CLI with DaisyUI ({version})...")
    else:
        version = get_tailwind_only_version()
        filename = f"tailwindcss-{system}-{machine}"
        url_base = "https://github.com/tailwindlabs/tailwindcss/releases/download"
        print(f"Installing Tailwind CSS CLI ({version})...")
    
    if system == "windows":
        filename += ".exe"
    
    # Download with original filename
    url = f"{url_base}/{version}/{filename}"
    temp_path = directory / filename
    final_path = directory / "tailwindcss"
    
    # Download Tailwind CSS
    urllib.request.urlretrieve(url, temp_path)
    
    # Make executable
    if os.name != 'nt':  # not Windows
        os.chmod(temp_path, 0o755)
    
    # Rename to tailwindcss
    if final_path.exists():
        final_path.unlink()
    temp_path.rename(final_path)
    
    print("Installation successful!")
    return final_path

@app.command()
def init(directory: Path = typer.Argument(".", help="Directory to initialize the project in")):
    """Initialize a new FastHTML + Tailwind project"""
    from .templates import TEMPLATES, TEMPLATES_DAISY
    
    directory = Path(directory).resolve()
    directory.mkdir(exist_ok=True)
    
    # Ask about DaisyUI
    use_daisy = typer.confirm("Would you like to include DaisyUI?", default=True)
    
    # Install tailwindcss
    tailwind_path = install_tailwind(directory, use_daisy)
    
    # Initialize tailwind and create files
    print("Initializing Tailwind CSS...")
    subprocess.run([str(tailwind_path), "init"], cwd=directory, check=True)
    
    # Create template files using appropriate templates
    templates = TEMPLATES_DAISY if use_daisy else TEMPLATES
    for file_path, content in templates.items():
        full_path = directory / file_path
        full_path.parent.mkdir(exist_ok=True)
        print(f"Creating {file_path}...")
        full_path.write_text(content)
    
    if use_daisy:
        print("\nSetup complete!")
        print("Now run: npm install -D @tailwindcss/typography daisyui")
    else:
        print("\nSetup complete!")
    
    print("Then either:")
    print("1. Start a watcher with: fastwand watch")
    print("2. Or minify your CSS and start the server with: fastwand run")

@app.command()
def watch(directory: Path = typer.Argument(".", help="Directory to watch for changes")):
    """Start Tailwind watch mode for development"""
    print("Starting Tailwind watch mode...")
    print("NOTE: Run 'python main.py' in a separate terminal")
    
    # Resolve absolute path
    directory = Path(directory).resolve()
    tailwind_path = directory / "tailwindcss"
    
    # Check if tailwindcss exists
    if not tailwind_path.exists():
        raise FileNotFoundError(f"Tailwind executable not found at {tailwind_path}. Did you run 'fastwand init' first?")
    
    subprocess.run([
        str(tailwind_path),
        "-i", "assets/input.css",
        "-o", "assets/output.css",
        "--watch"
    ], cwd=directory)

@app.command()
def run(directory: Path = typer.Argument(".", help="Directory to run the project in")):
    """Build minified CSS and run the Python server"""
    print("Building CSS and starting server...")
    
    # Resolve absolute path
    directory = Path(directory).resolve()
    tailwind_path = directory / "tailwindcss"
    
    # Check if tailwindcss exists
    if not tailwind_path.exists():
        raise FileNotFoundError(f"Tailwind executable not found at {tailwind_path}. Did you run 'fastwand init' first?")
    
    # Build CSS
    subprocess.run([
        str(tailwind_path),
        "-i", "assets/input.css",
        "-o", "assets/output.css",
        "--minify"
    ], cwd=directory, check=True)
    
    # Run server
    subprocess.run(["python", "main.py"], cwd=directory)

def main():
    app()

if __name__ == "__main__":
    main()