import base64

from typing import List, Optional

from utils.http_client import HttpClient

# https://docs.hybrik.com/api/v1/HybrikAPI.html?#getting-started
# https://docs.hybrik.com/api/v1/HybrikAPI.html?#create-job
# https://docs.hybrik.com/api/v1/HybrikAPI.html?#get-job-info


class HybrikApiClient(HttpClient):

    def __init__(self, api_url, oapi_key, oapi_secret, auth_key, auth_secret, compliance_date="20240228"):
        super().__init__(api_url)
        self.default_headers = {"X-Hybrik-Compliance": compliance_date}
        self.set_auth(oapi_key, oapi_secret)
        self.auth_key = auth_key
        self.auth_secret = auth_secret
        self.login_data = None

    def connect(self):
        response = self.login(self.auth_key, self.auth_secret)
        if response and 'token' in response:
            self.login_data = response
            return True
        return False

    def set_auth(self, oapi_key, oapi_secret):
        user_pass = f"{oapi_key}:{oapi_secret}"
        encoded_user_pass = base64.b64encode(user_pass.encode()).decode()
        self.default_headers["Authorization"] = f"Basic {encoded_user_pass}"

    def call_api(self, http_method, path, query=None, body=None):
        headers = self.default_headers

        if self.login_data:
            headers["X-Hybrik-Sapiauth"] = self.login_data["token"]
        if body:
            headers["Content-Type"] = "application/json"
        if http_method.lower() == "get":
            return self.get(path, query=query, headers=headers)
        elif http_method.lower() == "post":
            return self.post(path, data=body, query=query, headers=headers)
        elif http_method.lower() == "put":
            return self.put(path, data=body, query=query, headers=headers)
        elif http_method.lower() == "delete":
            return self.delete(path, query=query, headers=headers)

    def create_job(self,
                   name,
                   payload,
                   schema,
                   expiration,
                   priority,
                   task_tags,
                   task_retry_count,
                   task_retry_delay_secs,
                   user_tag,):
        endpoint = "jobs"
        body = {
            "name": name,
            "payload": payload,
            "schema": schema,
        }
        if expiration:
            body["expiration"] = expiration
        if priority:
            body["priority"] = priority
        if task_tags:
            body["task_tags"] = task_tags
        if user_tag:
            body["user_tag"] = user_tag
        if task_retry_count:
            body["task_retry:count"] = task_retry_count
        if task_retry_delay_secs:
            body["task_retry:delay_secs"] = task_retry_delay_secs

        return self.call_api("post", endpoint, body=body)

    def delete_job(self, job_id):
        endpoint = f"jobs/{job_id}/delete"
        return self.call_api("delete", endpoint)

    def get_job_definition(self, job_id):
        endpoint = f"jobs/{job_id}/definition"
        return self.call_api("get", endpoint)

    def get_job_results(self, job_id):
        endpoint = f"jobs/{job_id}/result"
        return self.call_api("get", endpoint)

    def get_job_tasks(self, job_id):
        endpoint = f"jobs/{job_id}/tasks"
        return self.call_api("get", endpoint)

    def list_jobs(self,
                  ids: Optional[List[str]] = None,
                  fields: Optional[List[str]] = None,
                  filters_field: Optional[str] = None,
                  filters_values: Optional[List[str]] = None,
                  order: Optional[str] = None,
                  skip: Optional[int] = None,
                  sort_field: Optional[str] = None,
                  take: Optional[int] = None,
                  ):
        # https://docs.hybrik.com/api/v1/HybrikAPI.html?javascript#list-jobs
        endpoint = "jobs/info"
        query = {
            # "ids": ids,
            # "fields": fields,
            # "filters": {
            #     filters_field: filters_values
            # },
            # "order": order,
            # "skip": skip,
            # "sort_field": sort_field,
            # "take": take
            # }
        }
        if ids:
            query["ids"] = ids
        if fields:
            query["fields"] = fields
        if filters_field and filters_values:
            query["filters"] = {
                filters_field: filters_values
            }
        if order:
            query["order"] = order
        if skip:
            query["skip"] = skip
        if sort_field:
            query["sort_field"] = sort_field
        if take:
            query["take"] = take

        return self.call_api("get", endpoint, query=query)

    def login(self, auth_key, auth_secret):
        endpoint = "login"
        data = {
            "auth_key": auth_key,
            "auth_secret": auth_secret
        }
        return self.call_api("post", endpoint, body=data)
