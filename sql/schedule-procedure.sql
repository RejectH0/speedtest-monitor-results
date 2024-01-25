CREATE EVENT archive_event
ON SCHEDULE EVERY 1 DAY -- Adjust the frequency as needed
DO
  CALL ArchiveOldEntries();
