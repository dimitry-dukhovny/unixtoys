# check.apache.sh uses this to see if HTTPD is running
apachetcpport=443

# check.squid.sh uses this to see if the transparent proxy is running
squidtcpport=3128

# check.domain.sh uses this to fetch certificates and whois data
certsrcip=127.0.0.1
certport=443
#whoishost=128.14.134.134

# check.postfix.sh uses this to test for 220 messages from SMTP listeners
postfixports="SMTPS:465 SUBMISSION:587 SMTP:25"
