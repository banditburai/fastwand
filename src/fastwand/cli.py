import platform
import urllib.request
import json
from pathlib import Path
import os
import subprocess
import tarfile
import sys
from platformdirs import user_cache_dir
from .templates import TEMPLATES, TEMPLATES_DAISY

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

def get_gum_version():
    """Get latest version of gum"""
    with urllib.request.urlopen("https://api.github.com/repos/charmbracelet/gum/releases/latest") as response:
        return json.loads(response.read())["tag_name"]

def install_gum(directory: Path) -> Path:
    """Download and install gum"""
    system, machine = get_system_info()
    version = get_gum_version()
    
    # Map to gum's naming convention
    if system == "macos":
        system = "darwin"
    
    filename = f"gum_{version[1:]}_{system}_{machine}.tar.gz"  # Remove 'v' prefix
    url = f"https://github.com/charmbracelet/gum/releases/download/{version}/{filename}"
    
    # Download and extract gum
    temp_path = directory / filename
    final_path = directory / "gum"
        
    urllib.request.urlretrieve(url, temp_path)
    
    with tarfile.open(temp_path) as tar:
        tar.extract("gum", directory)
    
    os.chmod(final_path, 0o755)
    temp_path.unlink()
    
    return final_path

def ensure_gum_installed() -> Path:
    """Ensure gum is installed and return path to binary"""
    cache_dir = Path(user_cache_dir("fastwand"))
    cache_dir.mkdir(exist_ok=True)
    
    gum_path = cache_dir / "gum"
    if not gum_path.exists():
        install_gum(cache_dir)
    
    return gum_path

def run_gum(gum_path: Path, *args, **kwargs):
    """Helper to run gum commands"""
    result = subprocess.run(
        [str(gum_path)] + list(args),
        capture_output=True,
        text=True,
        **kwargs
    )
    return result.stdout.strip()

def get_tailwind_only_version():
    """Get latest version of vanilla Tailwind CSS"""
    with urllib.request.urlopen("https://api.github.com/repos/tailwindlabs/tailwindcss/releases/latest") as response:
        return json.loads(response.read())["tag_name"]

def get_tailwind_daisy_version():
    """Get latest version of Tailwind CSS with DaisyUI"""
    with urllib.request.urlopen("https://api.github.com/repos/dobicinaitis/tailwind-cli-extra/releases/latest") as response:
        return json.loads(response.read())["tag_name"]

def install_tailwind(directory: Path, use_daisy: bool, gum: Path) -> Path:
    """Download and install tailwindcss"""
    system, machine = get_system_info()
    
    if use_daisy:
        version = get_tailwind_daisy_version()
        filename = f"tailwindcss-extra-{system}-{machine}"
        url_base = "https://github.com/dobicinaitis/tailwind-cli-extra/releases/download"
        run_gum(gum, "style", "--foreground", "99",
            f"Installing Tailwind CSS CLI with DaisyUI ({version})...")        
    else:
        version = get_tailwind_only_version()
        filename = f"tailwindcss-{system}-{machine}"
        url_base = "https://github.com/tailwindlabs/tailwindcss/releases/download"
        run_gum(gum, "style", "--foreground", "99",
            f"Installing Tailwind CSS CLI ({version})...")        
    
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
        
    return final_path

def style_text(gum_path: Path, text: str, **style_args):
    """Helper for styled text"""
    args = []
    for k, v in style_args.items():
        args.extend([f"--{k.replace('_', '-')}", str(v)])
    return run_gum(gum_path, "style", *args, text)

def show_spinner(gum_path: Path, title: str, action):
    """Show spinner while executing action"""
    with subprocess.Popen([
        str(gum_path), "spin",
        "--spinner", "dot",
        "--title", title
    ]):
        return action()

