#!/usr/bin/env bash

DIR=$(dirname "$(readlink -f "$0")");

scp -r josefkolar.cz:/home/ifj/ifj.cz/media josefkolar.cz:/home/ifj/ifj.cz/db.sqlite3 ${DIR}/../;