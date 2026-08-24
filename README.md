# SCJoseki
SCJoseki is a user-friendly Plotly Dash web application for the analysis of single-cell RNA-seq datasets with additional support for viral datasets

## Installation
SCJoseki can be installed in 3 different ways:

1. The EXE available within the GitHub releases.
2. Through Docker
```bash
docker pull beyondourminds/scjoseki:latest
```
3. Via PIP
   a. Clone the repo:
   ```bash
   git clone https://github.com/BeyondOurMinds/SCJoseki 
   ```
   b. switch to current directory:
   ```bash
   cd SCJoseki
   ```
   c. Create a virtual environment:
   ```bash
   python.exe -m venv .venv
   ```
   d. Activate the virtual environment:
   
   **Windows (PowerShell):**
    ```powershell
    .venv\Scripts\Activate.ps1
    ```
    
    **Windows (Command Prompt):**
    ```cmd
    .venv\Scripts\activate.bat
    ```
    
    **Linux/Mac:**
    ```bash
    source .venv/bin/activate
    ```

    e. Install the package:
    ```bash
    pip install .
    ```
    

## How To Run
1. **EXE File**

Double-click the file, and it runs!

2. **Docker**

To run with Docker, follow the functional example below. -v mounts a location for exported files. The code below will create a folder, if one does not already exist, in your current working directory called "exports", where the outputs will be saved. To choose/create a different export folder, update the path before the semicolon (:). 
```bash
docker run --rm -p 8050:8050 -e CHROME_BIN=/usr/bin/chromium -v "${PWD}/exports:/exports" scjoseki
```
Once run, navigate to https://localhost:8050 to see the running app.

3. Pip

Within the package's root directory, run:
```bash
scjoseki
```

## Prerequisites:
Python < 3.14

