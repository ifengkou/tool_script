#!/usr/bin/env bash

basepath=$(cd `dirname $0`; pwd)

while true
do
    procnum=`ps -ef|grep "服务名称"|grep -v grep|wc -l`
    if [ $procnum -eq 0 ]
    then
        执行命令
        echo `date +%Y-%m-%d` `date +%H:%M:%S`  "restart 服务" >>$basepath/shell.log
    fi
    sleep 5
done