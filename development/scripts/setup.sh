#!/bin/bash

MONGODB1=mongo1
MONGODB2=mongo2
MONGODB3=mongo3

echo "**********************************************" ${MONGODB1}
echo "Waiting for startup.."
until curl http://${MONGODB1}:27017/serverStatus\?text\=1 2>&1 | grep uptime | head -1; do
  printf '.'
  sleep 1
done

# echo curl http://${MONGODB1}:28017/serverStatus\?text\=1 2>&1 | grep uptime | head -1
# echo "Started.."


echo SETUP.sh time now: `date +"%T" `
mongosh --host ${MONGODB1}:27017 <<EOF
cfg = {
    _id: "rs0",
    members: [
        {
            _id: 0,
            host: "${MONGODB1}:27017",
        },
        {
            _id: 1,
            host: "${MONGODB2}:27017",
        },
        {
            _id: 2,
            host: "${MONGODB3}:27017",
        }
    ]
};
rs.initiate(cfg);
EOF
# rs.reconfig(cfg, { force: true });
# rs.slaveOk();
# db.getMongo().setReadPref('nearest');
# db.getMongo().setSlaveOk(); 