DELIMITER //

CREATE PROCEDURE ArchiveOldEntries()
BEGIN
    -- Inserts entries older than 48 hours into the archive table
    INSERT INTO speedtest_results_archive 
    SELECT * FROM speedtest_results
    WHERE timestamp < NOW() - INTERVAL 48 HOUR;

    -- Deletes those entries from the original table
    DELETE FROM speedtest_results 
    WHERE timestamp < NOW() - INTERVAL 48 HOUR;
END //

DELIMITER ;
