import requests
import env_config
import json
import base64
import sys


def get_token(ip, username, password):
    # print(ip)
    url = "https://%s/api/v1/appmgr/tokenservice" % ip
    print(url)

    r = requests.post(url, auth=(username, password), verify=False)
    token = ''
    if r.status_code == 202:
        print(r.json())
        token = r.json()['token']
        # print(token)
    else:
        print("ERROR")
        print("Status code is " + str(r.status_code))
        print(r.text)
    return token


def delete_token(ip, token):
    url = "https://%s/api/v1/appmgr/tokenservice/%s" % (ip, token)

    headers = {'x-token-id': token, 'content-type': 'application/json'}

    r = requests.delete(url, headers=headers, verify=False)

    if r.status_code == 200:
        print(r.json())
    else:
        print("ERROR")
        print("Status code is " + str(r.status_code))
        print(r.text)


def find_app_info(ip, token, appname):
    url = "https://%s/api/v1/appmgr/localapps" % (ip)

    headers = {'x-token-id': token}

    r = requests.get(url, headers=headers, verify=False)

    if r.status_code == 200:
        ret_json = r.json()
        # print(ret_json)
        app_data = ret_json["data"]
        print(app_data)
        app_list_check = True

        while app_list_check:
            for i in app_data:
                if i["descriptor"]["name"] == appname:
                    return i["localAppId"], i["version"]
            app_list_check = False
        print("Data Not Found. Are you sure the app is deployed")
        sys.exit(1)

    else:
        print("ERROR")
        print("Status code is " + str(r.status_code))
        print(r.text)
        sys.exit(1)


def update_app(ip, token, appname, imageTag, dockerReg, localappid, prevappver):
    prev_app = localappid + ":" + prevappver
    url = "https://%s/api/v1/appmgr/localapps/%s/package" % (ip, prev_app)

    headers = {'x-token-id': token}
    parameters = {"type": "docker",
                  "dockerImageName": appname,
                  "dockerImageTag": imageTag,
                  "dockerRegistry": dockerReg,
                  "ignoreDeviceResourceValidation": "false"}

    r = requests.post(url, headers=headers, params=parameters, verify=False)

    if r.status_code == 201:
        print(r.json())
    else:
        print("ERROR")
        print("Status code is " + str(r.status_code))
        print(r.text)




app_mgr_ip = env_config.app_mgr_ip
username = env_config.username
password = env_config.password
appname = env_config.appname
imageTag = env_config.imageTag
dockerReg = env_config.dockerReg

# Login to Fog Director
print("Login to Fog Director")
token_id = get_token(app_mgr_ip, username, password)
print(token_id)

print("Locating App to be updated")
app_id, prev_version = find_app_info(app_mgr_ip, token_id, appname)

print("Updating app on Fog Director")
update_app(app_mgr_ip, token_id, appname, imageTag, dockerReg, app_id, prev_version)

# print("Logging out of Fog Director")
# delete_token(app_mgr_ip, token_id)
