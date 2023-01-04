import argparse
import re
import http.client as hc
from bs4 import BeautifulSoup
import json


def init_argparser() -> argparse.ArgumentParser:
    parent_parser = argparse.ArgumentParser(
        description="KU class info site scrapper")
    parent_parser.add_argument(
        "department", help="department code (EECS, CLSX, ...) to look search for")
    parent_parser.add_argument(
        "output", help="file to output results to")

    parent_parser.add_argument("start_year", help="Start year")
    parent_parser.add_argument("start_term", help="Start term")
    parent_parser.add_argument("end_year", help="End year")
    parent_parser.add_argument("end_term", help="End term")
    return parent_parser


semesters = ["spring", "summer", "fall"]


def searchTermEncoder(year: str, semester: str) -> str:
    semester = semester.lower()
    year = int(year) % 100  # only last 2 digits
    if (semester == "spring"):
        return "4" + str(year) + "2"
    elif (semester == "summer"):
        return "4" + str(year) + "6"
    else:
        return "4" + str(year) + "9"


def connect_url(department: str, searchTerm: str) -> str:
    url = f"https://classes.ku.edu/Classes/CourseSearch.action?classesSearchText={department}&searchCareer=UndergraduateGraduate&searchTerm={searchTerm}"
    # open initial connection
    conn = hc.HTTPSConnection("classes.ku.edu")
    conn.request("GET", url)
    resp = conn.getresponse()
    if (resp.status != 200):
        raise ConnectionError("GET failed")
    return resp.read()


def clean_text(text: str) -> str:
    text = text.replace("\n", " ").replace(
        "\t", " ").replace("\xa0", " ").replace("(Save)", " ")
    while text != text.replace("  ", " "):
        text = text.replace("  ", " ")
    text = re.sub("^ ", "", text)
    text = re.sub(" $", "", text)
    return text


def parse_table(table) -> tuple[list[str], list[list[str]]]:
    headers = table.find_all("th")
    headers = [header.get_text() for header in headers]
    tableRows = table.find_all("tr")[1:]
    tableData = []
    for tableRow in tableRows:
        tableCols = [clean_text(tableCol.get_text())
                     for tableCol in tableRow.find_all("td")]
        tableData.append(tableCols)
    # The last entry of each 2 important rows are not very important
    tableData = [tableData[i]
                 for i in range(len(tableData)) if (i % 3 == 0 or i % 3 == 1)]
    for i in range(0, len(tableData), 2):
        tableData[i].append(tableData[i+1][1])
    tableData = [tableData[i] for i in range(0, len(tableData), 2)]
    # Hacky fix
    headers[1] = "Topic/Instructor"
    return (headers + ["Time/Place"], tableData)


def parse_row(row) -> tuple[str, str, str, list[str], list[list[str]]]:
    # return tuple of (className, miniDesc, description)
    descRow = row.find_next_sibling("tr")
    infoRow = descRow.find_next_sibling("tr")
    (headers, tableData) = parse_table(infoRow.find("table"))
    className = clean_text(row.find("h3").get_text())
    miniDesc = clean_text(row.find("td").get_text())
    description = clean_text(descRow.find("td").get_text())
    return (className, miniDesc, description, headers, tableData)


def parse_html(text: str):
    soup = BeautifulSoup(text, "html.parser")
    startBlocks = soup.find_all("h3")
    topRows = []
    for blk in startBlocks:
        topRows.append(blk.parent.parent)
    outStuff = {}
    for row in topRows:
        (name, miniDesc, desc, headers, tableData) = parse_row(row)
        outStuff[name] = {"name": name, "miniDesc": miniDesc,
                          "description": desc, "tableData": [headers] + tableData}
    return outStuff


def generateRange(startYear, endYear, startTerm, endTerm) -> list[str]:
    startCode = searchTermEncoder(startYear, startTerm)
    endCode = searchTermEncoder(endYear, endTerm)
    codes = [startCode]
    currentCode = startCode
    while endCode > currentCode:
        (year, term) = (int(currentCode[1:3]), int(currentCode[-1]))
        if (term == 2):
            term = 6
        elif (term == 6):
            term = 9
        elif (term == 9):
            year += 1
            term = 2
        else:
            raise Exception("ERROR")
        currentCode = f"4{year}{term}"
        codes.append(currentCode)
    return codes


def traverseClasses(out_file: str, department: str, startYear: int, endYear: int, startTerm: str, endTerm: str):
    codeRange = generateRange(startYear, endYear, startTerm, endTerm)
    bigObject = {}
    for code in codeRange:
        htmlRes = connect_url(department, code)
        classes = parse_html(htmlRes)
        bigObject[f"{department}-{code}"] = classes
    # default file name was `f"./data/{department}-{codeRange[0]}-{codeRange[-1]}.json"`
    with open(out_file, "w") as out_write:
        json.dump(bigObject, out_write, indent=2)


# https: // classes.ku.edu/Classes/CourseSearch.action?classesSearchText = eecs & searchCareer = UndergraduateGraduate & searchTerm = 4219


if __name__ == "__main__":
    parent_parser = init_argparser()
    args = parent_parser.parse_args()
    dept: str = args.department
    output: str = args.output
    s_year = args.start_year
    s_term = args.start_term
    e_year = args.end_year
    e_term = args.end_term
    traverseClasses(output, dept, s_year, e_year, s_term, e_term)
    print("Complete")
