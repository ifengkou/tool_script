#!/bin/bash
#description:这个脚本通过读取一个文件内容，来实现自动部署，避开由于用户权限问题导致的进程无法杀死，文件无法删除
#author:huangjunfeng
#set -x
#export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/root/bin
basepath=$(cd `dirname $0`; pwd)
while [ 1 == 1 ]
do

        #待处理任务文件
        taskFile=$basepath"/task"
        ##定义需要查看的文件
        taskInfo=$(cat $taskFile)
        echo $taskInfo 
        ##定义存放modify值的文件
        logFile=$basepath"/run.log"
         
        ##判断任务文件是否为空
        if [ "$taskInfo" =  ""  ]; then
#           echo "n"
            echo ""
        else
			# 0.读取任务之后立即清除任务
			echo "[`date '+%Y-%m-%d %H:%M:%S'`]                立即清除任务文件！ " >> $logFile
            echo "" > $taskFile
			echo "[`date '+%Y-%m-%d %H:%M:%S'`]                start deploy ....... " >> $logFile
			echo "[`date '+%Y-%m-%d %H:%M:%S'`]                taskInfo   :   "$taskInfo >> $logFile
			#info = dirname + " " + sourcePath + " " + toPath + " " + removePath;
			
			#tomcat文件名称，如：8097-qianfan-4a-8705-2G
			dirname=$(echo $taskInfo | awk '{split($0,arr," ");print arr[1]}')
			echo "[`date '+%Y-%m-%d %H:%M:%S'`]                dirname   :   "$dirname >> $logFile
			
			#新war包存放绝对路径，如：/data/backup/qianfan-4a-prod/backend/20170707182839/ROOT.war
			sourcePath=$(echo $taskInfo | awk '{split($0,arr," ");print arr[2]}')
			echo "[`date '+%Y-%m-%d %H:%M:%S'`]                sourcePath   :   "$sourcePath >> $logFile

			
			#tomcat中webapps绝对路径 ，如：/data/tomcat/8097-qianfan-4a-8705-2G/webapps
			toPath=$(echo $taskInfo | awk '{split($0,arr," ");print arr[3]}')
			echo "[`date '+%Y-%m-%d %H:%M:%S'`]                toPath   :   "$toPath >> $logFile
			
			#需要删除的文件绝对路径 如： /data/tomcat/8097-qianfan-4a-8705-2G/webapps/ROOT*
			removePath=$(echo $taskInfo | awk '{split($0,arr," ");print arr[4]}')
			echo "[`date '+%Y-%m-%d %H:%M:%S'`]                removePath   :   "$removePath >> $logFile

			# 1.执行shutdown命令
			#shutdownPath=$toPath"/../bin/shutdown.sh"
			#echo "[`date '+%Y-%m-%d %H:%M:%S'`]                shutdownPath   :   "$shutdownPath >> $logFile
			#$shutdownPath
			#sleep 2
			
			# 2. 杀死进程
			pid=$(ps -ef | grep $dirname | grep -v grep | awk '{print $2}')
			echo "pid:"$pid
			if [ "$pid" !=  ""  ]; then
				ps -ef | grep $dirname | grep -v grep | awk '{print $2}' | xargs kill -9
				sleep 1
				echo "ps -ef | grep $dirname | grep -v grep | awk '{print \$2}' | xargs kill -9"
				echo "[`date '+%Y-%m-%d %H:%M:%S'`]                ps -ef | grep $dirname | grep -v grep | awk '{print \$2}' | xargs kill -9" >> $logFile
			fi
            
			
			# 3. 移除webapps目录下源文件
			#处理备份文件夹backup
			backupDir=$toPath"/../backup"
			if [ ! -d "$backupDir" ]; then
				echo "[`date '+%Y-%m-%d %H:%M:%S'`]                mkdir $backupDir" >> $logFile
				mkdir $backupDir
			fi
			#移除备份目录下的所有文件
			oldBackupFiles=$backupDir"/*"
			rm -rf $oldBackupFiles
			echo "[`date '+%Y-%m-%d %H:%M:%S'`]                rm -rf $oldBackupFiles" >> $logFile
			#将webapp目录下的所有文件移到备份目录下
			oldWarFiles=$toPath"/*"
			
			files=`ls $oldWarFiles`
			if [ -z "$files" ]; then
				echo "Folder $oldWarFiles is empty!"
			else
				echo "Folder $oldWarFiles is not empty."
				mv $oldWarFiles $backupDir
				echo "mv $oldWarFiles $backupDir"
				echo "[`date '+%Y-%m-%d %H:%M:%S'`]                mv $oldWarFiles $backupDir" >> $logFile
			fi
			
						
			# 4.将本次需要发布的文件拷贝到webapp目录下
			cp -r $sourcePath $toPath
			echo "[`date '+%Y-%m-%d %H:%M:%S'`]                cp -r $sourcePath $toPath" >> $logFile
			sleep 2
						
			# 5. 启动服务
			startupPath=$toPath"/../bin/startup.sh"
			echo "$startupPath"
			echo "[`date '+%Y-%m-%d %H:%M:%S'`]                startupPath   :   $startupPath" >> $logFile
			$startupPath
			
			echo "[`date '+%Y-%m-%d %H:%M:%S'`]                deploy end！ " >> $logFile
			echo "" >> $logFile
			echo "" >> $logFile
			echo "" >> $logFile
			echo "" >> $logFile
			echo "" >> $logFile
			echo "" >> $logFile


        fi
        sleep 1
done


