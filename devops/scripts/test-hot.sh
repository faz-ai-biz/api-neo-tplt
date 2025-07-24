#!/bin/bash

ptw --onpass "echo 'Tests passed!'" \
--onfail "echo 'Tests failed!'; clear;" \
--nobeep --clear /app/tests/ /app/src/
