from langchain_community.llms import Bedrock

def get_bedrock_model():
    """
    Creates and returns a LangChain LLMChain using the Llama 2 70B chat model from Bedrock.

    Returns:
        LLMChain: An LLMChain object configured with the Llama 2 model.
    """

    # Initialize the Bedrock model
    bedrock_client = Bedrock(
        model_id="meta.llama3-70b-instruct-v1:0",
        region_name="us-east-1",  # Choose the appropriate region
        credentials_profile_name="default"  # Use your default AWS profile or specify a different one
    )

    # Create a LangChain LLMChain
    return bedrock_client

