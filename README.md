# CSV Change detection system: a K.I.S.S. approach

The objective is to provide a simple and fast delta provider: the final objective is to show difference between different version of date, being them in different time (changes between yesterday and today) or between different machines.

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
<br>
<br>
A performance tests has been executed, logs below. <br>
Source CSV files with 200.000 rows each.<br>
Each CSV file has 5 columns, detailed in header files (attached as well):<br>
ID,LABEL,ENTITYNAME,ATTR0,ATTR1<br>
<br>
Files data are being created to reproduce the worst case scenario:<br>
•	File1 has rows with ID from 0 to 200000<br>
•	File2 has rows with ID from 100000 to 300000<br>
•	IDs from 100000 to 200000 are shared, but all attributes are changed<br>
<br>
So, to resume, we will have<br>
•	100k new IDs -> 100k “inserts”<br>
•	100k changed IDs -> 100k “updates”<br>
•	100k disappeared IDs -> 100k “deletes”<br>
<br>
Execution example:
```
date

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

echo ID,LABEL,ENTITYNAME,ATTR0,ATTR1 > DONTBACKUP/200Ktest.header.csv

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

time ./postpostCYPHER.py                  \
      200Ktest                        \
      DONTBACKUP/200Ktest.diff.gz     \
      DONTBACKUP/200Ktest.header.csv  \
      | gzip > DONTBACKUP/200Ktest.cy.gz

zcat DONTBACKUP/200Ktest.json.gz | wc -l

zcat DONTBACKUP/200Ktest.json.gz | grep \"111111\"

date

```


Execution output example:
```
$ date
Tue, Aug 16, 2016 12:05:42 PM


$ mkdir DONTBACKUP/



$ ./randomData.entities.py 200KTest.20010101 200000 DONTBACKUP/ &
[1] 1204

$ ./randomData.entities.py 200KTest.20111111 200000 DONTBACKUP/ 100000 &
[2] 9740

$ wait
[1]-  Done                    ./randomData.entities.py 200KTest.20010101 200000 DONTBACKUP/
[2]+  Done                    ./randomData.entities.py 200KTest.20111111 200000 DONTBACKUP/ 100000



$ zcat DONTBACKUP/200Ktest.20010101.csv.gz | head -4
id:ID(entity200KTest.20010101),:LABEL,entityName,attr0,attr1
"1","entity200KTest.20010101","Ent_1","attr0_527593","attr1_392675"
"2","entity200KTest.20010101","Ent_2","attr0_268000","attr1_20936"
"3","entity200KTest.20010101","Ent_3","attr0_912182","attr1_618131"

$ zcat DONTBACKUP/200Ktest.20111111.csv.gz | head -4
id:ID(entity200KTest.20111111),:LABEL,entityName,attr0,attr1
"100001","entity200KTest.20111111","Ent_100001","attr0_46062","attr1_466131"
"100002","entity200KTest.20111111","Ent_100002","attr0_226397","attr1_925353"
"100003","entity200KTest.20111111","Ent_100003","attr0_331961","attr1_362192"

$ zcat DONTBACKUP/200Ktest.20010101.csv.gz | tail -3
"199998","entity200KTest.20010101","Ent_199998","attr0_747332","attr1_56769"
"199999","entity200KTest.20010101","Ent_199999","attr0_693643","attr1_4989"
"200000","entity200KTest.20010101","Ent_200000","attr0_708617","attr1_734619"

$ zcat DONTBACKUP/200Ktest.20111111.csv.gz | tail -3
"299998","entity200KTest.20111111","Ent_299998","attr0_922601","attr1_176458"
"299999","entity200KTest.20111111","Ent_299999","attr0_588278","attr1_253595"
"300000","entity200KTest.20111111","Ent_300000","attr0_295461","attr1_36491"



$ zcat DONTBACKUP/200Ktest.20010101.csv.gz | grep ^\"111111
"111111","entity200KTest.20010101","Ent_111111","attr0_703808","attr1_665025"

$ zcat DONTBACKUP/200Ktest.20111111.csv.gz | grep ^\"111111
"111111","entity200KTest.20111111","Ent_111111","attr0_632068","attr1_273703"



$

$ time ./prep.sh                            \
>       DONTBACKUP/200Ktest.20010101.csv.gz \
>       DONTBACKUP/200Ktest.20111111.csv.gz \
>       > DONTBACKUP/200Ktest.diff.gz

real    0m1.385s
user    0m1.337s
sys     0m0.243s



$ zcat DONTBACKUP/200Ktest.diff.gz  | wc -l
400004



$ echo ID,LABEL,ENTITYNAME,ATTR0,ATTR1 > DONTBACKUP/200Ktest.header.csv



$ time ./postJSON.py                  \
>       200Ktest                        \
>       DONTBACKUP/200Ktest.diff.gz     \
>       DONTBACKUP/200Ktest.header.csv  \
>       | gzip > DONTBACKUP/200Ktest.json.gz

real    0m7.533s
user    0m11.902s
sys     0m0.357s



$ time ./postSQL.py                  \
>       200Ktest                        \
>       DONTBACKUP/200Ktest.diff.gz     \
>       DONTBACKUP/200Ktest.header.csv  \
>       | gzip > DONTBACKUP/200Ktest.sql.gz

real    0m3.638s
user    0m4.601s
sys     0m0.217s



$

$ zcat DONTBACKUP/200Ktest.json.gz | wc -l
3250019



$ zcat DONTBACKUP/200Ktest.json.gz | grep \"111111\"
   ,"sourceTablePk": "111111"
   ,"oldValuesCsv":["111111","entity200KTest.20010101","Ent_111111","attr0_703808","attr1_665025"]
   ,"oldValuesKv": [{"id": "111111"},{"label": "entity200KTest.20010101"},{"entityname": "Ent_111111"},{"attr0": "attr0_703808"},{"attr1": "attr1_665025"}]
   ,"oldValuesJson": {"id": "111111","label": "entity200KTest.20010101","entityname": "Ent_111111","attr0": "attr0_703808","attr1": "attr1_665025"}
   ,"newValuesCsv": ["111111","entity200KTest.20111111","Ent_111111","attr0_632068","attr1_273703"]
   ,"newValuesKv": [{"id": "111111"},{"label": "entity200KTest.20111111"},{"entityname": "Ent_111111"},{"attr0": "attr0_632068"},{"attr1": "attr1_273703"}]
   ,"newValuesJson": {"id": "111111","label": "entity200KTest.20111111","entityname": "Ent_111111","attr0": "attr0_632068","attr1": "attr1_273703"}



$ date
Tue, Aug 16, 2016 12:06:03 PM

```



