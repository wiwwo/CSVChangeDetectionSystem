The core of the solution is the bare metal diff Unix command, more specifically the Unified diff format which was being used (between the many cases) to patch Linux Kernel source code (1996 Linux Journal article, for those who want to spend a tear on his past  ).

Basically, given two files, diff –u returns (simplified):

1,this line is the same in both files
-2,this line contains AAA in old file
+2,this line contains BBB in new file
-3,this line is just in old file
+4,this line is just in new file


Where
•	Line with id 1 is in both file and is unchanged, so it has no leading sign
•	Line with id 2 is different between old and new file, so it appears twice: once with the leading minus sign, with old values, and one with plus sign, with new values
•	Line with id 3 is just in old file, so it appears just once, with a minus sign
•	Line with id 4 is just in new file, so it appears just once, with a plus sign

Which leads to the conclusion that (taking in consideration rows with a unique leading sign only)
•	Lines with leading + are INSERTS
•	Lines with leading – are DELETES
•	Lines with same ID repeated are UPDATES (- sign line contains old values, + sign line contains new ones)

Starting from those basic assumptions, generating deltas is pretty straight forward.

I show here my quick and dirty solution, which should be good enough for a P.O.C.
Many files attached, let’s start from the beginning:
•	prep.sh is used to do the real magic: calls the diff –u command, filters out lines without sign, and compresses output.
No magic, no 200 lines code with 20 pages manual (those numbers swap if code is in python ), no custom code, 99.9999999999% bugs free,  one line solution, runs everywhere with no change, works out-of-the-box, no external dependencies, no compiler/interpreter, …
Maybe the K.I.S.S.-est solution I’ve ever found 
•	postJSONv6.py takes the prep.sh output and elaborates it, producing a JSON row for every difference in file.
Please note this is just a P.O.C., there are many ways of writing this code better! 
•	postSQLv2.py is the very same, but produces a SQL file. Same terms & conditions apply 
•	randomData.entities.py creates CSVs with random data.