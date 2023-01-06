import json
import re
from copy import deepcopy


def load_file(fileName: str) -> json:
    with open(fileName, "r") as fp:
        return json.load(fp)


def flatten_dict(dict: dict[str, dict[str, dict]]) -> dict[str, dict]:
    returnDict = {}
    for topKey in dict.keys():
        [dept, termCode] = topKey.split("-")
        for classKey in dict[topKey].keys():
            if (classKey not in returnDict.keys()):
                # not available yet, so set up
                returnDict[classKey] = {}
            # add relevant for term
            returnDict[classKey][termCode] = dict[topKey][classKey]
    return returnDict

# cleans up the data some


def simple_data_clean(dict: dict[str, dict]) -> dict[str, dict]:
    # lazy approach
    returnDict = deepcopy(dict)
    # drop tableData, and name (its obvious)
    for cls in returnDict.values():
        for term in cls.values():
            del term["tableData"]
            del term["name"]
            term["miniDesc"] = re.sub(
                " (Fall|Spring|Summer) \d+", "", term["miniDesc"])
    # dropping duplicates
    for clsKey in returnDict.keys():
        cls = returnDict[clsKey]
        clsOut = {}
        for termKey in cls.keys():
            term = cls[termKey]
            resolved = False
            for outTermKey in clsOut.keys():
                outTerm = clsOut[outTermKey]
                if (term["miniDesc"] == outTerm["miniDesc"]
                        and term["description"] == outTerm["description"]):
                    # these are duplicates
                    clsOut[outTermKey]["terms"].append(termKey)
                    resolved = True
            if (not resolved):
                # we did not find a duplicate so add here
                # not a duplicate, add a term
                clsOut[termKey] = deepcopy(term)
                clsOut[termKey]["terms"] = [termKey]
        returnDict[clsKey] = clsOut

    # sorting
    keyList = list(returnDict.keys())
    keyList.sort()
    sorted = {i: returnDict[i] for i in keyList}

    return sorted


def simplify_data():
    inFile = input("Input file path: ")
    outFile = input("Output file path: ")
    with open(outFile, "w") as fo:
        json.dump(simple_data_clean(
            flatten_dict(load_file(inFile))), fo, indent=2)


if __name__ == "__main__":
    simplify_data()
