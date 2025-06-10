import requests
import json

url = "http://192.168.3.128:1100/admin-api/oa/myTask/commitTask"
headers = {
    "Authorization": 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJsb2dpbl91c2VyX2tleSI6ImEzMjE1ZjFlLTRhNTktNDNhZC1iY2M0LWRhZDQ1OTY1ZWE2YyJ9._539Dc3mfX9nvZZCBMy5ns6SKHj2Mz0MCs8l9ZlV8B55-1owcEKIzSv0hF7qJBkNcH2Pv021XrUudcvlbSRLug',
    "Content-Type": "application/json;charset=UTF-8"
}
payload = {
    "billType": "sm_sales",
    "businessId": 19,
    "comment": "",
    "insid": "2572432",
    "operateType": 0,
    "taskid": "2572439"
}
print("提交审批 payload:", json.dumps(payload, indent=2))

res = requests.post(url, headers=headers, json=payload)
print("审批响应：", res.status_code, res.text)
