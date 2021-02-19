#!/bin/sh
exec docker exec -it titanic /bin/sh -c "flask db migrate; flask db upgrade"
