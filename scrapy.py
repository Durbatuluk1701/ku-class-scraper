

import argparse
from datetime import date
import http.client as hc
from bs4 import BeautifulSoup

def init_argparser() -> argparse.ArgumentParser:
    argparser = argparse.ArgumentParser(description="Scrappy KU site for class info")
    argparser.add_argument("department", help = "department code (EECS, CLSX, ...) to look search for")
    argparser.add_argument("output", help = "file to output results to")
    return argparser

semesters = ["spring", "summer", "fall"]

def searchTermEncoder(year, semester):
    year = year % 100 # only last 2 digist
    if (semester == "spring"):
        return "4" + str(year) + "2"
    elif (semester == "summer"):
        return "4" + str(year) + "6"
    else:
        return "4" + str(year) + "9"

# https: // classes.ku.edu/Classes/CourseSearch.action?classesSearchText = eecs & searchCareer = UndergraduateGraduate & searchTerm = 4219

def connect_url(department : str, searchTerm : str) -> str:
    url = f"https://classes.ku.edu/Classes/CourseSearch.action?classesSearchText={department}&searchCareer=UndergraduateGraduate&searchTerm={searchTerm}"
    # open initial connection
    conn = hc.HTTPSConnection("classes.ku.edu")
    conn.request("GET", url)
    resp = conn.getresponse()
    if (resp.status != 200):
        raise ConnectionError("GET failed")
    return resp.read()

def parse_html(text : str):
    soup = BeautifulSoup(text, "html.parser")
    startBlocks = soup.find_all("tr > td > h3")
    print(startBlocks)


def traverseClasses(department : str):
    print("dull")
    

# if __name__ == "__main__":
#     argparser = init_argparser()
#     args = argparser.parse_args()
#     dept : str = args.department
#     output : str = args.output

