from helpingFunctions import *
        


#DEFINE NECESSARY FOLDERS and a FILE
divizWFfolder = "C:/Users/matejp/diviz_workspace/rorUtaNecessaryAndPossibleRelations"
performanceTableCSV = "performances.csv"
inputFolder = "C:/Users/matejp/Documents/predavanja/decisionSupport"
myProjects = "divizStvari"
projectName = "rorUtaNecessaryAndPossibleRelations"




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
strong = defineStrongRelations("{}/{}".format("C:/Users/matejp/Documents/predavanja/decisionSupport/preferences", "{}.pref".format(variants[-2]))) #user-defined strong relations
preferencesXML([strong, weak, indif])                   #preferences

directions = [1,0,0,0,0,1,0,0]
criteriaDirectXML(directions)                           #directions of criteria
                
strongInt = []                                          #[[["a3", "a4"],["a7", "a8"]]]#[[["a0", "a1"],["a4", "a5"]]]#[["a0", "a1"], ["a0", "a2"]]
weakInt = []                                            #[["a0", "a1"]]#[["a3", "a0"]]
indifInt = []                                           #[[["a6","a7"],["a7","a6"]]]#[["a1" ,"a2"]]#[["a1", "a4"],["a8","a0"]]
intensitiesOfPrefXML([strongInt, weakInt, indifInt])    #intensities of preferences
    

#PLOT THE RELATIONS AND MOST REPRESENTATIVE UTILITY FUNCTION
ind = -1
drawRelations(alt, divizWFfolder, True, file=variants[ind])
drawRelations(alt, divizWFfolder, False, file=variants[ind])

dicty = drawUtilityFunction(divizWFfolder, criteria, file=variants[ind])
