from aws_cdk import (
  Stack,
  RemovalPolicy,
  aws_lambda as _lambda,
  aws_apigateway as apigateway,
  aws_dynamodb as dynamodb
)
from constructs import Construct

class MyProjectStack(Stack):

  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    table = dynamodb.Table(self, "TasksTable",
      partition_key={"name": "taskId", "type": dynamodb.AttributeType.STRING},
      removal_policy=RemovalPolicy.DESTROY,
    )

    get_function = _lambda.Function(self, "GetTaskFunction", 
      runtime = _lambda.Runtime.PYTHON_3_9,
      handler = "lambda_handler.get_task",
      code = _lambda.Code.from_asset("lambda"),
      environment = {
        "TABLE_NAME": table.table_name
      }
    )

    create_function = _lambda.Function(self, "CreateTaskFunction",
      runtime = _lambda.Runtime.PYTHON_3_9,
      handler = "lambda_handler.create_task",
      code = _lambda.Code.from_asset("lambda"),
      environment = {
        "TABLE_NAME": table.table_name
      }
    )

    edit_function = _lambda.Function(self, "EditTaskFunction",
      runtime = _lambda.Runtime.PYTHON_3_9,
      handler = "lambda_handler.update_task",
      code = _lambda.Code.from_asset("lambda"),
      environment = {
        "TABLE_NAME": table.table_name
      }
    )

    delete_function = _lambda.Function(self, "DeleteTaskFunction",
      runtime = _lambda.Runtime.PYTHON_3_9,
      handler = "lambda_handler.delete_task",
      code = _lambda.Code.from_asset("lambda"),
      environment = {
        "TABLE_NAME": table.table_name
      }
    )

    table.grant_read_data(get_function)
    table.grant_read_write_data(create_function)
    table.grant_read_write_data(edit_function)
    table.grant_read_write_data(delete_function)

    api = apigateway.RestApi(self, "ApiEndpoint",
      rest_api_name = "CRUD Tasks",
      description = "This REST API manage CRUD operations for tasks"
    )

    tasks = api.root.add_resource("tasks")

    tasks.add_method("POST", apigateway.LambdaIntegration(create_function))

    task = tasks.add_resource("{taskId}")

    task.add_method("GET", apigateway.LambdaIntegration(get_function))
    
    task.add_method("PUT", apigateway.LambdaIntegration(edit_function))

    task.add_method("DELETE", apigateway.LambdaIntegration(delete_function))
