import os
import json

from collections import deque
from .content import Content

def confirm_user_exists(user_id: int) -> bool:
    """
    Checks if user chat data exists, and initializes it if missing.

    Args:
        user_id (str): The unique user ID.

    Returns:
        bool: True if the check (or initialization) succeeds, False otherwise.
    """
    base_path = f"./user_chats/{user_id}"
    conversation_path = os.path.join(base_path, "conversation.json")

    chat_data = deque()
    try:
        with open(conversation_path, "r") as fp:
            chat_data = deque(json.load(fp))
    except FileNotFoundError:
        os.makedirs(base_path, exist_ok=True)
        with open(conversation_path, "w") as fp:
            json.dump(list(chat_data), fp)
    except Exception:
        return False

    return True

def reset_conversation(user_id: int) -> bool:
    """
    Resets the conversation history for a given user by clearing their conversation file.

    This function ensures the user exists, then overwrites their conversation history
    (stored in 'conversation.json') with an empty list.

    Args:
        user_id (str): The unique identifier of the user.

    Returns:
        bool: True if the reset was successful, False if the user doesn't exist
            or an error occurred during the reset process.
    """
    if not confirm_user_exists(user_id): return False
    base_path = f"./user_chats/{user_id}"
    conversation_path = os.path.join(base_path, "conversation.json")
    
    try:
        chat_data = deque()
        json.dump(list(chat_data), open(conversation_path, "w"))
    except Exception:
        return False
    return True

def get_conversation(user_id: int, limit: int = 10) -> deque:
    """
    Loads the user's conversation history into a deque, optionally limiting the number of messages.

    Args:
        user_id (str): The unique identifier for the user.
        limit (int, optional): Maximum number of most recent messages to return. Defaults to 10.

    Returns:
        deque: A deque containing the user's most recent conversation messages.
    """
    confirm_user_exists(user_id)
    conversation_path = os.path.join("user_chats", user_id, "conversation.json")

    with open(conversation_path, "r") as fp:
        messages = json.load(fp)

    return deque(messages[-limit:])

def save_conversation(user_id: int, content: Content) -> None:
    """
    Appends new conversation content to a user's existing conversation history and saves it.

    This function retrieves the user's current conversation, appends the new content,
    and writes the updated history back to the conversation file.

    Args:
        user_id (str): The unique identifier of the user.
        content (Content): The new conversation content to append (messages in list-like format).
    """
    conversation = get_conversation(user_id)
    conversation.extend(content)
    
    conversation_path = os.path.join("user_chats", user_id, "conversation.json")
    
    json.dump(list(conversation), open(conversation_path, "w"), indent=4)
    