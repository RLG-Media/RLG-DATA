# Help_center.py

import os
import json
from typing import Union

class HelpCenter:
    """
    Help Center class to manage user guides, FAQs, troubleshooting, and support articles.
    """
    
    def __init__(self, help_folder_path: str):
        """
        Initialize the HelpCenter class with the folder path where help articles are stored.
        :param help_folder_path: Path to the folder containing the help resources.
        """
        self.help_folder_path = help_folder_path
        self.load_help_articles()

    def load_help_articles(self) -> None:
        """
        Load all help articles from the specified folder.
        """
        self.articles = {}
        try:
            if not os.path.exists(self.help_folder_path):
                os.makedirs(self.help_folder_path)

            for root, _, files in os.walk(self.help_folder_path):
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            article_data = json.load(f)
                            self.articles[article_data['id']] = article_data
        except Exception as e:
            raise IOError(f"Error loading help articles: {e}")

    def add_help_article(self, article_id: str, title: str, content: str, tags: Union[list, None] = None) -> None:
        """
        Add a new help article to the help center.
        :param article_id: Unique identifier for the article.
        :param title: Title of the help article.
        :param content: Content of the help article.
        :param tags: List of tags associated with the article.
        """
        try:
            new_article = {
                'id': article_id,
                'title': title,
                'content': content,
                'tags': tags if tags else []
            }
            # Save to local folder
            file_path = os.path.join(self.help_folder_path, f"{article_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(new_article, f, ensure_ascii=False, indent=4)
            self.articles[article_id] = new_article
        except Exception as e:
            raise ValueError(f"Error adding help article: {e}")

    def get_help_article(self, article_id: str) -> Union[dict, None]:
        """
        Retrieve a help article by its ID.
        :param article_id: Unique identifier for the article.
        :return: Dictionary containing the article details or None if not found.
        """
        return self.articles.get(article_id)

    def search_help_articles(self, keyword: str) -> list:
        """
        Search for help articles by keyword.
        :param keyword: Keyword to search in titles or content.
        :return: List of matching articles.
        """
        results = []
        for article in self.articles.values():
            if keyword.lower() in article['title'].lower() or keyword.lower() in article['content'].lower():
                results.append(article)
        return results

    def update_help_article(self, article_id: str, title: Union[str, None] = None, content: Union[str, None] = None, tags: Union[list, None] = None) -> None:
        """
        Update an existing help article.
        :param article_id: Unique identifier for the article to update.
        :param title: Updated title of the help article.
        :param content: Updated content of the help article.
        :param tags: Updated list of tags associated with the article.
        """
        if article_id in self.articles:
            if title:
                self.articles[article_id]['title'] = title
            if content:
                self.articles[article_id]['content'] = content
            if tags:
                self.articles[article_id]['tags'] = tags
            
            # Save changes to local file
            file_path = os.path.join(self.help_folder_path, f"{article_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.articles[article_id], f, ensure_ascii=False, indent=4)
        else:
            raise KeyError(f"Help article with ID {article_id} not found.")

    def delete_help_article(self, article_id: str) -> None:
        """
        Delete a help article by its ID.
        :param article_id: Unique identifier for the article to delete.
        """
        if article_id in self.articles:
            del self.articles[article_id]
            file_path = os.path.join(self.help_folder_path, f"{article_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            raise KeyError(f"Help article with ID {article_id} not found.")

    def get_all_articles(self) -> list:
        """
        Retrieve all help articles.
        :return: List of all help articles.
        """
        return list(self.articles.values())

    def close(self):
        """
        Close any resources or perform cleanup.
        """
        # Any necessary cleanup (none required in this case)
        pass

# Example Usage:
"""
if __name__ == "__main__":
    help_folder_path = "help_articles"
    help_center = HelpCenter(help_folder_path)
    
    # Add a new help article
    help_center.add_help_article('001', 'How to create an account', 'Detailed guide on creating an account...', ['account', 'signup'])
    
    # Retrieve an article
    article = help_center.get_help_article('001')
    print("Retrieved Article:")
    print(article)
    
    # Search for articles
    search_results = help_center.search_help_articles('account')
    print("Search Results:")
    print(search_results)
    
    # Update an article
    help_center.update_help_article('001', content='Updated content for creating an account...')
    
    # Retrieve all articles
    all_articles = help_center.get_all_articles()
    print("All Articles:")
    print(all_articles)
    
    # Delete an article
    help_center.delete_help_article('001')
"""
