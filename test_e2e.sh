#!/bin/sh
exec docker run -it -v $(pwd)/e2e:/e2e --workdir /e2e\
 -e CYPRESS_VIDEO=false\
 -e CYPRESS_baseUrl=http://localhost:80\
 --network="host"\
 cypress/included:6.5.0
