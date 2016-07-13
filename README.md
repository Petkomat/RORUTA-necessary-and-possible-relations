# RORUTA: necessary and possible relations

Use of the widgets `RORUTA-NecessaryAndPossiblePreferenceRelations` and `RORUTA-RepresentativeValueFunction` from [diviz](http://www.decision-deck.org/diviz/download.html).

## Dependencies

- `Python3`; if you want to plot the most representative utility function, the `matplotlib` library is needed also
- `diviz` (tested on the version `1.15.1`)

## Useful notes

One should proceed as follows:
 
1. Use the script `roruta.py` to create all input files and include them into the workflow in diviz.
2. Run the workflow.
3. Use the script `roruta.py` to analyse the results.

First of all, the following values must be set:

- `divizWFfolder`: the chosen workflow folder, where diviz outputs are stored
- `performanceTableCSV`: name of the file, where a performance table is stored.
        The file can be the result of a call of the function `createCSVPerformanceTable`,
        whose documentation includes also the expected form of the performance table in
        this file.
        If the number of alternatives or criteria is high, it might me tedious to enter the values
        of the table one by one (which is the case, when we use `createCSVPerformanceTable`).
        In that case, user should find a better way to create a table.
- `inputFolder`: location of `performanceTableCSV` and folders with settings files for the diviz RORUTA-related project `projectName`
- `myProjects`: folder in `inputFolder`, where folders with setings file are stored
- `projectName`: the name of a diviz workflow that is used to produce the results.
        In the folder `inputFolder/projectName`, all `.xml` settings file are created
        by the functions, such as `alternativesXML` etc. In the folder `divizWFfolder/projectName`, one can find all files, produced by diviz,
        when running the workflow.
- `preferences`: this folder is not necessary, if we get user-defined preferences
        from some other source (for example, by defining them directly in `roruta.py`)
        or if we simply do not have any.
        However, if the folder is there, we expect that it contains `.pref` files
        which are ordinary text files, that must be compatible with the function that reads them:
        `defineStrongRelations`, hence its documentations also includes the form of the `.pref` files.

Strings describing paths should contain `/` and not `\`, and should not end with `/` (function `toSlash` might come in handy).


The following file structure is expected:

##### Input files
  ````
inputFolder/
    performanceTableCSV (file)
    myProjects          (folder)
        projectName     (folder)
        ....
    preferences         (folder)
    ...
````
##### Output files
````
divizWFfolder/
    projectName/
        standard structure of output (and input) files and folders, produced by diviz
````
It is necessary for the diviz workflow with the name `projectName`, to have the following widgets:

- `RORUTA-NecessaryAndPossiblePreferenceRelations` (for the computation of relations),
- `RORUTA-RepresentativeValueFunction` (for the most representative utility function),

see the ![workflow structure](https://github.com/Petkomat/RORUTA-necessary-and-possible-relations/blob/master/workflow.pdf "Diviz workflow").


##### Defining relations

When defining your relations/preferences, do not use the real names in the pairs:
A list of (for example, strog) relations
     `[['Mazda CX-5 ... 2015 - 2016', 'Audi A3 ... 2014 - 2016'], ...]`
is not valid. You must use the abbreviations of the form `a<id>` instead of the real names,
where `0 <= id < number of alternatives`. The `id` of an alternative is the index of the alternative
in the list of alternatives `myAlternatives`.

The correct version of the upper list with the relations
would be  `[['a1', 'a0'], ...]` (since Mazda and Audi are the second and the first car in `myAlternatives`).


The same holds for weak and indif relations (and for the lists, describing the intensities
of the relations). Some examples can be seen in the comments below.

Element `[aI, aJ]` of the list for relation `R` (strong: `>`, weak: `>=`, indifferent: `=`), means that
`aI R aJ`.
Element `[[aI1, aJ1], [aI2, aJ2]]` of the list for intensities of the relation `R`, means that
`U(aI1) - U(aJ1) R U(aI2) - U(aJ2)` for all utility functions `U`, and `R` as in the upper case.

##### Choosing a particular run to be analysed
This is described in the documentation of the 'plotting' functions.
