#! /bin/sh
basepath=$(cd `dirname $0`; pwd)
autoRunPath=$basepath"/autoRun.sh"
chmodPath=$basepath"/*"
chmod 777 $chmodPath
nohup $autoRunPath > /dev/null  &
