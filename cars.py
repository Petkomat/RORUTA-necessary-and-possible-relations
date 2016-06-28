from os import listdir
from os.path import isfile
from functools import partial
from re import search
from tkinter import *
import matplotlib.pyplot as plt


# set the size of picture and font for pyplot
plt.rcParams['figure.figsize'] = 20, 10
plt.rcParams.update({'font.size': 15})

def toSlash(myPath):
    """
    Replaces backslashes in myPath with slashes and removes the last character of the modified myPath
    if the last character is slash.
    :param myPath: something like C:<delimiter1>Users<delimiter2>john<delimiter3>Documents<delimiter4>, where
    each delimiter is either slash or backslash. The last delimiter (delimiter4 in the example) my be empty string).
    :return: something like C:/Users/john/Documents
    """
    p = []
    for x in myPath:
        if x != "\\":
            p.append(x)
        else:
            p.append("/")
    if p[-1] == "/":
        p.pop()
    return "".join(p)


###################################################################################
# Performance table creation and reading                                          #
###################################################################################


def populatePerfTableDict(carName):
    """
    For Semi-automatic filling of the performanceTableDict. You will be asked to enter
    the values of the criteria. The input values are saved to performanceTableDict.

    :param carName: The name of the car, we want to describe.
    :return: None
    """

    print("Collecting data for", carName)
    performanceTableDict[carName] = {}
    for i,x in enumerate(criteriaNames):
        numberType = numberTypes[i]
        performanceTableDict[carName][x] = numberType(input("Enter {}: ".format(x)).strip())


def createCSVPerformanceTable():
    """
    Creates a CSV (comma-separated) of the form

    car,<crit1>,<crit2>,...,<critM>
    <alternative1>,<value11>,<value12>,...
    ...
    <alternativeN>,<valueN1>,...

    where <critJ> are the names of the criteria, <alternativeI> are names of the cars, and <valueIJ> is the
    value of J-th criterion for the I-th car.

    This file (table in it) is necessary for (almost) all of the following operations.
    If the inputFolder/performanceTableCSV already exists, nothing happens, otherwise populatePerfTableDict is used,
    and the result is saved to inputFolder/performanceTableCSV.

    :return: None
    """

    separator = ","
    alreadyExists = False
    for f in listdir(inputFolder):
        if isfile("{}/{}".format(inputFolder,f)) and f == performanceTableCSV:
            alreadyExists = True
            break
    if alreadyExists:
        print("The file already exists. This call of createCSVPerformanceTable will not have any effect.")
    else:
        for x in myAlternatives:
            populatePerfTableDict(x)
        with open("{}/{}".format(inputFolder, performanceTableCSV), "w") as f:
            print("{}{}{}".format("car", separator, separator.join(criteriaNames)), file=f)
            for x in myAlternatives:
                line = [x] + [str(performanceTableDict[x][y]) for y in criteriaNames]
                print(separator.join(line),  file=f)


def readPerformanceCSV():
    """
    Reads the performance table in the file  inputFolder/performanceTableCSV.

    :return: [altName1, ...], [critName1, ...], {altName1: {critName1: value11, ...}, ...}
    """

    alter = []
    perf = {}
    with open("{}/{}".format(inputFolder, performanceTableCSV)) as f:
        critNames = f.readline().strip().split(",")[1:]
        for x in f:
            line = x.strip().split(",")
            alter.append(line[0])
            perf[line[0]] = {critNames[i - 1]:line[i] for i in range(1, len(line))}
    return alter, critNames, perf

###################################################################################
# Creating necessary XML settings files for diviz                                 #
###################################################################################


def header():
    """
    Returns the header for the settings files.

    :return: The header for the settings files.
    """
    return '<xmcda:XMCDA xmlns:xmcda="http://www.decision-deck.org/2009/XMCDA-2.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.decision-deck.org/2009/XMCDA-2.0.0 file:/home/pat/Documents/currentResearch/DecisionDeck/svn-DecisionDeck/XMCDA/XMCDA-2.0.0.xsd">'


