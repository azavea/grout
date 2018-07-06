function init_db() {
    #
    # Start the database service and poll it until it becomes available. Useful
    # for services that rely on the database, since by default Docker considers
    # a dependency service to have been satisfied when the container starts
    # up, not when its command has actually completed.
    #
    docker-compose up -d db
    INIT_COUNTER=15
    COUNTER=$INIT_COUNTER
    until
        [ $(docker-compose exec db pg_isready -d postgres -h "0.0.0.0" -p 5432 > /dev/null 2>&1 && echo $? || echo 1) -eq 0 ] ||
        [ $COUNTER -eq 0 ];
    do
        echo "Database unavailable -- attempting to connect (${COUNTER} attempts remaining)"
        COUNTER=$((COUNTER-1))
        sleep 1
    done

    if [ $COUNTER -eq 0 ];
    then
        echo "ERROR: Database service failed to start after ${INIT_COUNTER} seconds."
        echo "Adjust the timeout by increasing the INIT_COUNTER variable in scripts/server."
        exit 1
    fi
}
