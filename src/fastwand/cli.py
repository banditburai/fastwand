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

def get_tailwind_version():
    with urllib.request.urlopen("https://api.github.com/repos/dobicinaitis/tailwind-cli-extra/releases/latest") as response:
        return json.loads(response.read())["tag_name"]

def download_file(url: str, dest_path: Path):
    urllib.request.urlretrieve(url, dest_path)
    if os.name != 'nt':  # not Windows
        os.chmod(dest_path, 0o755)

def run_tailwind_init(directory: Path):
    """Run tailwindcss init in the specified directory"""
    tailwind_path = directory / "tailwindcss"
    subprocess.run([str(tailwind_path), "init"], cwd=directory, check=True)

@app.command()
def init(directory: Path = typer.Argument(".", help="Directory to initialize the project in")):
    """Initialize a new FastHTML + Tailwind + DaisyUI project"""
    from .templates import TEMPLATES
    
    directory = Path(directory)
    directory.mkdir(exist_ok=True)
    
    # Create assets directory
    assets_dir = directory / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Download and setup tailwindcss
    system, machine = get_system_info()
    version = get_tailwind_version()
    filename = f"tailwindcss-extra-{system}-{machine}"
    if system == "windows":
        filename += ".exe"
        
    url = f"https://github.com/dobicinaitis/tailwind-cli-extra/releases/download/{version}/{filename}"
    tailwind_path = directory / "tailwindcss"
    
    print(f"Downloading Tailwind CSS CLI ({version})...")
    download_file(url, tailwind_path)
    
    # Initialize tailwind
    print("Initializing Tailwind CSS...")
    run_tailwind_init(directory)
    
    # Create template files
    for file_path, content in TEMPLATES.items():
        full_path = directory / file_path
        full_path.parent.mkdir(exist_ok=True)
        full_path.write_text(content)
        
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Run: uv pip install python-fasthtml")
    print("2. Run: npm install -D @tailwindcss/typography daisyui")
    print("3. Run: fastwand watch")
    print("4. In another terminal, run: python main.py")

@app.command()
def watch(directory: Path = typer.Argument(".", help="Directory to watch for changes")):
    """Start Tailwind watch mode for development"""
    print("Starting Tailwind watch mode...")
    print("NOTE: Run 'python main.py' in a separate terminal")
    
    tailwind_path = directory / "tailwindcss"
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
    
    # Build CSS
    tailwind_path = directory / "tailwindcss"
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