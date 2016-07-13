from os import listdir
from os.path import isfile
from functools import partial
from re import search
from tkinter import *
import matplotlib.pyplot as plt
from random import random, seed


# set the size of picture and font for pyplot
plt.rcParams['figure.figsize'] = 10, 20
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


def populatePerfTableDict(alternativeName):
    """
    For Semi-automatic filling of the performanceTableDict. You will be asked to enter
    the values of the criteria. The input values are saved to performanceTableDict.

    :param alternativeName: The name of the alternative, we want to describe.
    :return: None
    """

    print("Collecting data for", alternativeName)
    performanceTableDict[alternativeName] = {}
    for i,x in enumerate(criteriaNames):
        numberType = numberTypes[i]
        performanceTableDict[alternativeName][x] = numberType(input("Enter {}: ".format(x)).strip())


def createCSVPerformanceTable():
    """
    Creates a CSV (comma-separated) of the form

    alternative,<crit1>,<crit2>,...,<critM>
    <alternative1>,<value11>,<value12>,...
    ...
    <alternativeN>,<valueN1>,...

    where <critJ> are the names of the criteria, <alternativeI> are names of the alternatives, and <valueIJ> is the
    value of J-th criterion for the I-th alternative.

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
        print("The file that contains performance table already exists. This note is the only effect of this call of "
              "createCSVPerformanceTable.")
    else:
        for x in myAlternatives:
            populatePerfTableDict(x)
        with open("{}/{}".format(inputFolder, performanceTableCSV), "w") as f:
            print("{}{}{}".format(alternative, separator, separator.join(criteriaNames)), file=f)
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
            perf[line[0]] = {critNames[i - 1]: line[i] for i in range(1, len(line))}
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
            if a is not None:
                criterion = a.group(1)
                dicty[criterion] = {}
            if afterAxis >= 0:
                value = search("<(.+)>(.+)</(.+)>", x)  # it suffices to do so ...
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


def evalRepresentativeFunction(dictFunction, alternativesToEvaluate, file='', sortByUtility=True):
    """
    Evaluats the function given as the dictionary {'cr0': {x00: y00, x01: y01, ...}, ...} on the list of indices of
    alternatives alternativesToEvaluate (with respect to myAlternatives). Indices of criteria correspond
    to the criteriaNames.
    :param dictFunction:
    :param alt:
    :param crit:
    :return: list of values representativeFunction(alternative)
    """
    _, _, performances = readPerformanceCSV()
    evaluations = {myAlternatives[ind_a]: 0.0 for ind_a in alternativesToEvaluate}
    for ind_a in alternativesToEvaluate:
        a = myAlternatives[ind_a]
        for ind_cr, cr in enumerate(criteriaNames):
            value = numberTypes[ind_cr](performances[a][cr])
            evaluations[a] += dictFunction["cr{}".format(ind_cr)][value]
    sortingCriteron = (lambda u: -evaluations[u]) if sortByUtility else lambda u: u
    if file != '':
        with open(file, "w") as f:
            print("alternative,mostRepresentativeUtilityFunction(alternative)", file=f)
            for x in sorted(evaluations, key=sortingCriteron):
                print("{},{:.4f}".format(x, evaluations[x]), file=f)
    else:
        print("alternative,mostRepresentativeUtilityFunction(alternative)")
        for x in sorted(evaluations, key=sortingCriteron):
            print("{},{:.4f}".format(x, evaluations[x]))


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


def drawRelations(alter, divizWorkflowFolder, necessaryRels, divizRun=""):
    """
    Draws the relations. Green / red coloured field in the intersection of i-th row and j-th column, means that
    alternative_i R alternative_j, where R is discovered / user defined relation.
    (For all feasible models, user defined relations are subset of discovered relations.
    If the model is infeasible, then the output xmls are non-existent, hence there is no possible
    source of confusion.)

    :param alter: list of names of alternatives, e.g., ['Volvo', 'Skoda', ...] and not ['a2', 'a0', ...]
    :param divizWorkflowFolder: root folder of a workflow, where the outputs are stored, e.g.,
    'C:/Users/user/diviz_workspace/rorUtaNecessaryAndPossibleRelations'
    :param necessaryRels: bool, if necessaryRels, then we draw necessary relations, otherwise we draw possible-ones
    :param divizRun: name of the output folder of the workflow, if divizRun = '',
    then the latest output folder is chosen
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
    run = "{}/{}".format(divizWorkflowFolder, divizRun if divizRun != "" else latestRun(divizWorkflowFolder))
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


