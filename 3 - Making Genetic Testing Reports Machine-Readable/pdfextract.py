'''
    This module is for extracting text from PDF files
    
    Current Functionality:
        - Extract text starting from a specified page
        - Extract tables from a specified page
        - Find the page number for the first instance of a string
'''
import pdfplumber


def detailedExtract(pdfFile: str, pageNum: int) -> str:
    ''' 
        Extracts the text from a specified pdf file using pdfplumber

        Parameters:
            pdfFile: str - the name of the pdf file to extract text from
            pageNum: int - the number of the page to start extracting from

        Returns:
            extracted text
    '''
    txt = ""
    with pdfplumber.open(pdfFile) as pdf:
        for i in range(pageNum, len(pdf.pages)):
            txt = txt + pdf.pages[i].extract_text()
    return txt


def tableExtract(pdfFile: str, pageNum: int):
    ''' 
        Extracts tables from a specified page of a pdf file

        Parameters:
            pdfFile: str - the name of the pdf file
            pageNum: int - the page number of the pdf file to extract tables from

        Returns:
            a list of tables containing a list of rows containing a list of cells
    '''
    with pdfplumber.open(pdfFile) as pdf:
        page = pdf.pages[pageNum]
        tables = page.extract_tables()
    return tables


def findPageNum(pdfFile: str, txt: str) -> int:
    ''' 
        Finds the page number of the page containing the first instance of a specified text

        Parameters:
            pdfFile: str - the name of the pdf file
            txt: str - the text to search for

        Returns:
            the page number
    '''
    pageNum = -1
    with pdfplumber.open(pdfFile) as pdf:
        for i in range(len(pdf.pages)):
            if len(pdf.pages[i].search(txt)) > 0:
                pageNum = i
                break
    return pageNum
