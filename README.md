# Quest Survey Class Assignment Algorithm
Hello from 2025. This is Python code to take input data from a Salesforce (TFA) survey and distribute students randomly within their matriculation semester.
The code was run by the Quest Director in Ruby, but was re-coded in Python by Joe Uong, Data Analyst in CLAS and Preview Troubleshooter, in 2024. 
Below are the steps to prep the files in order to complete this process. 
Direct access to Course data is helpful but not mandatory since Quest Admin (currently Kendall Kroger) can assist with section info (such as name and capacity)

## Prep
### Need an Excel file with these sheets (sample has required columns highlighted in yellow):
    - Sheet1 (data from the survey):
        - UFID
        - Course Offering SFID
            - Needs to be the 18-character version
        - Topic
    - Sheet2 (summary data, aggregate data of Sheet 3): 
        - Course Offering SFID
            - Needs to be the 18-character version
        - CAPACITY 
            - Sum of all sections of the course using Sheet3
    - Sheet3 (data from SOC, requires student records access. Need to match TOPIC with CS name and translate SFID)
        - Course Offering SFID
            - Needs to be the 18-character version
        - Topic
        - CN
        - C_CAPACITY

### 

## Run

## Campus Solutions


## Additional tasks: 
- removed summer students who were moved to fall (checked for Summer Term Activation)
- removed students from both terms who did not have a term activation in either semester
- Rename the CSV file
- CSV Structure should be: 
- Need to add Student Groups in beforehand
- Watch out for UFO students