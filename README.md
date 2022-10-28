**Requirements:**
+ Flask (API)
+ PyJWT (API)
+ requests

**Structure:** 
+ **API.py**  
    + Runs and controls the API  
+ **BusinessLogic.py**
    + Handles business logic and DB interactions
+ **Database.py**
    + Used by BusinessLogic.py to directly interact with the persistence layer
+ **Main_CLI.py**  
    + Command line interface implementation


<p><b>How to run</b>:

+ Run the API in one session
    + This session must stay running for API requests to be processed
    + Execute the API file through 'python API.py'
+ (OPTIONAL) Run Main_CLI.py
    + Could run anything that hits the localhost API
    
**Notes**
+ Flask can hang sometimes and not process requests
    + To fix this, stop the flask session with a keyboard interrupt (Ctrl+C) and restart