def endTag():
    """
    Returns the end tag for the settings files.

    :return: The end tag for the settings files.
    """
    return "</xmcda:XMCDA>"


def alternativesXML(alt):
    """
    Creates alternatives XML in inputFolder/myProjects/projectName folder.

    :param alt: List of the names of the alternatives.
    :return: None
    """

    spaceString = 4 * " "
    with open("{}/{}/{}/alternatives.xml".format(inputFolder, myProjects, projectName), "w") as f:
        space = 0
        print(header(), file=f)
        space += 1
        print("{}<alternatives>".format(spaceString * space), file=f)
        space += 1
        for i,a in enumerate(alt):
            print('{}<alternative id="a{}" name="{}"/>'.format(spaceString * space, i,a), file=f)
        space -= 1
        print("{}</alternatives>".format(spaceString * space), file=f)
        space -= 1
        print(endTag(), file=f)


def criteriaXML(criteria):
    """
    Creates criteria XML in inputFolder/myProjects/projectName folder.

    :param criteria: List of the names of the criteria.
    :return: None
    """
    spaceString = 4 * " "
    with open("{}/{}/{}/criteria.xml".format(inputFolder, myProjects, projectName), "w") as f:
        space = 0
        print(header(), file=f)
        space += 1
        print("{}<criteria>".format(spaceString * space), file=f)
        space += 1
        print("{}<description>".format(spaceString * space), file=f)
        space += 1
        print("{}<title>List of criteria</title>".format(spaceString * space), file=f)
        space -= 1
        print("{}</description>".format(spaceString * space), file=f)
        for i,cr in enumerate(criteria):
            print('{}<criterion id="cr{}" name="{}"/>'.format(spaceString * space, i, cr), file=f)
        space -= 1
        print("{}</criteria>".format(spaceString * space), file=f)
        space -= 1
        print(endTag(), file=f)


def perfTableXML(alt, criteria, perf):
    """
    Creates performance table XML in inputFolder/myProjects/projectName folder.

    :param alt: names of laternatives (list)
    :param criteria: names of criteria (list)
    :param perf: pefrormance table (dictionary: {alternative: {criterion: value, ...}, ...})
    :return: None
    """

    spaceString = 4 * " "
    with open("{}/{}/{}/performanceTable.xml".format(inputFolder, myProjects, projectName), "w") as f:
        space = 0
        print(header(), file=f)
        space += 1
        print("{}<performanceTable>".format(spaceString * space), file=f)
        space += 1
        print("{}<description>".format(spaceString * space), file=f)
        space += 1
        print("{}<title>Performance table</title>".format(spaceString * space), file=f)
        space -= 1
        print("{}</description>".format(spaceString * space), file=f)
        
        for i in range(len(alt)):
            print("{}<alternativePerformances>".format(spaceString * space), file=f)
            space += 1
            print("{}<alternativeID>a{}</alternativeID>".format(spaceString * space, i), file=f)
            for j in range(len(criteria)):
                print("{}<performance>".format(spaceString * space), file=f)
                space += 1
                print("{}<criterionID>cr{}</criterionID>".format(spaceString * space, j), file=f)
                print("{}<value>".format(spaceString * space), file=f)
                space += 1
                mtype = "real" if "." in perf[alt[i]][criteria[j]] else "integer"# change this if necessary
                print("{0}<{1}>{2}</{1}>".format(spaceString * space, mtype, perf[alt[i]][criteria[j]]), file=f)
                space -= 1
                print("{}</value>".format(spaceString * space), file=f)
                
                space -= 1
                print("{}</performance>".format(spaceString * space), file=f)

            space -= 1
            print("{}</alternativePerformances>".format(spaceString * space), file=f)
        
        space -= 1
        print("{}</performanceTable>".format(spaceString * space), file=f)
        space -= 1
        print(endTag(), file=f)


