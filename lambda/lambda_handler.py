import json
import os
import boto3
from uuid import uuid4
from boto3.dynamodb.conditions import Attr


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def get_task(event, context):
    try:
        if len(event["pathParameters"]["taskId"]) != 36:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "The ID has been provided incorrectly."})
            }
        taskId = event["pathParameters"]["taskId"]
        body = table.get_item(
            Key={"taskId": taskId}
        )
        res = body["Item"]
        return {
            "statusCode": 200,
            "body": json.dumps({
                "taskId": res["taskId"],
                "title": res["title"],
                "description": res["description"],
                "status": res["status"]
            })
        }
    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)})
        }

def create_task(event, context):
    try:
        task = json.loads(event["body"])
        if "title" not in task or "status" not in task:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required attributes."})
            }
        new_task = {
            "taskId": str(uuid4()),
            "title": task["title"],
            "description": task["description"],
            "status": task["status"]
        }
        res = table.scan(FilterExpression=Attr("title").eq(new_task["title"]))
        if res["Items"]:
            raise Exception("Task already exists.")
        table.put_item(Item=new_task)
        return {
            "statusCode": 201,
            "body": json.dumps({"message": f"Task {new_task['taskId']} added successfully"})
        }
    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)})
        }

def update_task(event, context):
    try:
        if len(event["pathParameters"]["taskId"]) != 36:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "The ID has been provided incorrectly."})
            }
        taskId = event["pathParameters"]["taskId"]
        task = json.loads(event["body"])
        table.get_item(Key={"taskId": taskId})
        table.update_item(
            Key={"taskId": taskId},
            UpdateExpression="SET #T = :t, #D = :d, #S = :s",
            ExpressionAttributeNames={
                "#T": "title",
                "#D": "description",
                "#S": "status"
            },
            ExpressionAttributeValues={
                ":t": task["title"],
                ":d": task["description"],
                ":s": task["status"]
            }
        )
        return {
            "statusCode": 201,
            "body": json.dumps({"message": f"Task {taskId} updated successfully"})
        }
    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)})
        }

def delete_task(event, context):
    try:
        if len(event["pathParameters"]["taskId"]) != 36:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "The ID has been provided incorrectly."})
            }
        taskId = event["pathParameters"]["taskId"]
        task = table.get_item(Key={"taskId": taskId})
        if "Item" not in task:
            raise Exception("Task not found.")
        table.delete_item(
            Key={"taskId": taskId}
        )
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Task {taskId} deleted successfully"})
        }
    except Exception as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)})
        }
