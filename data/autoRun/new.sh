#!/bin/bash
#x="a b c d"

#echo $x | awk '{split($0,arr," ");for(i in arr) print i,arr[i]}'

basepath=$(cd `dirname $0`; pwd)
taskFile=$basepath"/test"
taskInfo=$(cat $taskFile)
echo $taskInfo 
echo $taskInfo | awk '{split($0,arr," ");dirname=arr[1];print dirname}'
dirname=$(echo $taskInfo | awk '{split($0,arr," ");print arr[1]}')
echo "[`date '+%Y-%m-%d %H:%M:%S'`]                dirname   :   "$dirname

