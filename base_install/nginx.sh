LC_ALL="en_US.UTF-8"
#!/bin/bash
RED="\033[31m"      # Error message
GREEN="\033[32m"    # Success message
YELLOW="\033[33m"   # Warning message
BLUE="\033[36m"     # Info message
PLAIN='\033[0m'
BT='false'

checkSystem() {
    result=$(id | awk '{print $1}')
    if [[ $result != "uid=0(root)" ]]; then
        colorEcho $RED " 请以root身份执行该脚本"
        exit 1
    fi

    res=`which yum 2>/dev/null`
    if [[ "$?" != "0" ]]; then
        res=`which apt 2>/dev/null`
        if [[ "$?" != "0" ]]; then
            colorEcho $RED " 不受支持的Linux系统"
            exit 1
        fi
        PMT="apt"
        CMD_INSTALL="apt install -y "
        CMD_REMOVE="apt remove -y "
        CMD_UPGRADE="apt update; apt upgrade -y; apt autoremove -y"
    else
        PMT="yum"
        CMD_INSTALL="yum install -y "
        CMD_REMOVE="yum remove -y "
        CMD_UPGRADE="yum update -y"
    fi
    res=`which systemctl 2>/dev/null`
    if [[ "$?" != "0" ]]; then
        colorEcho $RED " 系统版本过低，请升级到最新版本"
        exit 1
    fi
}

colorEcho() {
    echo -e "${1}${@:2}${PLAIN}"
}

installNginx() {
    echo ""
    colorEcho $BLUE " install nginx..."
    check_res=`which nginx 2>/dev/null`
    if [[ "$?" == "0" ]]; then
        colorEcho $BLUE " nginx alread installed..."
    else
        if [[ "$BT" = "false" ]]; then
            if [[ "$PMT" = "yum" ]]; then
                $CMD_INSTALL epel-release
                if [[ "$?" != "0" ]]; then
                    echo '[nginx-stable]
    name=nginx stable repo
    baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
    gpgcheck=1
    enabled=1
    gpgkey=https://nginx.org/keys/nginx_signing.key
    module_hotfixes=true' > /etc/yum.repos.d/nginx.repo
                fi
            fi
            $CMD_INSTALL nginx
            if [[ "$?" != "0" ]]; then
                colorEcho $RED " Nginx install failed"
                exit 1
            fi
            systemctl enable nginx
        else
            res=`which nginx 2>/dev/null`
            if [[ "$?" != "0" ]]; then
                colorEcho $RED " 您install 了宝塔，请在宝塔后台install nginx后再运行本脚本"
                exit 1
            fi
        fi
    fi
}

startNginx() {
    if [[ "$BT" = "false" ]]; then
        systemctl start nginx
    else
        nginx -c /www/server/nginx/conf/nginx.conf
    fi
}

stopNginx() {
    if [[ "$BT" = "false" ]]; then
        systemctl stop nginx
    else
        res=`ps aux | grep -i nginx`
        if [[ "$res" != "" ]]; then
            nginx -s stop
        fi
    fi
}

