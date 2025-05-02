# Quest Survey Class Assignment Algorithm
Hello from 2025. This is Python code to take input data from a Salesforce (TFA) survey and distribute students randomly within their matriculation semester.

The code was run by the Quest Director in Ruby, but was re-coded in Python by Joe Uong, Data Analyst in CLAS and Preview Troubleshooter, in 2024. 

Below are the steps to prep the files in order to complete this process. 

Direct access to Course data is helpful but not mandatory since Quest Admin (currently Kendall Kroger) can assist with section info (such as name and capacity).

## Prep
### Need an Excel file with these sheets (sample has required columns highlighted in yellow):
- Need two files: one for Summer and one for Fall. 
- Give each file the name of the term in term-code format (e.g., "2245" or "2248")
- Each file should have these tabs named like this (lowercase):
    1. `data` (data from the survey):
        - `UFID`
        - `Course Offering Id 18` (SF18)
            - Needs to be the 18-character version
        - `Topic`
        - New columns for 2025: prioritizing Honors students:
            - Use a character of "1" to denote that this line meets column criteria
                - `URSP`
                - `Honors` (Honors students)
                - `Honors Course`
    2. `summary` (summary data, aggregate data of Sheet 3): 
        - `Course Offering Id 18` (SF18)
            - Needs to be the 18-character version
        - `CAPACITY`
            - Sum of all sections of the course using Sheet3
        - `PRIORTIY`
            - Sort the courses by priority:
                - Honors classes first
                - Lower picked classes next
                - Then everything else by number of picks from the Survey Results
    3. `detail` (data from SOC, requires student records access. Need to match TOPIC with CS name and translate SFID)
        - `Course Offering Id 18` (SF18)
            - Needs to be the 18-character version
        - `Topic`
        - `CN`
        - `C_CAPACITY`
```    
    Sheet 1 - Data
        - Data from the Salesforce output (adding data for which courses are Honors)
        - Data indicating which Students are URSP or Honors
    Sheet 2 - Summary
        - Pivot data from Sheet 3 to get summary capacity
        - Then sort by priority courses
    Sheet 3 - Detail
        - Data comes from CS / SOC. 
        - Match Quest 1 courses along with Class Nbrs with the SF18
        - Match the CS name of the section up with the Topic shown to students in the Salesforce survey
```

### Salesforce Data
- Reports folder (must have read access): [CLAS > Quest](https://uf.lightning.force.com/lightning/r/Folder/00l4X000002nHiYQAU/view?queryScope=userFoldershttps://uf.lightning.force.com/lightning/r/Folder/00l4X000002nHiYQAU/view?queryScope=userFolders)
    - Need two files: 
        1. **Quest Course Connections** 
            - This is the survey data with student information
            - Includes _Course Offering Id 18_ and Student information
        2. **Quest Course Offerings** 
            - This is the file with the _Course Offering Id 18_ that will need to be read by the script
            - It will have the _Topic_ as well which will need to be compared to the CS version

### Campus Solutions Data (WH)
- Pull all Quest 1 courses along with Class Nbrs (included SQL)
- Match each course & class nbr with a _Course Offering Id 18_
    - Some from CS will not have a _Course Offering Id 18_

## Production Day (You)
- Download files from Salesforce
    - Results
    - Offering
- Download files from Campus Solutions
- Archive a copy of each file
- In one `main` file with both Summer and Fall terms: 
    - Rename/add additional tabs (`data`, `summary`, `detail`)
    - `data`
        - Delete UFO?
        - Add in applicable columns (`Honors`, `Honors Course`, `URSP`)
            - Use a character of "1" to denote that this line meets column criteria
            - `Honors` and `Honors Course` can be determined on the sheet
            - Identify and add `URSP` separately
    - `summary`
        - A pivot of the `detail` tab
        - Determine the order of which this tab should be sorted
            - Order will be the least picked courses first.
    - `detail`
        - Delete UFO?
        - Add _Course Offering Id 18_ to each Class Num
        - Add `C_CAPACITY` column
        - Delete rows without a _Course Offering Id 18_

### Run the script 
- Place files into the `source_files` directory
- Run `main.py`
- Output files will be in the `output_files` directory

## Registration Day
### Select and Clean file after run (You)
    - Remove summer students who were moved to fall (checked for Summer Term Activation)
        - Can be done prior to running script. 
    - Remove students from both terms who did not have a term activation in either semester
        - Can be done prior to running script. 
    - Rename each CSV file to `qbuenrollfile####.csv` where #### is the term code
    - Structure for CSV sent to UFIT should be: 
        - `UFID, STRM, CLASS_NBR`

### Run in Campus Solutions (OUR/Quest/Query Based Update - QBU)
- Meet with Quest Admin, Registrar's Admin(s), and UFIT 
    - In 2024, it was Kendall, Chadia/Rachel, and Monica, respectively
    - In 2025, ... 
- Assign Quest Student Groups
    - This allows dropped seats to return to a reserved bucket
- Generally will excecute in CSMNT1 before running in Production
- Send file to Quest/Admin UFIT

## Additional tasks: 
- Send UFIDs for unassigned students to Quest Admin for the Spring Quest Hold