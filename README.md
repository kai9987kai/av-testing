# av-testing

A **safe antivirus testing harness** for validating endpoint/browser protections using standard, non-malicious test artifacts and checks.

This project provides a small Python CLI that can:

- Generate the standard **EICAR antivirus test file**
- Generate a **set of common EICAR variants** (plain, `.txt`, zip, nested zip)
- Open official **AMTSO security feature check** pages in your browser
- Print a local environment/system report
- Optionally download a file to disk for controlled testing workflows

> ⚠️ This repository is intended for **defensive/security validation** and lab testing.  
> The EICAR string is a **test signature**, not real malware, but your antivirus may quarantine/delete it immediately.

---

## Features

- ✅ **Safe AV validation** using the industry-standard EICAR test pattern
- ✅ **Multiple EICAR variants** for more realistic detection-path testing:
  - `eicar.com`
  - `eicar.com.txt`
  - `eicar_com.zip`
  - `eicarcom2.zip` (nested zip)
- ✅ **AMTSO browser checks** launcher (opens official test pages)
- ✅ **CLI-based workflow** (easy to automate in scripts)
- ✅ **Windows EXE build script** (PyInstaller one-file build)

---

## Repository Contents

- `safe_av_test_harness.py` — Main CLI script
- `build_safe_av_test_harness.ps1` — PowerShell build script for PyInstaller
- `safe-av-test-harness.spec` — PyInstaller spec file
- `eicar.com`, `eicar.com.txt`, `eicar_com.zip`, `eicarcom2.zip` — Pre-generated test artifacts

---

## How It Works

### 1) EICAR test generation
The script builds the EICAR test string from fragments in code (instead of embedding the full signature inline as a single literal), then writes it to disk as a test artifact.

### 2) ZIP / nested ZIP variants
To test archive scanning behavior, the harness can generate:
- a zipped EICAR file
- a nested zip containing the zipped EICAR file

### 3) AMTSO browser checks
The harness can open official AMTSO test pages in your default browser to verify browser/endpoint security features such as phishing protection and cloud lookup behavior.

### 4) Local system report
A lightweight report mode prints platform, Python version, executable path, CPU core count, and local timestamp.

---

## Requirements

- Python **3.x**
- Standard library only for the core script (no external packages required for runtime)

### Optional (for building a Windows `.exe`)
- `PyInstaller`

---

## Quick Start

### Run with Python (default behavior)
If you run the script with **no arguments**, it will:
1. print a local system report
2. write the **default EICAR test set** into the current directory

```bash
python safe_av_test_harness.py
