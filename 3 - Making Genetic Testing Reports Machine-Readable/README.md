# Making Genetic Testing Reports Machine-Readable

## Intro

Genetic-Report-PDF-Extraction is a program for extracting data from Genetic Testing Reports that are in PDF form.  
Instead of manually extracting the data to a spreadsheet, this program automates it. All you need to do is input what PDFs and what CSV to extract to.

It takes on average 1.82 minutes to complete 18 reports!

It uses [pdfplumber](https://github.com/jsvine/pdfplumber) to extract text and tables from Genetic Testing PDFs. It then uses this extracted text to extract key data and output it to a CSV file.

**Note:** Currently only supports Invitae Reports

## Table of Contents

- [Requirements](README.md#Requirements)
- [Installation](README.md#Installation)
- [Features](README.md#Features)
- [Usage](README.md#Usage)
- [Files](README.md#Files)

## Requirements

- Python 3.10
- pdfplumber v0.7.6

## Installation

1. Download the program using the command

```bash
git clone https://github.com/PRISM-SING-HEALTH/2023-NCP-Projects/
```

2. Move to the project directory

```bash
cd 2023-NCP-Projects/3\ -\ Making\ Genetic\ Testing\ Reports\ Machine-Readable/
```

3. Install requirements

```bash
pip3 install -r requirements.txt
```

4. Run the program

```bash
python3 main.py
```

## Features

Current Features:
- Extracts key data from Invitae Diagnostic Testing Reports 
- Extracts key data from Invitae Familial Variant Testing Reports
- Extracts key data from Invitae Carrier Screening Reports
- Outputs data to CSV

## Usage

### main.py

When running `main.py` the program will ask for the path of a folder containing all the PDFs you wish to extract data from.
It will then ask for the path of the CSV you wish to extract the data to.

It will create at most 2 CSV files:

- CSV containing all Diagnostic Testing and Familial Variant Testing Reports
- CSV containing all Carrier Screening Reports

The program will list any exceptions that arise and print to the shell the name of the file that caused the error and the error.

At the end the program prints the time it took to extract all the data from the PDFs. This time is in seconds.

## Files
- `main.py`  
  Contains the main program. Use this file to run the program.
- `dataExtraction.py`  
  Contains all methods related to extracting data from the reports. Has three classes:
    - InvitaeData
    - InvitaeCarrier
    - InvitaeFamilial
- `pdfextract.py`  
  Contains all methods related to extracting text from PDFs
- `output.py`  
  Contains all methods related to outputting to a CSV file
- `requirements.txt`  
  A list of requirements for this program



