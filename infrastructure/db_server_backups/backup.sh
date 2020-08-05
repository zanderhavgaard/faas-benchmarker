access_key=$SPACE_KEY
secret_access_key=$SPACE_SECRET_KEY
space_name=$SPACE_NAME
db_user=$DB_SQL_USER
db_pass=$DB_SQL_PASS

timestamp=$(date -u +%d-%m-%Y_%H-%M-%S)
backup_dir="/home/ubuntu/backup"
sqldump_file="$timestamp-sqldump.sql"
tar_archive_name="$timestamp-backup.tar"
tar_archive="/home/ubuntu/$tar_archive_name"

mkdir "$backup_dir"

docker run \
        --rm \
        --network host \
        mysql:5.7 \
        mysqldump \
        -u$db_user \
        -p$db_pass \
        -h127.0.0.1 \
        Benchmarks > "$backup_dir/$sqldump_file"

cp -r /home/ubuntu/logs "$backup_dir/logs"

tar czf "$tar_archive" -C "$backup_dir" .

docker run \
        --rm \
        -e AWS_ACCESS_KEY_ID="$access_key" \
        -e AWS_SECRET_ACCESS_KEY="$secret_access_key" \
        --mount type=bind,source="/home/ubuntu",target="/home/arch/shared" \
        faasbenchmarker/s3cmd \
        s3cmd put "$tar_archive_name" "s3://$space_name/backup/"

rm -rf $backup_dir
rm $tar_archive
