from pprint import pprint
from base64 import b64encode, b64decode
import json
import os
import requests

API_TOKEN = os.environ['GITHUB_API_TOKEN']
HEADER = {"Authorization": "token " + API_TOKEN}

BASE_URL = os.environ['GITHUB_BASE_URL']


def base64(s: str) -> str:
    return b64encode(s.encode()).decode()


def unbase64(s: str) -> str:
    return b64decode(s.encode()).decode()


class github:
    def __init__(self, project_url: str) -> None:
        global BASE_URL
        if project_url[-1] != '/':
            project_url += '/'

        self.project_url = project_url
        self.repo_url = BASE_URL + "repos/" + project_url
        assert self.get_repo()  # checks auth and that the repo exists

    def get_html_url(self, filepath: str) -> str:
        return self.get_file(filepath)['html_url']

    def contents_url(self, filepath: str) -> str:
        return self.repo_url + 'contents/' + filepath

    def get_repo(self) -> dict:
        response = requests.get(self.repo_url[:-1], headers=HEADER).json()
        assert 'message' not in response or (response['message'] != 'Not Found'), \
            "the repository was not found"
        return response

    def get_directory(self, filepath: str) -> list:
        response = requests.get(self.contents_url(filepath), headers=HEADER).json()

        if str(type(response)) == "<class 'dict'>":
            if 'message' in response:
                assert response['message'] != 'Not Found', \
                    'directory was not found'
            else:
                assert False, \
                    f"filepath: '{filepath}' is not a directory"
        assert str(type(response)) == "<class 'list'>"

        return response

    def get_file(self, filepath: str) -> dict:
        response = requests.get(self.contents_url(filepath), headers=HEADER).json()

        assert str(type(response)) != "<class 'list'>", \
            f"'{filepath}' is a directory" # the type is {type(response)} is <class 'list'>

        if str(type(response)) == "<class 'dict'>" \
                and 'message' in response:
            message = response['message']
            if 'Not Found' == message:
                raise FileNotFoundError("the file doesn't exist in " + self.project_url)
            if 'Bad credentials' == message:
                raise EnvironmentError('Error: Github AuthToken is incorrect! Please update GITHUB_API_TOKEN!')

        return response

    def get_file_contents(self, filepath: str) -> str:
        file_response = self.get_file(filepath)
        try:
            file_content_b64_lines = file_response['content']
        except KeyError:
            raise EnvironmentError('Error: Github AuthToken is incorrect! Please update GITHUB_API_TOKEN!')
        file_content_b64 = "".join(file_content_b64_lines.splitlines())
        return unbase64(file_content_b64)

    def create_file(self, filepath: str, content: str) -> dict:
        data = {
            "message": "add " + filepath,
            "content": base64(content)
        }

        j = json.dumps(data)
        response = requests.put(self.contents_url(filepath), headers=HEADER, data=j).json()

        return response

    def update_file(self, filepath: str, content: str) -> dict:
        data = {
            "message": "update " + filepath,
            "sha": self.get_file(filepath)['sha'],
            "content": base64(content)
        }

        j = json.dumps(data)
        response = requests.put(self.contents_url(filepath), headers=HEADER, data=j).json()
        return response