def preferencesXML(prefList):
    """
    Creates preferences XML of user defined preferences in inputFolder/myProjects/projectName folder.

    :param prefList:  A list of length three: the elements correspond to strong, weak and indiference preferences.
    Each of the three elements is of form [[a<id11>, a<id12>], [a<id21>, a<id22>], [a<id31>, a<id32>], ...]
    and contains at least 0 pairs.
    If R is a relation (>, >= or =), then [a<id1>, a<id2>] encodes the fact that a<id1> R a<id2>.
    :return: None
    """
    prefTypes = ["strong", "weak", "indif"]
    spaceString = 4 * " "
    with open("{}/{}/{}/preferences.xml".format(inputFolder, myProjects, projectName), "w") as f:
        printf = partial(print, file=f)
        space = 0
        printf(header())
        space += 1
        for i in range(len(prefTypes)):
            if prefList[i]:
                printf("{}<alternativesComparisons>".format(spaceString * space))
                space += 1
                printf("{}<comparisonType>{}</comparisonType>".format(spaceString * space, prefTypes[i]))
                printf("{}<pairs>".format(spaceString * space))
                space += 1
                for pair in prefList[i]:
                    printf("{}<pair>".format(spaceString * space))
                    space += 1
                    
                    printf("{}<initial>".format(spaceString * space))
                    space += 1
                    printf("{}<alternativeID>{}</alternativeID>".format(spaceString * space, pair[0]))
                    space -= 1
                    printf("{}</initial>".format(spaceString * space))
                    printf("{}<terminal>".format(spaceString * space))
                    space += 1
                    printf("{}<alternativeID>{}</alternativeID>".format(spaceString * space, pair[1]))
                    space -= 1
                    printf("{}</terminal>".format(spaceString * space))
                    
                    space -= 1
                    printf("{}</pair>".format(spaceString * space))
                
                space -= 1
                printf("{}</pairs>".format(spaceString * space))

                space -= 1
                printf("{}</alternativesComparisons>".format(spaceString * space))
    
        space -= 1
        print(endTag(), file=f)


def criteriaDirectXML(directions):
    """
    Creates criteria directions XML in inputFolder/myProjects/projectName folder.

    :param directions: a 0/1 list of directions, where 0 is used for the criteria where more is better
    (e.g., profit), and 1 otherwise (e.g., cost).
    :return: None
    """

    spaceString = 4 * " "
    with open("{}/{}/{}/criteriaPreferenceDirections.xml".format(inputFolder, myProjects, projectName), "w") as f:
        printf = partial(print, file=f)
        space = 0
        printf(header())
        space += 1
        printf('{}<criteriaValues mcdaConcept="preferenceDirection">'.format(spaceString * space))
        space += 1

        for i in range(len(directions)):
            printf("{}<criterionValue>".format(spaceString * space))
            space += 1
            printf("{}<criterionID>cr{}</criterionID>".format(spaceString * space, i))
            printf("{}<value>".format(spaceString * space))
            space += 1
            printf("{}<integer>{}</integer>".format(spaceString * space, directions[i]))
            space -= 1
            printf("{}</value>".format(spaceString * space))
            space -= 1
            printf("{}</criterionValue>".format(spaceString * space))

        space -= 1
        printf('{}</criteriaValues>'.format(spaceString * space))

        space -= 1
        printf(endTag())


