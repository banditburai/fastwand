import platform
import urllib.request
import json
from pathlib import Path
import os
import sys
import subprocess
from platformdirs import user_cache_dir
import signal

def get_system_info():
    """Get system and architecture info"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        system = "macos"
    
    if machine == "x86_64":
        machine = "x64"
    elif machine == "aarch64":
        machine = "arm64"
        
    return system, machine

def handle_sigint(signum, frame, processes):
    """Gracefully handle SIGINT (Ctrl+C)"""
    print("\nSTATUS:Shutting down processes...", flush=True)
    for process in processes:
        if process and process.poll() is None:
            process.terminate()
            process.wait()
    print("DONE:true", flush=True)
    sys.exit(0)

def get_fastwand_version():
    """Get latest version of fastwand CLI"""
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/banditburai/fastwandCLI/releases/latest",
            headers={'User-Agent': 'fastwand'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read())["tag_name"]
    except Exception as e:
        return "v0.1.00"  # Updated fallback version

def install_fastwand(directory: Path) -> Path:
    """Download and install fastwand CLI"""
    system, machine = get_system_info()
    version = get_fastwand_version()
    
    filename = f"fastwand-{system}-{machine}"
    if system == "windows":
        filename += ".exe"
    
    url = f"https://github.com/banditburai/fastwandCLI/releases/download/{version}/{filename}"
    
    final_path = directory / filename
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'fastwand'})
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(final_path, 'wb') as f:
                f.write(response.read())
    except Exception as e:
        print(f"Error downloading fastwand CLI: {e}")
        if final_path.exists():
            final_path.unlink()
        raise
    
    # Make executable on Unix systems
    if system != "windows":
        os.chmod(final_path, 0o755)
    
    return final_path

def ensure_fastwand_installed() -> Path:
    """Ensure fastwand CLI is installed and return path"""
    cache_dir = Path(user_cache_dir("fastwand"))
    cache_dir.mkdir(exist_ok=True)
    
    cli_path = cache_dir / "fastwand"
    if not cli_path.exists():
        cli_path = install_fastwand(cache_dir)
    
    return cli_path

def run_command(directory: Path = Path(".")):
    """Run server with status updates to Go CLI"""
    try:
        print("STATUS:Building CSS...", flush=True)
        
        # Build CSS first
        subprocess.run([
            "./tailwindcss",
            "-i", "assets/input.css",
            "-o", "assets/output.css",
            "--minify"
        ], cwd=directory, check=True)
        
        # Start Python server
        print("STATUS:Starting Python server...", flush=True)
        server = subprocess.Popen(
            ["python", "main.py"], 
            cwd=directory
        )
        
        # Setup signal handler
        processes = [server]
        signal.signal(signal.SIGINT, lambda s, f: handle_sigint(s, f, processes))
        
        # Wait for server
        server.wait()
        print("DONE:true", flush=True)
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR:{e}", flush=True)
        sys.exit(1)

def watch_command(directory: Path = Path(".")):
    """Watch for changes and rebuild CSS with status updates to Go CLI"""
    try:
        print("STATUS:Starting Tailwind watch process...", flush=True)
        
        # Start Tailwind in watch mode
        tailwind = subprocess.Popen([
            "./tailwindcss",
            "-i", "assets/input.css",
            "-o", "assets/output.css",
            "--watch"
        ], cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Start Python server in parallel
        print("STATUS:Starting Python server...", flush=True)
        server = subprocess.Popen(
            ["python", "main.py"], 
            cwd=directory
        )
        
        # Setup signal handler
        processes = [tailwind, server]
        signal.signal(signal.SIGINT, lambda s, f: handle_sigint(s, f, processes))
        
        # Monitor Tailwind output while server runs
        while server.poll() is None:
            output = tailwind.stdout.readline()
            if output:
                msg = output.decode().strip()
                if "Change detected" in msg:
                    print("STATUS:Rebuilding CSS...", flush=True)
                elif "Done" in msg:
                    print("STATUS:CSS rebuilt successfully", flush=True)
                elif "Error" in msg:
                    print(f"ERROR:{msg}", flush=True)
                    handle_sigint(None, None, processes)
                    sys.exit(1)
        
        # Clean up if server exits
        handle_sigint(None, None, processes)
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR:{e}", flush=True)
        sys.exit(1)

def main():
    """Main CLI entrypoint"""
    cli = ensure_fastwand_installed()
    
    # Forward all arguments to the Go CLI
    try:
        subprocess.run([str(cli)] + sys.argv[1:], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()