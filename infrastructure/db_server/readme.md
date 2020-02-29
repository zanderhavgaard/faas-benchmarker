# terraform db server


terraform plan \
    -var do_token="$DO_TOKEN" \
    -var pub_key="$tf_db_pub_key" \
    -var pvt_key="$tf_db_pvt_key" \
    -var ssh_fingerprint="$tf_db_md5"