def intensitiesOfPrefXML(pairsOfPairs):
    """
    Creates intensities of preferences XML in inputFolder/myProjects/projectName folder.

    :param pairsOfPairs: Like in the function preferences, the input list contains three elements that correspond
    to strict, weak and indifferent intensities. Each of the three elements contains at least 0
    elements of the form [[a,b],[c,d]] where a-d are alternatives. Such an element encodes the fact
    that U(a)- U(b) R U(c) - U(d), where R is one of the relations >, >= and =, and U is a utility function.
    :return: None
    """

    spaceString = 4 * " "
    prefTypes = ["strict", "weak", "indif"] # not strong, but strict!
    with open("{}/{}/{}/intensitiesOfPref.xml".format(inputFolder, myProjects, projectName), "w") as f:
        printf = partial(print, file=f)
        space = 0
        printf(header())
        space += 1
        for i in range(3):
            if pairsOfPairs[i]:
                printf('{}<alternativesComparisons>'.format(spaceString * space))
                printf("{}<comparisonType>{}</comparisonType>".format(spaceString * space, prefTypes[i]))
                printf("{}<pairs>".format(spaceString * space))
                space += 1
                for pp in pairsOfPairs[i]:
                    printf("{}<pair>".format(spaceString * space))
                    space += 1
                    for j in range(2):
                        printf("{}{}".format(spaceString * space,"<initial>" if j == 0 else "<terminal>"))
                        space += 1
                        printf("{}<alternativesSet>".format(spaceString * space))
                        space += 1
                        for elt in pp[j]:                            
                            printf("{}<element>".format(spaceString * space))
                            space += 1
                            printf("{}<alternativeID>{}</alternativeID>".format(spaceString * space, elt))
                            space -= 1
                            printf("{}</element>".format(spaceString * space))                            
                            
                        space -= 1
                        printf("{}</alternativesSet>".format(spaceString * space))

                        space -= 1
                        printf("{}{}".format(spaceString * space,"</initial>" if j == 0 else "</terminal>"))

                    space -= 1
                    printf("{}</pair>".format(spaceString * space))
                    space -= 1
                        

                printf("{}</pairs>".format(spaceString * space))
                printf('{}</alternativesComparisons>'.format(spaceString * space))
        space -= 1
        printf(endTag())


def getRepresentativeFunction(utilityXML):
    """
    Reads the XML file of the most representative utility function and returns it as a dictionary.

    :param utilityXML: name of XML file of most representative utility function
    :return: dictionary {crit1: {x11: y11, x12: y12, ...}, crit2: {x21: y21, x22: y22, ...}, ...},
    where x_ij are the values of crit_i and y_ij the values of i-th u_i in the point x_ij,
    where U = sum_i u_i, where U is the most representative utility function and u_i are its
    components that correspond to the criteria.
    """

    dicty = {}
    criterion = None
    point = [None, None]
    afterAxis = -1

    with open(utilityXML, "r") as f:
        for x in f:
            if "</criteria>" in x:
                break
            a = search('<criterion id="(.+)">', x)
            if a != None:
                criterion = a.group(1)
                dicty[criterion] = {}
            if afterAxis >= 0:
                value = search("<(.+)>(.+)</(.+)>",x) # it suffices to do so ...
                u = value.group(2)
                if afterAxis == 0:
                    # u may not be a number
                    try:
                        floatValue = float(u) if "." in u else int(u)
                    except:
                        floatValue = u
                else:
                    floatValue = float(u)
                point[afterAxis] = floatValue
                if afterAxis == 1: # we have ordinate
                    dicty[criterion][point[0]] = point[1]
                afterAxis = -1
            if "<abscissa>" in x:
                afterAxis = 0
            elif "<ordinate>" in x:
                afterAxis = 1
    return dicty

###################################################################################
# Plotting: relations and utility function                                        #
###################################################################################


def readRelations(relations, inputRels):
    """
    Reads the relations (either computed by diviz or user-defined.)

    :param relations: path pathToFile/file to the xml file, where the relations are stored
    :param inputRels: bool, if True, then the relations are input relations (user defined), otherwise,
    the relations were computed by diviz.
    :return: q list of relations: [strong, weak, indif], where each of the three elements has at
          at least 0 elements of form [alt1, alt2], meaning alt1 R alt2, where R is the corresponding
          relation (>, >= or =).
    """

    print("Reading", relations)
                 
    prefTypes = {"strong": 0, "weak": 1, "indif": 2}
    pairs = [[],[],[]] if inputRels else []
    pair = [None, None]
    place = 0
    mtype = None
    with open(relations, "r") as f:
        for x in f:
            a = search("<alternativeID>(.+)</alternativeID>", x)
            b = search("<comparisonType>(.+)</comparisonType>", x)
            if b != None:
                mtype = prefTypes[b.group(1).strip()]
            if a != None:
                pair[place] = a.group(1)
                if place == 1:
                    if inputRels:
                        pairs[mtype].append(pair[::])
                    else:
                        pairs.append(pair[::])
                place = 1 - place
    return pairs


