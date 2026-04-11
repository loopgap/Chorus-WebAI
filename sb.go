package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

func main() {
	if len(os.Args) < 2 {
		printUsage()
		return
	}

	command := os.Args[1]
	switch command {
	case "setup":
		setup()
	case "web":
		runPython("web_app.py")
	case "cli":
		runPython("main.py")
	case "check":
		check()
	case "test":
		runModule("pytest", "-v")
	case "help":
		printUsage()
	default:
		fmt.Printf("Unknown command: %s\n", command)
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println("ShadowBoard Management Tool")
	fmt.Println("Usage: go run sb.go <command>")
	fmt.Println("\nCommands:")
	fmt.Println("  setup   Initialize .venv, install dependencies and playwright")
	fmt.Println("  web     Start the Web UI Boardroom")
	fmt.Println("  cli     Start the CLI Expert Advisor")
	fmt.Println("  check   Run quality gate (ruff, pytest, perf_check)")
	fmt.Println("  test    Run unit tests (pytest)")
	fmt.Println("  help    Show this help message")
}

func getPythonExe() string {
	cwd, _ := os.Getwd()
	var relPath string
	if runtime.GOOS == "windows" {
		relPath = filepath.Join(".venv", "Scripts", "python.exe")
	} else {
		relPath = filepath.Join(".venv", "bin", "python")
	}
	return filepath.Join(cwd, relPath)
}

func runCommand(name string, args ...string) error {
	cmd := exec.Command(name, args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Stdin = os.Stdin
	return cmd.Run()
}

func runPython(script string, args ...string) {
	python := getPythonExe()
	allArgs := append([]string{script}, args...)
	if err := runCommand(python, allArgs...); err != nil {
		fmt.Printf("Error executing %s: %v\n", script, err)
		os.Exit(1)
	}
}

func runModule(module string, args ...string) {
	python := getPythonExe()
	allArgs := append([]string{"-m", module}, args...)
	if err := runCommand(python, allArgs...); err != nil {
		fmt.Printf("Error executing module %s: %v\n", module, err)
		os.Exit(1)
	}
}

func setup() {
	fmt.Println(">>> Setting up ShadowBoard environment...")
	
	// 1. Create venv if missing
	if _, err := os.Stat(".venv"); os.IsNotExist(err) {
		fmt.Println("Creating virtual environment...")
		if err := runCommand("python", "-m", "venv", ".venv"); err != nil {
			fmt.Printf("Failed to create venv: %v\n", err)
			os.Exit(1)
		}
	}

	// 2. Install requirements
	fmt.Println("Installing dependencies...")
	python := getPythonExe()
	if err := runCommand(python, "-m", "pip", "install", "--upgrade", "pip"); err != nil {
		fmt.Printf("Failed to upgrade pip: %v\n", err)
	}
	if err := runCommand(python, "-m", "pip", "install", "-r", "requirements.txt"); err != nil {
		fmt.Printf("Failed to install requirements: %v\n", err)
		os.Exit(1)
	}
	if err := runCommand(python, "-m", "pip", "install", "pytest", "ruff", "playwright"); err != nil {
		fmt.Printf("Failed to install dev tools: %v\n", err)
		os.Exit(1)
	}

	// 3. Install playwright browsers
	fmt.Println("Installing Playwright Chromium...")
	if err := runCommand(python, "-m", "playwright", "install", "chromium"); err != nil {
		fmt.Printf("Failed to install browsers: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("\n>>> Setup complete! You can now run 'go run sb.go web'")
}

func check() {
	fmt.Println(">>> Running Quality Gate...")
	
	fmt.Println("\n1. Running Ruff (static analysis)...")
	runModule("ruff", "check", ".")

	fmt.Println("\n2. Running Pytest (unit tests)...")
	// Use -q for quiet output in check mode
	runModule("pytest", "-q")

	fmt.Println("\n3. Running Performance Check...")
	runPython("perf_check.py")

	fmt.Println("\n>>> All quality gates passed!")
}
