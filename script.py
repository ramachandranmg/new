import boto3
import json

def lambda_handler(event, context):
    # Log the incoming event for debugging purposes
    print("Received event:", json.dumps(event))

    # Extract and parse the body if it is provided as a JSON string
    
    if "body" in event:
        try:
            body = json.loads(event["body"])
            source_bucket = body['source_bucket']
            destination_bucket = body['destination_bucket']
            game_name = body['game_name']
        except (KeyError, json.JSONDecodeError) as e:
            return {
                'statusCode': 400,
                'body': json.dumps(f'Missing or invalid parameter: {str(e)}')
            }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing required body in the request.')
        }

    s3 = boto3.client('s3')

    try:
        # List all objects in the source bucket with the given game_name as prefix
        response = s3.list_objects_v2(
            Bucket=source_bucket,
            Prefix=f"{game_name}/"
        )

        # Check if the folder exists
        if 'Contents' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps(f"Game folder '{game_name}' not found in bucket '{source_bucket}'.")
            }

        # Copy each object to the destination bucket
        for obj in response['Contents']:
            source_key = obj['Key']
            destination_key = source_key  # Maintain the same folder structure
            s3.copy_object(
                Bucket=destination_bucket,
                CopySource={'Bucket': source_bucket, 'Key': source_key},
                Key=destination_key
            )

        # Delete each object from the source bucket
        for obj in response['Contents']:
            source_key = obj['Key']
            s3.delete_object(
                Bucket=source_bucket,
                Key=source_key
            )

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps(f"Game folder '{game_name}' successfully moved from '{source_bucket}' to '{destination_bucket}'.")
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error occurred: {str(e)}")
        }

