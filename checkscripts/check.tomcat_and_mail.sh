#!/bin/bash

# Configure this part
mydaemon=tomcat
tcpport=8080
testuri=mywebapp
responsestring="This can be a regex."

# Derived, but also configurable
outfile=/tmp/check.${mydaemon}
pidfile=/var/run/${mydaemon}/${mydaemon}.pid

# Bookkeeping
mypid=$$
myname=$0

# Leave this alone.  Algebraic dates are cool.
timestampit() {
        #date -u +%s
        date +%Y%m%d%H%M%S
        return 0
}

# Modify this.  I used httpd as an example.
bouncedaemon() {
        logger -f ${outfile}
        echo Stopping...
        /etc/init.d/${mydaemon} stop
        sleep 1
        echo Killing any leftovers...
        killdaemon ${mydaemon}
        echo Starting...
        /etc/init.d/${mydaemon} start
}

killdaemon() {
        victim=${1:-${mydaemon}}
        ps -ef | grep -v ${mypid} | grep -v grep | grep ${1:-${mydaemon}} | awk '{print $2}' | xargs kill -9
}

# This takes a port number as a parameter and returns a process or 0
getportholder() {
        targetport=${1:-443}
        portproc=`netstat -anp | egrep "tcp.*:${targetport} .*LISTEN" | awk '{print $NF}' | sed 's/\/.*//'`
        portproc=${portproc:-0}
        echo ${portproc}
        return ${portproc}
}

checkssl() {
        echo 'GET /' | openssl s_client -connect 127.0.0.1:${1:-443} 2>&1 | grep -c 'SSL handshake has read'
}


checkfordata() {
    # This may need change.
    curl -k http://127.0.0.1:${tcpport}/${testuri} 2>&1 | egrep -c "${responsestring}"
}

smtpcheck() {
    checkstring=${1:-CHECKSTRING}
    echo ${checkstring} | mail -s "Test Postfix" root@localhost
    sleep 2
    egrep -c ${checkstring} /var/spool/mail/root
}

#httpdcount=`ps -ef | grep -v $$ | grep -v grep | egrep '\/usr\/sbin\/httpd' | wc -l`

main() {
        bounce=0
        timestamp=`timestampit`
        echo ${timestamp}
        echo Looking for pidfile ${pidfile}
        ls -l ${pidfile}
        if [ -f ${pidfile} ]; then oldpid=`cat ${pidfile}`; else oldpid=0; fi
        echo PID claims to be ${oldpid}
        [ ${oldpid} -eq 0 ] && bounce=$(( ${bounce} + 1 ))
        portholder=`getportholder ${tcpport}`
        echo PID ${portholder} owns TCP port ${tcpport}
        [ ${portholder:-0} -eq 0 ] && bounce=$(( ${bounce} + 1 ))
        [ ${portholder:-0} -ne ${oldpid:-0} ] && bounce=$(( ${bounce} + 1 ))

        # Start of SSL dialog.  Turn this off if you don't need it.
        sslresponse=`checkssl ${tcpport}`
        echo GOT ${sslresponse} SSL handshake\(s\) from ${tcpport}
        [ ${sslresponse:-0} -eq 0 ] && bounce=$(( ${bounce} + 1 ))

        # Regex web check.  Turn this off if you don't need it.
        datacount=`checkfordata`
        echo GOT ${datacount} instances of ${responsestring} from ${mydaemon}
        [ ${datacount} -lt 1 ] && bounce=$(( ${bounce} + 1 ))

        # SMTP check.  Turn this off if you don't need it.
        mailresponse=`smtpcheck ${timestamp}
        echo GOT ${mailresponse} from SMTP check
        [ ${mailresponse} -lt 1 ] && bounce=$(( ${bounce} + 1 ))

        echo ${mydaemon} has ${bounce} reasons to restart!
        [ ${bounce} -gt 0 ] && bouncedaemon
}

touch ${outfile}; chmod a+r ${outfile}
main ${@} > ${outfile} 2>&1