def latestRun(folder):
    """
    Returns the name of the latest output folder in a folder than corresponds to some diviz workflow.
    The folder names are of form
    <year>-<month>-<day>T<hour>_<minute>_<second>.<miliseconds>+<something> or 'current'.

    :param folder: folder of the output folders
    :return: The name of the latest output file from a folder of the output files folder
    """

    files = [f for f in listdir(folder) if "current" not in f] # folder names
    return max(files)


def drawRelations(alter, divizWorkflowFolder, necessaryRels, file=""):
    """
    Draws the relations. Green / red coloured field in the intersection of i-th row and j-th column, means that
    alternative_i R alternative_j, where R is discovered / user defined relation.
    (For all feasible models, user defined relations are subset of discovered relations.
    It the model is infeasible, then the output xml are non-existent, hence there is no possible
    source of confusion.)

    :param alter: list of names of alternatives
    :param divizWorkflowFolder: root folder of a workflow, e.g., 'C:/Users/user/diviz_workspace/rorUtaNecessaryAndPossibleRelations'
    :param necessaryRels: bool, if necessaryRels, then we draw necessary relations, else we draw possible-ones
    :param file: output file of the workflow, if file = '', then the latest output file is chosen
    :return: None
    """

    def colour(i1, i2):
        """
        Determines the color of the relation of the alternatives i1 and i2: discovered relations are green,
        user defined are red. We do not make any distinction between different types (strong, weak etc.)

        :param i1: index of alternative
        :param i2: index of alternative
        :return:
        """

        i = "a" + str(i1)
        j = "a" + str(i2)
        if any([[i,j] in dmPref[k] for k in range(3)]):
            return "red"
        elif [i,j] in outputRelations:
            return "green"
        else:
            return "black"

    #reading
    run = "{}/{}".format(divizWorkflowFolder, file if file != "" else latestRun(divizWorkflowFolder))
    outputRelationsFolder = "{}/{}".format(run, "RORUTA-NecessaryAndPossiblePreferenceRelations-1")

    dmPref = readRelations("{}/{}".format(run, "preferences.xml"), True)  # decision maker preferences

    relXml = "necessary-relations.xml" if necessaryRels else "possible-relations.xml"
    outputRelations = readRelations("{}/{}".format(outputRelationsFolder, relXml), False)

    n = len(alter)
    altId = ["a{}".format(i) for i in range(n)]

    #canvas creation
    height = 700
    width = height
    window = Tk()
    window.title(("Neccesary" if necessaryRels else "Possible") +  " relations")
    canv = Canvas(window, height = height, width = width, bg="black")
    canv.grid(row=0, column=0)

    offset = 50
    unitDim = int((height - offset) / n)

    #plotting
    for i in range(n):
        x,y = offset + unitDim * i + unitDim // 2, 30
        canv.create_text(x, y, text = altId[i],  anchor="c", fill ="white", font = 20)
        canv.create_text(y, x, text = altId[i],  anchor="c", fill ="white", font = 20)
    for i in range(n):
        for j in range(n):
            x1, y1 = unitDim * i + offset, unitDim * j + offset
            x2, y2 = unitDim * (i + 1) + offset, unitDim * (j + 1) + offset
            canv.create_rectangle(x1, y1, x2, y2, fill = colour(j,i))
    window.mainloop()


