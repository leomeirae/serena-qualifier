#!/bin/sh
set -e

# Wait for 15 seconds to allow other services to be ready
sleep 15
 
# Start Kestra
/app/kestra server standalone 