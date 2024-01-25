#!/bin/bash

# Function to delete old files
delete_old_files() {
    local directory=$1
    local pattern=$2
    local age_minutes=$3

    echo "Searching for files matching the pattern $pattern in $directory that are older than $age_minutes minutes."

    # Find files matching the pattern and older than specified age
    local files_to_delete=$(find "$directory" -name "$pattern" -type f -mmin +"$age_minutes")

    if [ -z "$files_to_delete" ]; then
        echo "No files to delete."
    else
        echo "Files to be deleted:"
        echo "$files_to_delete"

        # Actual deletion
        echo "Deleting files..."
        echo "$files_to_delete" | xargs rm
        echo "Files deleted."
    fi
}

# Main function
main() {
    # Directory where the files are located
    local directory="/usr/local/speedtest-monitor-results/static/images"

    # Pattern of the files to be deleted
    local pattern="*-speedtest-[0-9][0-9][0-1][0-9][0-3][0-9]*.png"

    # Age in minutes for file deletion (12 hours)
    local age_minutes=720

    delete_old_files "$directory" "$pattern" "$age_minutes"
}

# Execute main function
main
