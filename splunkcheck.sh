#!/bin/bash

SPLUNKDIR=${1:-/opt/splunk}

myname=`basename ${0}`
mylabel=${2:-${myname}}
logout=/tmp/${mylabel}.out
logerr=/tmp/${mylabel}.err

# Generated from Jinja2 template runcheck.sh.j2 by dimitry
OUTPUT() {
  echo ${@}`tput sgr0`
}

GREENOUT() {
  OUTPUT -e "\E[32;40m"${@}
  tput sgr0
}

REDOUT() {
  OUTPUT -e "\E[31;40m"${@}
  tput sgr0
}

info() {
  GREENOUT "${mylabel}:  ${@}" >&2
}

err() {
  REDOUT "${mylabel}:  ${@}" >&2
}

diskpercentcheck() {
  # Takes file system and max percentage in use as parameters
  fs=${1:-/opt}
  max=${2:-90}
  if [ ! -d ${fs} ]
  then
    err "Not found or not mounted something as ${fs}"
    echo 1
  else
    percentused=`df -h ${1:-/opt} 2> /dev/null | \
      grep -v Filesystem 2> /dev/null | \
      awk '{gsub(/%/,""); print $5}' 2> /dev/null`
    percentused=${percentused:-NONE}
    if [ "${percentused}" == "NONE" ]
    then
      err "Could not calculate ${fs} use or missing df, grep, or awk."
      echo 1
    elif [ ${percentused} -gt ${max} ]
    then
      err "${fs} exceeds ${max}% usage at ${percentused}%"
      echo 1
    else echo 0
    fi
  fi
}

portpidcheck() {
  # Takes a single parameter of a unique process name
  processname=${1:-httpd}
  checkpid=`pgrep -xo ${processname} 2> /dev/null`
  if [ "x${checkpid}x" == "xx" ]
  then
    err "No ${processname} PID found."
    echo 1
  else
    checkport=`sudo netstat -plant 2> /dev/null | \
      egrep "LISTEN\s*${checkpid}\/${processname}" | \
      awk '{print $4}' \
      || echo NONE`
    if [ "${checkport:-NONE}" == "NONE" ]
    then
      err "Found ${processname} PID, but no port; \
        or not root or missing sudo or netstat."
      echo 1
    else
      info "${processname} listens on ${checkport}"
      echo 0
    fi
  fi
}

splunklicensecheck() {
  result=`${SPLUNKDIR}/bin/splunk search \
   'index=_internal source="*license_usage.*" earliest=@d  | \
   eval GB=round(b/1024/1024/1024,1) | \
   eval LGB=round(poolsz/1024/1024/1024,1) | \
   stats sum(GB) AS GB_Today values(LGB) AS Limit_GB by pool  | \
   eval License_Percent_Usage=round(GB_Today/Limit_GB * 100,1)  | \
   eval Violation_Risk = if((round((((tonumber(strftime(now(), "%H")) * 60) + \
   tonumber(strftime(now(),"%M"))) / 1440)* 100,1)) \
   < License_Percent_Usage, "Yes", "No")' | egrep 'Yes | No'`
  licenserisks=`echo ${result} | grep -c "Yes"`
  if [ ${licenserisks:-0} -ne 0 ]
  then
    err ${result}
    echo ${licenserisks}
  else
    info ${result}
    echo ${licenserisks}
  fi
}

swapcheck() {
  # Checks percent of all swap available against a max in-use parameter
  swapmax=${1:-90}
  used=0
  for f in `swapon --show=USED --bytes --noheadings 2> /dev/null`
  do
    used=$(( ${used:-0} + ${f:-0}))
  done
  size=0
  for f in `swapon --show=SIZE --bytes --noheadings 2> /dev/null`
  do
    size=$(( ${size:-0} + ${f:-0}))
  done
  if [ ${size} -eq 0 ]
  then
    info "No swap found.  This might be OK."
    echo 0
  else
    swappercent=$(( ${used} / ${size} ))
    if [ ${swappercent} -ge ${swapmax} ]
    then
      err "Swap ${used} / ${size} is ${swappercent}, more than ${swapmax}"
      echo 1
    else echo 0
    fi
  fi
}

statecheck() {
  # Blind state check with a command string as a parameter
  runable=${@}
  ${runable} > /dev/null 2>&1 && state=0 || state=1
  echo ${state}
}

usage() {
  REDOUT "Usage:"
  echo "${0} <SPLUNKDIR> [<LABEL>]"
  echo "  SPLUNKDIR is required, but is usually /opt/splunk"
  echo "  LABEL is optional and determines the output file names in /tmp"
}

main() {
  MONGOFAIL=`portpidcheck mongod`
  APPFAIL=`portpidcheck splunkd`
  DISKFAIL=`diskpercentcheck ${SPLUNKDIR} 80`
  SPLUNKFAIL=`statecheck ${SPLUNKDIR}/bin/splunk status`
  SPLUNKLICFAIL=`splunklicensecheck`
  SWAPFAIL=`swapcheck 90`
  
  [ ${MONGOFAIL} -gt 0 ] && err "MONGOFAIL ${MONGOFAIL}" || \
    info "MONGOFAIL ${MONGOFAIL}"
  [ ${APPFAIL} -gt 0 ] && err "APPFAIL ${APPFAIL}" || \
    info "APPFAIL ${APPFAIL}"
  [ ${DISKFAIL} -gt 0 ] && err "DISKFAIL ${DISKFAIL}" || \
    info "DISKFAIL ${DISKFAIL}"
  [ ${SPLUNKFAIL} -gt 0 ] && err "SPLUNKFAIL ${SPLUNKFAIL}" || \
    info "SPLUNKFAIL ${SPLUNKFAIL}"
  [ ${SPLUNKLICFAIL} -gt 0 ] && err "SPLUNKLICFAIL ${SPLUNKLICFAIL}" || \
    info "SPLUNKLICFAIL ${SPLUNKLICFAIL}"
  [ ${SWAPFAIL} -gt 0 ] && err "SWAPFAIL ${SWAPFAIL}" || \
    info "SWAPFAIL ${SWAPFAIL}"
  echo "FAILURE_REASONS $(( ${MONGOFAIL:-0} + \
    ${APPFAIL} + \
    ${DISKFAIL:-0} + \
    ${SPLUNKFAIL:-0} + \
    ${SWAPFAIL:-0} ))"
}

[ ${#} -lt 1 ] && usage || main > ${logout} 2> ${logerr}

