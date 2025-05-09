Example command
``` bash
python3 zBHPasswordAnalysus.py --uri bolt:localhost:7687 --user neo4j --password neo4j! --password-file passwords.txt --sort username --filter 'Welcome123,Password1,!ChangeMeNow123!,Leaver123,Welcome1' --min-password-length 12 --output-file output.xlsx --strict
```
