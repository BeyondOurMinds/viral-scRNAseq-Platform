# <img width="100" height="100" alt="SCJosekiLogo" src="https://github.com/user-attachments/assets/8b281b9a-40d7-464c-a0d4-66f6eb123f48" /> SCJoseki: A Viral Single-Cell RNA-seq Analysis Platform

## About
SCJoseki is a user-friendly Plotly Dash web application for the analysis of single-cell RNA-seq datasets with additional support for viral datasets.

The application contains many of the standard modular workflows found in scRNA-seq pipelines, while addressing the current gaps of viral analysis functionality.

<img width="1121" height="510" alt="NewFlowBabe" src="https://github.com/user-attachments/assets/04fd3ee9-739b-4bd3-8c0c-9a51e59d5117" />


An overview of the application can be found on the first page whenever you load the application (or let's be honest, you can just look through the code to read it all before downloading). 
At current, the application only supports H5AD files or zipped 10x genomics cell ranger files.


<img width="1896" height="908" alt="Screenshot 2026-08-26 211800" src="https://github.com/user-attachments/assets/545abd10-0954-464d-a166-d4fd4d31a942" />


Almost every module offers some form of data visualisation, such as violin, bar, volcano, UMAP, and network plots

<img width="1892" height="913" alt="Screenshot 2026-08-26 214142" src="https://github.com/user-attachments/assets/8f5effd3-8f46-496b-b42c-397af7ed759d" />




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

