epoch=$(date +%s000)
mykey=$ZIA_API_KEY

key=""

n=${epoch:(-6)}
o=`printf %06d $((10#$n >> 1))`

for ((i=0; i<${#n}; i++)); do
    tmp=${n:$i:1}
    key+=${mykey:$tmp:1}
done

for ((j=0; j<${#o}; j++)); do
    tmp=${o:$j:1}+2
    key+=${mykey:$tmp:1}
done

data='{"username":"'$ZIA_USERNAME'","password":"'$ZIA_PASSWORD'","apiKey":"'$key'","timestamp":'$epoch'}'
authurl=https://zsapi."$ZIA_CLOUD".net/api/v1/authenticatedSession
activateurl=https://zsapi."$ZIA_CLOUD".net/api/v1/status/activate

curl --location $authurl \
--header 'Content-Type: application/json' \
--header 'Server: Zscaler' \
--data-raw $data \
--cookie-jar 'cookie.txt'

curl --location $activateurl --request POST  \
--header 'Content-Type: application/json' \
--cookie 'cookie.txt'