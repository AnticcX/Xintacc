from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from tenacity import retry, stop_after_attempt

from .content import Content
from .conversation import get_conversation, save_conversation
from ..utils import get_config


class Model:
    """
    Wrapper class for interacting with an OpenAI-compatible LLM model.
    """
    
    def __init__(self, model_base_url: str, model: str, api_key: str, is_vision: bool = False):
        """
        Initializes the model configuration.

        Args:
            model_base_url (str): The base URL for the OpenAI or compatible API.
            model (str): The model ID or name (e.g. 'gpt-4', 'gpt-3.5-turbo').
            api_key (str): The API key used for authentication.
            is_vision (bool, optional): Indicates if the model supports image input. Defaults to False.
        """
        self.model_base_url: str = model_base_url
        self.model: str = model
        self.api_key: str = api_key
        self.is_vision: bool = is_vision 
        
    def get_client(self) -> OpenAI:
        """
        Creates and returns an OpenAI client instance.

        Returns:
            OpenAI: An instance of the OpenAI client configured with base URL and API key.
        """
        return OpenAI(base_url=self.model_base_url, api_key=self.api_key)
    
    @retry(stop=stop_after_attempt(4))
    def call_chat_completion(self, content: Content) -> str:
        client = self.get_client()
        response = client.chat.completions.create(model=self.model, messages=content, temperature=0.85)
        content = response.choices[0].message.content
        
        if len(content) <= 0:
            raise RuntimeError("Empty response")
        return content

    def fetch_response(self, user_id: str, content: Content) -> str:
        """
        Sends a request to the language model using the provided conversation content,
        and returns the assistant's response. The interaction is also appended to the user's
        saved conversation history.

        Args:
            user_id (str): The unique identifier of the user whose conversation is being processed.
            content (Content): The new user message(s) to send to the model. Must be a `Content` instance.

        Raises:
            ValueError: If the provided content is not a valid `Content` object or fails to load.

        Returns:
            str: The generated response text from the model.
    """
        if not isinstance(content, Content):
            try:
                content = Content(init_list=content)
            except ValueError:
                raise ValueError("fetch_response() requires 'content' be a valid content structure for LLM responses")
                return None
    
        conversation = get_conversation(user_id)
        conversation.extendleft(reversed(content))
        conversation.extendleft({
            "role": "system",
            "content": get_config("model_system_prompt")
        })

        model_response = self.call_chat_completion(content)
        print(model_response)
        
        conversation = Content(init_list=content)
        conversation.add_assistant([model_response])
        
        save_conversation(user_id, list(conversation))
        
        return model_response
    