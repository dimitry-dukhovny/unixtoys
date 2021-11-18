#!/bin/bash
###############################################################
# Title:   (U) check.functions.sh
# Source:  (U) Dimitry Dukhovny dimitry.dukhovny@gmail.com
# History: (U) 20180116.1956Z:  Added brief tcpdump for connection sampling
#          (U) 20170607.1014Z:  Initial version
# Purpose: (U) Allow sourcing for monitoring functions

# Time and output in a syslog format
datesay() {
    echo `date +'%b %e %R '` "${@}"
}

# Use datesay() to log something
logit() {
    logfile=${1:-/tmp/output.log}
    datesay ${@} >> ${logfile}
}

# Leave this alone.  Algebraic dates are cool.
timestampit() {
    #date -u +%s
    date +%Y%m%d%H%M%S
    return
}

# Daemon controls
## Restart daemon by description; must match init.d script name
bouncedaemon() {
    cat ${outfile} >> ${logfile}
    [ -f /etc/init.d/${mydaemon}.service ] && \
        initscript=/etc/init.d/${mydaemon}.service || \
        initscript=/etc/init.d/${mydaemon}
    datesay Stopping...
    ${initscript} stop
    sleep 1
    datesay Killing any leftovers...
    killdaemon ${mydaemon}
    datesay Starting...
    ${initscript} start
}

## Issue a kill to a running process by description
killdaemon() {
    victim=${1:-${mydaemon}}
    ps -ef | grep -v ${mypid} | grep -v grep | grep ${1:-${mydaemon}} | awk '{print $2}' | xargs kill -9
}

# This takes a port number as a parameter and returns a process or 0
getportholder() {
    targetport=${1:-443}
    # IP may be a regex
    ipaddress=${2:-NONE}
    if [ ${ipaddress} = NONE ]
    then
        portproc=`netstat -anp | egrep "tcp.*:${targetport} .*LISTEN" | awk '{print $NF}' | sed 's/\/.*//'`
    else
        portproc=`netstat -anp | egrep "tcp.*${ipaddress}:${targetport} .*LISTEN" | awk '{print $NF}' | sed 's/\/.*//'`
    fi
    portproc=${portproc:-0}
    echo ${portproc}
    return
}

# Fetches a certificate from an ssl dialog and extracts the CN and expiry
getcertstate() {
    tgtip=${1:-127.0.0.1}
    tport=${2:-443}
    certstate=`echo 'GET /' | openssl s_client -connect ${tgtip}:${tport} -showcerts 2>&1 | openssl x509 -noout -text | egrep -i '^\s*(Subject:.*CN=|Not.*After)'`
    certstate=`echo ${certstate} | perl -pe 'chomp'`
    echo ${certstate:-NONE}
}

# Extracts the probable domain from a URL as delivered by getcertstate().
getdomain() {
    certstate=${1:-NONE}
    [ "${certstate}" = NONE ] && return
    domain=`echo "${certstate}" | perl -pe 's/.*(?<=CN\=)(.*?\.\w\w\w)/\1/; chomp'`
    domain=`echo "${domain}" | perl -pe 's/^www\.//; chomp'`
    echo ${domain:-NONE}
}

# Fetches domain registration expiry from a variety of whois formats
getdomainexpiration() {
    domain=${1:-NONE}
    whoishost=${2:-NONE}
    if [ ${domain} = NONE ]
    then
        echo Unspecified domain
        return
    fi
    if [ ${whoishost} != NONE ]
    then
        domainexpiration=`whois -h ${whoishost} ${domain} | grep -i Expir`
    else
        domainexpiration=`whois ${domain} | grep -i Expir`
    fi
    echo ${domainexpiration:-NONE} | perl -pe '$CR=chr(13); s/${CR}.*//'
}

# Fetches IP and compares it to expected address
checkdomainresolution() {
    domain=${1:-www.google.com}
    resolver=${2:-8.8.8.8}
    resolvedip=`dig a +short ${domain} @${resolver}`
    echo ${resolvedip:-NONE} | egrep -c ${certsrcip}
}

# Check if a port is taking traffic
checknc() {
    targetport=${1:-80}
    echo | nc -v 127.0.0.1 ${targetport} 2> /dev/null | egrep -c "${targetport}.*succeeded\!"
}

# Run a cert-agnostic curl and count the characters we get back
checkcurl() {
    curl -k ${1} 2> /dev/null| wc -c
}

# See if a port is a real ESMTP port
checksmtp() {
    thost=${1:-localhost}
    tport=${2:-25}
    smtpresponse=`python -c 'import smtplib, sys; s=smtplib.SMTP(timeout=5); v1=s.connect(host=sys.argv[1], port=sys.argv[2]); print str(v1[0])' ${thost} ${tport} 2> /dev/null`
    echo ${smtpresponse:-0}
}

# Same as checksmtp(), but with TLS
checksmtpssl() {
    thost=${1:-localhost}
    tport=${2:-25}
    smtpresponse=`python -c 'import smtplib, sys; s=smtplib.SMTP_SSL(timeout=5); v1=s.connect(host=sys.argv[1], port=sys.argv[2]); print str(v1[0])' ${thost} ${tport} 2> /dev/null`
    echo ${smtpresponse:-0}
}

# Port check with openssl s_client
checkssl() {
    echo | openssl s_client -connect 127.0.0.1:${1:-443} 2>&1 | grep -c 'SSL handshake has read'
}

# Echo how many instances of a pid are in the process table.
#  Values should be 0 or 1.  Anything else is madness.
isrunningpid() {
    pidtocheck=${1}
    ps -eo pid | egrep -c "^\s*${pidtocheck}$"
}

# Start a tcpdump before a command and stop it afterward
dumpwrap() {
    dumpfile=/tmp/tcpdump.`timestampit`
    dumpcount=60
    dumphost=${1:-0.0.0.0}; shift
    dumpport=${1:-80}; shift
    dumpexec=${@:-checkssl}
    tcpdump -nvvvXXi any host ${dumphost} and port ${dumpport} -w ${dumpfile} 2> /dev/null &
    dumppid=$!
    datesay TCP dumping to ${dumpfile} for ${dumpcount} secs on ${dumpexec}
    sleep 2
    ${dumpexec} &
    execpid=$!
    while [ `isrunningpid ${execpid}` -gt 0 -a ${dumpcount} -gt 0 ]
    do
        let dumpcount--
        echo -n .
        sleep 1
    done
    echo

    [ `isrunningpid ${execpid}` -gt 0 ] && kill -2 ${execpid}
    let dumpcount=5
    while [ `isrunningpid ${execpid}` -gt 0 -a ${dumpcount} -gt 0 ]
    do
        let dumpcount--
        echo -n .
    done
    [ `isrunningpid ${execpid}` -gt 0 ] && kill -9 ${execpid}

    [ `isrunningpid ${dumppid}` -gt 0 ] && kill -2 ${dumppid}
    let dumpcount=5
    while [ `isrunningpid ${dumppid}` -gt 0 -a ${dumpcount} -gt 0 ]
    do
        let dumpcount--
        echo -n .
    done
    [ `isrunningpid ${dumppid}` -gt 0 ] && kill -9 ${dumppid}
    sleep 1
    tcpdump -nnvvvr ${dumpfile}
    rm -f ${dumpfile}
}

# Dump outfile contents to the defined logfile
logmyoutfile() {
    cat ${outfile:-/tmp/outfile.txt} >> ${logfile:-/tmp/output.log}
}

main() {
    [ "s${@}s" != "ss" ] && datesay ${@}
}

main ${@}