def drawUtilityFunction(divizWorkflowFolder, criteriaNames, file = "", dimGraphs=(3,3)):
    """
    Draws chosen most representative utility function and returns its values.

    :param divizWorkflowFolder:  root folder of a workflow that outputs the most representative utility function,
    e.g., 'C:/Users/user/diviz_workspace/nameOfWorkflow'
    :param criteriaNames: list of names of the criteria
    :param file: name of the file (not the full path) with the output of a possible-and-necessary-relations workflow;
    if file = '', then the latest run in the divizWorkflowFolder is chosen
    :param dimGraphs: 2-tuple: how to place the different components of utility function: by default, they are placed
    in 3 rows of 3 graphps; if the number of components of an utility function is 7, then the last two plots will simply
     be empty (using the default value of dimGraphs)
    :return: the output of the function getRepresentativeFunction for the chosen run of representative-value-function
    """

    #reading
    run = "{}/{}".format(divizWorkflowFolder, file if file != "" else latestRun(divizWorkflowFolder))
    outputFolder = "{}/{}".format(run, "RORUTA-RepresentativeValueFunction-1")
    functionDict = getRepresentativeFunction("{}/{}".format(outputFolder, "representative-value-function.xml"))
    
    #draw marginal functions
    n = len(functionDict)               # number of criteria
    graphs = {i:[] for i in range(n)}   # {crit1: (list of xs, list of ys, list of x-labels), ...}
    for i in range(n):
        criteria = "cr{}".format(i)
        points = sorted(functionDict[criteria].items(), key = lambda x: x[1])
        try:
            xs = [float(t) for t,u in points] #this will cause an Exception if there is a non-numeric criterium
            namesX = [str(x) for x in xs]
        except:
            xs = [t for t in range(len(points))]
            namesX = [t for t,u in points]
        ys = [float(u) for t,u in points]
        
        graphs[i] = (xs, ys, namesX)
    for i in range(n, dimGraphs[0] * dimGraphs[1]):
        graphs[i] = ([0],[0], [""])
        
    f, axes = plt.subplots(dimGraphs[0], dimGraphs[1])
    
    for i in range(len(axes)):
        for j in range(len(axes[i])):
            ind = dimGraphs[1] * i + j
            if ind < n:
                xs, ys, prefTypes = graphs[ind]
                axes[i][j].plot(xs, ys)
                axes[i][j].scatter(xs, ys, color='r')
                axes[i][j].set_title(criteriaNames[ind])
                if i in [0,2] and j == 0:
                    plt.sca(axes[i][j])
                    plt.xticks(xs, prefTypes, rotation='90')
            else:
                axes[i][j].text(0.5, 0.5, 'EMPTY', horizontalalignment='center')

    plt.tight_layout()
    plt.show()
    return functionDict


def defineStrongRelations(fileRels):
    """
    Reads a file with user defined strong relations.

    :param fileRels: pathToMyRels/myRels, where myRels is a file with user defined strict relations, for example
    a3 > a4
    a1 > a3
    a42 > a12
    (if user defined 3 relations). The id numbers should be >= 1. (If one wants to use zero based counting,
    just modify the pomo function: change int(x) - 1 to int(x)). The alternatives should be indexed with respect to
    their order in the list myAlternatives.
    :return: List of pairs [[2,3],[0,2], [41, 11]] (if we follow the same example).
    """

    def pomo(x):
        return "a{}".format(int(x) - 1)
    prefList = []
    with open(fileRels, "r") as f:
        for x in f:
            line = x.strip()
            if line:
                a = search("a([0-9]+) > a([0-9]+)", line)
                prefList.append([a.group(1), a.group(2)])
    prefList = [[pomo(x), pomo(y)] for [x,y] in prefList]
    return prefList
        
