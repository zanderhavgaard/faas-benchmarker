
def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html; charset=utf-8"
        },
        "body": "hello world2"
    }