def drawUtilityFunction(divizWorkflowFolder, criteriaNames, file="", dimGraphs=(3, 3)):
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
        points = sorted(functionDict[criteria].items(), key=lambda x: x[1])
        try:
            xs = [float(t) for t, u in points]  # this will cause an Exception if there is a non-numeric criterion
            namesX = [str(x) if i < len(xs) - 1 and abs(xs[i + 1] - x) > 4.0 or i == len(xs) else "" for i, x in enumerate(xs)]
        except:
            print("rarara")
            xs = [t for t in range(len(points))]
            namesX = [t for t, u in points]
        ys = [float(u) for t, u in points]

        graphs[i] = (xs, ys, namesX[::])
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
                    plt.sca(axes[i, j])
                    plt.xticks(xs, prefTypes, rotation='90')
            else:
                axes[i][j].text(0.5, 0.5, 'EMPTY', horizontalalignment='center')

    plt.tight_layout()
    plt.show()
    return functionDict


##################################################################################
# User defined relations                                                         #
##################################################################################


def defineStrongRelations(fileRels):
    """
    Reads a file with user defined strong relations.

    :param fileRels: pathToMyRels/myRels, where myRels is a file with user defined strict relations, for example
    a2 > a4
    a0 > a2
    a42 > a12
    (if user defined 3 relations). The id numbers should be >= 0. The alternatives should be indexed with respect to
    their order in the list myAlternatives.
    :return: List of pairs [[2,3],[0,2], [42, 12]] (if we follow the same example).
    """

    def pomo(x):
        return "a{}".format(x)
    prefList = []
    with open(fileRels, "r") as f:
        for x in f:
            line = x.strip()
            if line:
                a = search("a([0-9]+) > a([0-9]+)", line)
                prefList.append([a.group(1), a.group(2)])
    prefList = [[pomo(x), pomo(y)] for [x, y] in prefList]
    return prefList


def createRandomSubsampleOfAllRelations(linearOrder, size, file, randomSeed=12345):
    """
    We sample uniformly at random some relations and save them to file.
    :param linearOrder: [indexOfTheBestAlternative, indexOfSecondBestAlternative, ...], where indices >= 0 and they
    correspond to the myAlternatives.
    :param size: the size of the random sample
    :param randomSeed: randomSeed used
    :param file: The subsample will be saved to inputFolder/preferences/file.pref
    :return:
    """
    seed(randomSeed)
    indices = {x: i for i, x in enumerate(linearOrder)}
    n = len(linearOrder)
    maxPairs = n * (n + 1) // 2
    if not 0 <= size <= maxPairs:
        raise Exception("size = {} breaks the assumption 0 <= size <= #different pairs.".format(size))
    subsample = set()
    while len(subsample) < size:
        ind1 = int(random() * n)
        ind2 = int(random() * n)
        while ind2 == ind1:
            ind2 = int(random() * n)
        ind1, ind2 = (ind1, ind2) if ind1 < ind2 else (ind2, ind1)
        subsample.add((linearOrder[ind1], linearOrder[ind2]))
    with open("{}/preferences/{}.pref".format(inputFolder, file), "w") as f:
        for (alt1, alt2) in subsample:
            better = max(alt1, alt2, key=lambda x: -indices[x])
            worse = min(alt1, alt2, key=lambda x: -indices[x])
            print("a{} > a{}".format(better, worse), file=f)


