#!/bin/bash

zdiff -u --suppress-common-lines $1 $2 | grep ^[+-] | gzip

