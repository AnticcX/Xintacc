from collections import deque


class Content(list):
    def __init__(self, system_prompt: str = None, init_list: list = None):
        """
        Initializes the Content list with an optional system prompt message.

        Args:
            system_prompt (str, optional): A string to include as the initial system message.
        """
        super().__init__()
        if system_prompt:
            self.append({"role": "system", "content": system_prompt})
            
        if init_list: self.load_from_existing(init_list)

    def _build_content_blocks(self, text: list[str] = None, image_url: list[str] = None) -> list:
        """
        Builds a list of content blocks from text and/or image URLs.

        Args:
            text (list[str], optional): A list of text strings to convert to content blocks.
            image_url (list[str], optional): A list of image URLs to convert to content blocks.

        Returns:
            list: A list of content blocks suitable for use in a message payload.
        """
        content = []
        if text:
            content.extend({"type": "text", "text": msg} for msg in text)
        if image_url:
            content.extend({"type": "image_url", "image_url": {"url": url}} for url in image_url)
        return content

    def add_user(self, text: list[str] = None, image_url: list[str] = None) -> None:
        """
        Adds a 'user' role message to the content list with text and/or image URLs.

        Args:
            text (list[str], optional): A list of text strings.
            image_url (list[str], optional): A list of image URLs.

        Raises:
            ValueError: If neither text nor image_url is provided or both are empty.
        """
        content = self._build_content_blocks(text, image_url)
        if not content:
            raise ValueError("add_user() requires at least one of 'text' or 'image_url'.")
        self.append({"role": "user", "content": content})

    def add_assistant(self, text: list[str]) -> None:
        """
        Adds an 'assistant' role message with a list of text responses.

        Args:
            text (list[str]): A list of text strings for the assistant's reply.

        Raises:
            ValueError: If the text list is empty or not provided.
        """
        if not text:
            raise ValueError("add_assistance() requires a non-empty list of text.")
        content = [{"type": "text", "text": msg} for msg in text]
        self.append({"role": "assistant", "content": content})

    def load_from_existing(self, content: list[dict] | deque) -> None:
        """
        Loads and replaces the current content with a list of existing message dictionaries.

        Args:
            content (list[dict]): A list of message dictionaries to load.

        Raises:
            ValueError: If content is not a list.
            ValueError: If any message is not a dictionary.
            ValueError: If any message lacks required keys ('role', 'content').
            ValueError: If any message role is not one of 'system', 'user', or 'assistant'.
        """
        if not isinstance(content, list) and not isinstance(content, deque):
            raise ValueError("Expected a list of message dictionaries or deque.")

        for message in content:
            if not isinstance(message, dict):
                raise ValueError("Each message must be a dictionary.")
            if "role" not in message or "content" not in message:
                raise ValueError("Each message must contain 'role' and 'content' keys.")
            if message["role"] not in ("system", "user", "assistant"):
                raise ValueError(f"Invalid role: {message['role']}")

        self.clear()
        self.extend(content)