def init(directory: Path):
    """Initialize a new FastHTML + Tailwind project"""
    gum = ensure_gum_installed()
    directory = Path(directory).resolve()
    
    # Welcome message
    run_gum(gum, "style",
        "--border", "normal",
        "--margin", "1",
        "--padding", "1 2",
        "--border-foreground", "212",
        "Welcome to FastWand - FastHTML + Tailwind made easy!"
    )
    
    # Project setup
    directory.mkdir(exist_ok=True)
    
    # Framework choice with nice formatting
    run_gum(gum, "style", "--foreground", "99", "\nChoose your UI framework:")
    framework = run_gum(gum, "choose",
        "🌼 Tailwind CSS with DaisyUI",
        "🔷 Vanilla Tailwind CSS"
    )
    use_daisy = "DaisyUI" in framework
    
    # Install tailwind with spinner
    tailwind_path = show_spinner(gum, "Installing Tailwind CSS...", 
        lambda: install_tailwind(directory, use_daisy, gum))
    
    # Initialize tailwind
    subprocess.run([str(tailwind_path), "init"], cwd=directory, check=True)
    
    # Create files with progress
    templates = TEMPLATES_DAISY if use_daisy else TEMPLATES
    for file_path, content in templates.items():
        full_path = directory / file_path
        full_path.parent.mkdir(exist_ok=True)
        run_gum(gum, "style", "--foreground", "99", f"Creating {file_path}...")
        full_path.write_text(content)
    
    # Success message
    run_gum(gum, "style",
        "--border", "double",
        "--margin", "1",
        "--padding", "1",
        "--border-foreground", "57",
        "✨ Setup complete!"
    )
    
    if use_daisy:
        cmd = style_text(gum, "fastwand run", 
            foreground="yellow")
        print(f"\nRun: {cmd}")
    
    print("\nThen either:")
    watch_cmd = style_text(gum, "fastwand watch", foreground="cyan")
    run_cmd = style_text(gum, "fastwand run", foreground="cyan")
    print(f"1. {watch_cmd} - Start development mode")
    print(f"2. {run_cmd}   - Build and serve")


def watch(directory: Path):
    """Start Tailwind watch mode for development"""
    gum = ensure_gum_installed()
    
    # Welcome message
    run_gum(gum, "style",
        "--border", "normal",
        "--margin", "1",
        "--padding", "1 2",
        "--border-foreground", "99",
        "Starting Tailwind watch mode..."
    )
    
    # Note about running server
    run_gum(gum, "style",
        "--foreground", "212",
        "--italic",
        "NOTE: Run 'python main.py' in a separate terminal"
    )
    
    # Resolve absolute path
    directory = Path(directory).resolve()
    tailwind_path = directory / "tailwindcss"
    
    # Check if tailwindcss exists with nice error
    if not tailwind_path.exists():
        run_gum(gum, "style",
            "--foreground", "196",  # Red color
            "--border", "rounded",
            "--padding", "1",
            f"Error: Tailwind executable not found at {tailwind_path}\nDid you run 'fastwand init' first?"
        )        
    
    try:
        subprocess.run([
            str(tailwind_path),
            "-i", "assets/input.css",
            "-o", "assets/output.css",
            "--watch"
        ], cwd=directory)
    except KeyboardInterrupt:
        run_gum(gum, "style",
            "--foreground", "99",
            "\nStopping watch mode..."
        )
        sys.exit(0)

def run(directory: Path):
    """Build minified CSS and run the Python server"""
    gum = ensure_gum_installed()
    
    # Welcome message
    run_gum(gum, "style",
        "--border", "normal",
        "--margin", "1",
        "--padding", "1 2",
        "--border-foreground", "212",
        "Building CSS and starting server..."
    )
    
    # Resolve absolute path
    directory = Path(directory).resolve()
    tailwind_path = directory / "tailwindcss"
    
    # Check if tailwindcss exists with nice error
    if not tailwind_path.exists():
        run_gum(gum, "style",
            "--foreground", "196",  # Red color
            "--border", "rounded",
            "--padding", "1",
            f"Error: Tailwind executable not found at {tailwind_path}\nDid you run 'fastwand init' first?"
        )
        sys.exit(1)
    
    # Build CSS with spinner
    try:
        show_spinner(gum, "Building CSS...", lambda: subprocess.run([
            str(tailwind_path),
            "-i", "assets/input.css",
            "-o", "assets/output.css",
            "--minify"
        ], cwd=directory, check=True))
        
        # Success message
        run_gum(gum, "style",
            "--foreground", "99",
            "CSS built successfully!"
        )
        
        # Start server message
        run_gum(gum, "style",
            "--foreground", "212",
            "\nStarting server..."
        )
        
        # Run server with proper signal handling
        server_process = subprocess.Popen(["python", "main.py"], cwd=directory)
        try:
            server_process.wait()
        except KeyboardInterrupt:
            run_gum(gum, "style",
                "--foreground", "99",
                "\nShutting down server..."
            )
            server_process.terminate()
            server_process.wait()
            
    except subprocess.CalledProcessError:
        run_gum(gum, "style",
            "--foreground", "196",
            "--border", "rounded",
            "--padding", "1",
            "Error: Failed to build CSS"
        )
        sys.exit(1)

def main():
    """Main CLI entrypoint"""
    if len(sys.argv) < 2:
        print("Usage: fastwand [init|watch|run]")
        sys.exit(1)
    
    command = sys.argv[1]
    directory = Path(sys.argv[2] if len(sys.argv) > 2 else ".")
    
    if command == "init":
        init(directory)
    elif command == "watch":
        watch(directory)
    elif command == "run":
        run(directory)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()