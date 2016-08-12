#CSV Change detection system: a K.I.S.S. approach

The core of the solution is the bare metal diff Unix command, more specifically the Unified diff format which was being used (between the many cases) to patch Linux Kernel source code (1996 Linux Journal article, for those who want to spend a tear on his past :-) ).<br>
<br>
Basically, given two files, diff –u returns (simplified):<br>
```
 1,this line is the same in both files
-2,this line contains AAA in old file
+2,this line contains BBB in new file
-3,this line is just in old file
+4,this line is just in new file
```

Where<br>
•	Line with id 1 is in both file and is unchanged, so it has no leading sign<br>
•	Line with id 2 is different between old and new file, so it appears twice: once with the leading minus sign, with old values, and one with plus sign, with new values<br>
•	Line with id 3 is just in old file, so it appears just once, with a minus sign<br>
•	Line with id 4 is just in new file, so it appears just once, with a plus sign<br>

Which leads to the conclusion that (taking in consideration rows with a unique leading sign only)<br>
•	Lines with leading + are INSERTS<br>
•	Lines with leading – are DELETES<br>
•	Lines with same ID repeated are UPDATES (- sign line contains old values, + sign line contains new ones)<br>
<br>
Starting from those basic assumptions, generating deltas is pretty straight forward.<br>
<br>
I show here my quick and dirty solution, which should be good enough for a P.O.C.<br>
Many files attached, let’s start from the beginning:<br>
•	```prep.sh``` is used to do the real magic: calls the diff –u command, filters out lines without sign, and compresses output.<br>
    No magic, no 200 lines code with 20 pages manual (those numbers swap if code is in python :-P), no custom code, 99.9999999999% bugs free,  one line solution, runs everywhere with no change, works out-of-the-box, no external dependencies, no compiler/interpreter, …<br>
    Maybe the K.I.S.S.-est solution I’ve ever found :-)<br>
•	```postJSON.py``` takes the prep.sh output and elaborates it, producing a JSON row for every difference in file.<br>
    Please note this is just a P.O.C., there are many ways of writing this code better! :-)<br>
•	```postSQL.py``` is the very same, but produces a SQL file. Same terms & conditions apply :-)<br>
•	```randomData.entities.py``` creates CSVs with random data.<br>

Execution example:
```
mkdir DONTBACKUP/

./randomData.entities.py 200KTest.20010101 200000 DONTBACKUP/ &
./randomData.entities.py 200KTest.20111111 200000 DONTBACKUP/ 100000 &
wait

zcat DONTBACKUP/200Ktest.20010101.csv.gz | head -4
zcat DONTBACKUP/200Ktest.20111111.csv.gz | head -4
zcat DONTBACKUP/200Ktest.20010101.csv.gz | tail -3
zcat DONTBACKUP/200Ktest.20111111.csv.gz | tail -3

zcat DONTBACKUP/200Ktest.20010101.csv.gz | grep ^\"111111
zcat DONTBACKUP/200Ktest.20111111.csv.gz | grep ^\"111111


time ./prep.sh                            \
      DONTBACKUP/200Ktest.20010101.csv.gz \
      DONTBACKUP/200Ktest.20111111.csv.gz \
      > DONTBACKUP/200Ktest.diff.gz

zcat DONTBACKUP/200Ktest.diff.gz  | wc -l

time ./postJSON.py                  \
      200Ktest                        \
      DONTBACKUP/200Ktest.diff.gz     \
      DONTBACKUP/200Ktest.header.csv  \
      | gzip > DONTBACKUP/200Ktest.json.gz

time ./postSQL.py                  \
      200Ktest                        \
      DONTBACKUP/200Ktest.diff.gz     \
      DONTBACKUP/200Ktest.header.csv  \
      | gzip > DONTBACKUP/200Ktest.sql.gz


zcat DONTBACKUP/200Ktest.json.gz | wc -l

zcat DONTBACKUP/200Ktest.json.gz | grep \"111111\"

```