###################################################################################
# Some notes on use of the functions                                              #
###################################################################################
# When using this script, one should proceed as follows:
#    1. use this script to create all input files and include them into the workflow in diviz
#    2. run the workflow
#    3. use this script to analyse the results
#
# We expect the following file structure:
#    1. input files:
#        inputFolder/
#            performanceTableCSV (file)
#            myProjects/
#                projectName (folder)
#            preferences (folder)
#    2. output files:
#        divizWFfolder/
#            projectName/
#                standard structure of output (and input) files/folders, produced by diviz
#
#    It is necessary for the diviz workflow with the name projectName, to have the following widgets:
#        a) RORUTA-NecessaryAndPossiblePreferenceRelations (for the computation of relations)
#        b) RORUTA-RepresentativeValueFunction (for the most representative utility function)
#
# Description of some files and folders:
#
#    performanceTableCSV:
#        Name of the file, where a performance table is stored.
#        The file can be the result of a call of createCSVPerformanceTable function,
#        whose documentation includes also the expected form of the performance table in
#        this file.
#        
#        If the number of alternatives or criteria is high, it might me tedious to enter the values
#        of the table one by one (which is the case, when we use createCSVPerformanceTable).
#        In that case, user should find a better way to create a table.
#
#    projectName:
#        Name of the diviz workflow that is used to produce the results.
#        
#        In the inputFolder/projectName folder, all .xml settings file are created
#        by the functions, such as alternativesXML etc.
#
#        In the divizWFfolder/projectName, one can find all files, produced by diviz,
#        when running the workflow.
#
#    preferences:
#        Folder preferences is not necessary, if we get user-defined preferences
#        from some other source (for example, by defining them directly in this script)
#        or if we simply do not have any.
#        However, if the folder is there, we expect that it contains .pref files
#        preferences/
#            someName.pref
#            anotherName.pref
#            ...
#        which are ordinary text files, that must be compatible with the function that reads them:
#        defineStrongRelations, hence its documentations also includes the form of the .pref files.
#
# When defining your relations/preferences directly in this script, do not use the real names in the pairs:
#    A list of (for example, strog) relations
#         [['Mazda CX-5 ... 2015 - 2016', 'Audi A3 ... 2014 - 2016'], ...]
#    is not valid. You must use the abbreviations of form a<id>, instead of the real names,
#    where 0 <= id < number of alternatives. The correct version of a list with the relations
#    (for the same two cars) would be
#        [['a1', 'a0'], ...].
#
#    The id of a alternative is the index of the alternative in the list of alternatives myAlternatives.
#    The same holds for weak and indif relations (and for the lists, describing the intensities
#    of the relations). Some examples can be seen in the comments below.
#
#    Element [aI, aJ] of the list for relation R (strong: >, weak: >=, indifferent: =), means that
#    aI R aJ.
#    Element [[aI1, aJ1],[aI2, aJ2]] of the list for intensities of the relation R, means that
#    U(aI1) - U(aJ1) R U(aI2) - U(aJ2) for all utility functions U, and R as in the upper case.
#
# How to choose a particular run to be analysed:
#        This is described in the documentation of the 'plotting' functions.


