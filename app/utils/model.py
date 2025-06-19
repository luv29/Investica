from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.providers.bedrock import BedrockProvider
from dotenv import load_dotenv
import boto3
import os

load_dotenv()

required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

bedrock_client = boto3.client('bedrock-runtime', region_name='us-west-2')
# model = BedrockConverseModel(
#     # "us.anthropic.claude-sonnet-4-20250514-v1:0",
#     # "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
#     "arn:aws:bedrock:us-west-2:100098606670:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0",
#     # "arn:aws:bedrock:us-west-2:100098606670:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0",
#     provider=BedrockProvider(bedrock_client=bedrock_client),
# )

model="openai:gpt-4o-mini"