def createLinearRelations(linearOrder, file):
    """
    From the list linearOrder = [indexOfTheBestAlternative, indexOfSecondBestAlternative, ...] of length n,
    we create a file that contains n - 1 lines:
    a<indexOfTheBestAlternative> > a<indexOfSecondBestAlternative>
    ...
    a<indexOf(n-1)BestAlternative> > a<indexOf(n)BestAlternative>

    :param linearOrder:
    :param file: The relations will be saved to inputFolder/preferences/file.pref
    :return:
    """
    with open("{}/preferences/{}.pref".format(inputFolder, file), "w") as f:
        for i in range(len(linearOrder) - 1):
            print("a{} > a{}".format(linearOrder[i], linearOrder[i + 1]), file=f)


#############################################################################################
# Example                                                                                   #
#############################################################################################

# DEFINE NECESSARY FOLDERS and a FILE
divizWFfolder = "./carsExample/divizOutputs/rorUtaNecessaryAndPossibleRelations"
performanceTableCSV = "performances.csv"
inputFolder = "./carsExample/myInputs"
myProjects = "myWorkflows"
projectName = "rorUtaNecessaryAndPossibleRelations"

divizWFfolder = toSlash(divizWFfolder)
inputFolder = toSlash(inputFolder)


# DEFINE THE PROBLEM
alternative = "car"                                                                     # type of the alternatives
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
numberTypes = [int if "#" in x or "Date" in x or "crashTest" in x else float for x in criteriaNames]  # types of criteria: int or float; needed for nicer/cleaner representation

# CREATE A PERFORMANCE TABLE IF NECESSARY, AND READ IT
performanceTableDict = {}
createCSVPerformanceTable()
alt, criteria, perf = readPerformanceCSV()

# CREATE XML SETTINGS FILES:
alternativesXML(alt)                                    # alternatives
criteriaXML(criteria)                                   # criteria
perfTableXML(alt, criteria, perf)                       # performance table

variants = ["linear",                                 # names of folders whith some user defined preferences
            "random12",                               # in .pref files
            "full"]
ind = 2

strong = []                                             # [["a0", "a8"],["a1","a2"],["a3", "a8"],["a6","a7"],["a1","a0"],["a4","a3"],["a2","a4"],["a5","a8"]]
weak = []                                               # [["a0", "a1"]]#[["a3", "a0"]]
indif = []                                              # [["a2","a7"],["a7", "a2"],["a1","a6"],["a6","a1"],["a5","a6"],["a6","a5"]][:0]#[["a6","a7"],["a7","a6"]]#[["a1" ,"a2"]]

strong = defineStrongRelations("{}/preferences/{}".format(inputFolder, "{}.pref".format(variants[ind])))
preferencesXML([strong, weak, indif])                   # preferences

directions = [1, 0, 0, 0, 0, 1, 0, 0]
criteriaDirectXML(directions)                           # directions of criteria

strongInt = []                                          # [[["a3", "a4"],["a7", "a8"]]]#[[["a0", "a1"],["a4", "a5"]]]#[["a0", "a1"], ["a0", "a2"]]
weakInt = []                                            # [["a0", "a1"]]#[["a3", "a0"]]
indifInt = []                                           # [[["a6","a7"],["a7","a6"]]]#[["a1" ,"a2"]]#[["a1", "a4"],["a8","a0"]]
intensitiesOfPrefXML([strongInt, weakInt, indifInt])    # intensities of preferences


# PLOT THE RELATIONS AND MOST REPRESENTATIVE UTILITY FUNCTION
drawRelations(alt, divizWFfolder, True, divizRun=variants[ind])                               # here, we have renamed the diviz run, so
drawRelations(alt, divizWFfolder, False, divizRun=variants[ind])                              # that it equals the name of the variant
dicty = drawUtilityFunction(divizWFfolder, criteria, file=variants[ind], dimGraphs=(4, 2))    # of user defined preferecnes.

# EVALUATE THE ALTERNATIVES
evalRepresentativeFunction(dicty, list(range(len(myAlternatives))), file="", sortByUtility=False)