if __name__ == "__main__":
    #DEFINE NECESSARY FOLDERS and a FILE
    divizWFfolder = "C:/Users/matejp/diviz_workspace/rorUtaNecessaryAndPossibleRelations"  #the chosen workflow folder, where diviz outputs are stored
    performanceTableCSV = "performances.csv"                                                #the name of file with csv performance table    
    inputFolder = "C:/Users/matejp/Documents/predavanja/decisionSupport"                   #location of performanceTableCSV and folders with settings files for all diviz projects (or at least, for the RORUTA-related project)
    myProjects = "divizStvari"                                                              #folder in inputFolder, where folders with setings file are stored
    projectName = "rorUtaNecessaryAndPossibleRelations"                                     #name of the RORUTA-related diviz-project

    # folders should use / and not \\, and should not end with /.
    divizWFfolder = toSlash(divizWFfolder)
    inputFolder = toSlash(inputFolder)
    
    #DEFINE THE PROBLEM
    myAlternatives = sorted(["Audi A3 1.6 TDI 110hp Ambiente 2014 - 2016",                  # alternatives
                             "Mazda CX-5 SkyActiv-D 150 Skylease GT 2015 - 2016",
                             "Citroen C3 1.4 HDi 70 Ligne Business 2010 - 2011",
                             "Renault Twizy Color 2012 - 2016",
                             "Fiat 500 1.2 Naked 2008 - 2009",
                             "Peugeot 308 SW Active 1.6 VTi 2011 - 2013",
                             "Toyota Yaris 1.0 VVT-i Acces 2012 - 2014",
                             "Volkswagen Sharan 2.0 Comfortline 2000 - 2008",
                             "Skoda Fabia Sedan 1.4 16V 75hp Elegance 2004 - 2006"])
    criteriaNames = ["price",                                                               # criteria
                     "#doors",
                     "#seats",
                     "trunkVolume",
                     "maxEnginePower",
                     "fuelConsumption",
                     "releaseDate",
                     "crashTest"]    
    numberTypes = [int if "#" in x or "Date" in x or "crashTest" in x else float for x in criteriaNames] #types of criteria: int of float; needed for nicer/cleaner representation    

    
    if 1:
        #CREATE A PERFORMANCE TABLE IF NECESSARY, AND READ IT
        performanceTableDict = {} #{alternative1: {crit1: value11, crit2: value12, ...}, alternative2: {crit1: value21, crit2: value22, ...}, ...}
        createCSVPerformanceTable()
        
        alt, criteria, perf = readPerformanceCSV()  

        #CREATE XML SETTINGS FILES:
        alternativesXML(alt)                                    #alternatives
        criteriaXML(criteria)                                   #criteria    
        perfTableXML(alt, criteria, perf)                       #performance table

        variants = ["linearna",                                 #names of folders whith some user defined preferences
                    "nakljucnaTretjina",                        #in .pref files
                    "full",
                    "deterministicnaPolovica",
                    "linearnaBolje",
                    "linearna2"]
        
        strong = []                                             #[["a0", "a8"],["a1","a2"],["a3", "a8"],["a6","a7"],["a1","a0"],["a4","a3"],["a2","a4"],["a5","a8"]][:4]
        weak = []                                               #[["a0", "a1"]]#[["a3", "a0"]]
        indif = []                                              #[["a2","a7"],["a7", "a2"],["a1","a6"],["a6","a1"],["a5","a6"],["a6","a5"]][:0]#[["a6","a7"],["a7","a6"]]#[["a1" ,"a2"]]#[["a1", "a4"],["a8","a0"]]
        strong = defineStrongRelations("{}/{}".format("C:/Users/matejp/Documents/predavanja/decisionSupport/preference", "{}.pref".format(variants[-2]))) #user-defined strong relations
        preferencesXML([strong, weak, indif])                   #preferences
        directions = [1,0,0,0,0,1,0,0]
        criteriaDirectXML(directions)                           #directions of criteria
                        
        strongInt = []                                          #[[["a3", "a4"],["a7", "a8"]]]#[[["a0", "a1"],["a4", "a5"]]]#[["a0", "a1"], ["a0", "a2"]]
        weakInt = []                                            #[["a0", "a1"]]#[["a3", "a0"]]
        indifInt = []                                           #[[["a6","a7"],["a7","a6"]]]#[["a1" ,"a2"]]#[["a1", "a4"],["a8","a0"]]
        intensitiesOfPrefXML([strongInt, weakInt, indifInt])    #intensities of preferences
    
    
        if True:
            #PLOT THE RELATIONS AND MOST REPRESENTATIVE UTILITY FUNCTION
            ind = -1
            drawRelations(alt, divizWFfolder, True, file=variants[ind])
            drawRelations(alt, divizWFfolder, False, file=variants[ind])

            dicty = drawUtilityFunction(divizWFfolder, criteria, file=variants[ind])
    if 1:
        a = r"C:/Users/matej/ds"
        b = "C:\\Userst\\matej\\ds/"
        c = b[:-1] + "\\"
        print(toSlash(a), toSlash(b), toSlash(c))