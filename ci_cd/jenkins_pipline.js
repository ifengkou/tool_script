node {
        def appName
        def version
        def mvnHome
        def remote = [:]
        def serverDir = '/data/micro-services/8082-data-api-jar'
        def repoUrl = 'http://git.analysys.cn/noah/data-api.git'
        def repoBranch = 'dev'
        def skipTests = true
        remote.name = 'test'
        remote.host = '192.168.8.77'
        remote.user = 'root'
        remote.password = 'Eguan)@)$'
        remote.allowAnyHosts = true
        stage('Preparation') {
            mvnHome = tool 'Maven'
        }
        catchError {
            stage('pull code'){
                //pull代码
                git branch: "$repoBranch", credentialsId: 'xielibo', url: "$repoUrl"
                pom = readMavenPom file: 'pom.xml'
                version = pom.version
                appName = pom.name

            }

            stage('Maven Package') {
                // Run the maven build
                sh "'${mvnHome}/bin/mvn' clean package -Ptest -DskipTests=$skipTests -U -B -q "
            }
            if(!skipTests){
                stage('Test reports collection'){
                    junit keepLongStdio: true, testResults: '**/target/surefire-reports/TEST-*.xml'
                }
            }
        
            stage('ssh deploy') {
                def dirArr = serverDir.split('/');
                def dirname = dirArr[dirArr.length-1]
                def isexists = sshCommand remote: remote, command: "ls ${serverDir}/jars/"
                if(isexists){
                    def curDay = new Date().format('yyyyMMdd')
                    def backupDir = serverDir + "/backup/"+ curDay
                    sshCommand remote: remote, command: "mkdir -p ${backupDir} && cp -r ${serverDir}/jars/*[!source].jar ${backupDir} "
                }

                def oldAppPid = sshCommand remote: remote, command: "ps -ef | grep ${dirname} | grep -v grep | awk '{print \$2}' | tr '\n' ' '"
                sshCommand remote: remote, command: "rm -rf ${serverDir}/jars/*"
                sshPut remote: remote, from: "fangzhou-data-api-server/target/fangzhou-ms-data-api.jar", into: "${serverDir}/jars/"
                if (oldAppPid) {
                    sshCommand remote: remote, command: "kill -9 ${oldAppPid}"
                }
                sshCommand remote: remote, command: "sh ${serverDir}/bin/startup.sh "
            }
        }
        emailext body: '${SCRIPT, template="build_notify_template.template"}', subject: '${DEFAULT_SUBJECT}', to: "xielibo@analysys.com.cn"

    }
