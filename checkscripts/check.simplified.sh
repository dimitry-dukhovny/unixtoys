#!/bin/bash

# Configure this part
mydaemon=simplified

# Derived, but also configurable
outfile=/tmp/check.${mydaemon}
pidfile=/var/run/${mydaemon}/${mydaemon}.pid

# Bookkeeping
mypid=$$
myname=$0
mydir=`dirname ${myname}`

## Import node-specific configuration
#if [ ! -f ${mydir}/check.config.sh ]
#then
#    echo ${mydir}/check.config.sh is missing.  I am lost.
#    exit 255
#fi
#. ${mydir}/check.config.sh

# Import common functions after declaring configuration
if [ ! -f ${mydir}/check.functions.sh ]
then
    echo ${mydir}/check.functions.sh is missing.  I am lost.
    exit 255
fi
. ${mydir}/check.functions.sh


simplify() {
    tgt=${1:-httpd}
    egrep 'has [0-9]{1,} (reasons|failures)' /tmp/check.${tgt} | \
        perl -pe 's/^.*postfix/MAIL/g; \
        s/^.*stunnel/TUNNEL/g; \
        s/^.*httpd/WEBSERVER/g; \
        s/^.*reach/REACHBACK/g; \
        s/has ([0-9]{1,}) (reasons|failures).*/:\1/; \
        s/\[.*\]//; s/ //g; s/(:){2,}/:/g'
}

deadlines() {
    day=86400
    week=604800
    month=2600640
    datestamp=`date +%s`
    certdate=`strings /tmp/check.domain| egrep '^CERTIFICATE' | awk -F ' : | Subject:' '{print $2}' | xargs -i date --date="{}" '+%s'`
    domaindate=`strings /tmp/check.domain | egrep '^Registry|^Expir' | awk -F': ' '{print $NF}' | perl -pe 's/T.*Z//' | xargs -i date --date="{}" '+%s'`
    domainremain=$(( ${domaindate}-${datestamp} ))
    certremain=$(( ${certdate}-${datestamp} ))
    domaindays=$(( ${domainremain}/${day} ))
    certdays=$(( ${certremain}/${day} ))
    echo "DOMAIN_DAYS_REMAINING:${domaindays}"
    echo "CERTIFICATE_DAYS_REMAINING:${certdays}"
    egrep '^RESOLUTION:' /tmp/check.domain
}

main() {
    ${mydir}/check.apache.sh > /tmp/check.cron 2>&1
    ${mydir}/check.reach.sh >> /tmp/check.cron 2>&1
    ${mydir}/check.tunnels.sh >> /tmp/check.cron 2>&1
    ${mydir}/check.postfix.sh >> /tmp/check.cron 2>&1
    ${mydir}/check.domain.sh >> /tmp/check.cron 2>&1
    sleep 3

    bounce=0
    timestamp=`timestampit`
    output=( )
    for f in stunnel httpd postfix reach
    do
        #output=( "${output[@]}" "${timestamp}:`simplify ${f}`" )
        output=( "${output[@]}" "`simplify ${f}`" )
    done
    printf '%s\n' "${output[@]}"
    deadlines

}

touch ${outfile}; chmod 664 ${outfile}
touch ${outfile}.tmp; chmod 664 ${outfile}.tmp
main ${@} > ${outfile}.tmp 2>&1
mv -f ${outfile}.tmp ${outfile}
