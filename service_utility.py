import time
import functools
import json
import re
import random
from typing import List, Dict, Any, Callable, Optional


class ServiceUtility:
    """
    A comprehensive utility class with methods to optimize and speed up common Python operations.
    Provides tools for caching, timing, validation, and data manipulation.
    """

    @staticmethod
    def timer(func: Callable) -> Callable:
        """
        Decorator to measure and print execution time of a function.

        Args:
            func (Callable): Function to be timed

        Returns:
            Callable: Wrapped function with timing functionality
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"Function {func.__name__} took {
                  end_time - start_time:.4f} seconds")
            return result
        return wrapper

    @staticmethod
    def memoize(func: Callable) -> Callable:
        """
        Decorator to cache function results for repeated calls with same arguments.

        Args:
            func (Callable): Function to be memoized

        Returns:
            Callable: Memoized function with caching
        """
        cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]
        return wrapper
    @staticmethod
    def update_text(original_text):
        """ Replace underscores with spaces and convert to lowercase then title"""
        updated_text = original_text.replace('_', ' ').lower()
        updated_text = updated_text.title()
        return updated_text
    @staticmethod
    def get_question(dictionary: dict, search_key: str) -> Optional[Dict[str, Any]]:
        """
        This function takes an input dictionary and a search key, 
        then retrieves and returns a list of questions from the dictionary 
        that match the specified criteria.
        """
        new_dictionary = {}
        for key, value in dictionary.items():
            if search_key.upper() in key.upper() and not key.endswith("_VALIDATION"):
                new_dictionary[key] = value
        return new_dictionary
    
    @staticmethod
    def section_not_completed(dictionary):
        """
        This function takes an input dictionary and checks if the section 
        is completed and available for the user.
        """
        question_count = 0
        formula_count = 0
        recommendation_count = 0
        for key, _ in dictionary.items():
            if key.endswith("_FORMULA"):
                formula_count += 1
            elif "_QUESTION_" in key.upper():
                question_count += 1
            elif key.endswith("_RECOMMENDATIONS"):
                recommendation_count += 1

        return not (formula_count == 1 and recommendation_count == 1 and question_count > 0)
