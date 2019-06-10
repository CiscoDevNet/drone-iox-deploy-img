import requests
import json
import env_config
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def get_token(ip, username, password):
    # print(ip)
    url = "https://%s/api/v1/appmgr/tokenservice" % ip
    print(url)

    r = requests.post(url, auth=(username, password), verify=False)
    print(r.request.headers)
    token = ''
    if r.status_code == 202:
        print(r.json())
        token = r.json()['token']
        #print(token)
    else:
        print("ERROR")
        print("Status code is " + str(r.status_code))
        print(r.text)
    return token


def add_app(ip, token, appname, imageTag):
    url = "https://%s/api/v1/appmgr/localapps/upload" % ip

    headers = {'x-token-id': token}
    parameters = {"type": "docker",
                  "dockerImageName": appname,
                  "dockerImageTag": imageTag,
                  "dockerRegistry": ""}

    r = requests.post(url, headers=headers, params=parameters, verify=False)

    if r.status_code == 201:
        print(r.json())
    else:
        print("ERROR")
        print("Status code is " + str(r.status_code))
        print(r.text)


def is_myapp_present(ip, token, myapp_name):
    url = "https://%s/api/v1/appmgr/myapps?searchByName=%s" % (ip, myapp_name)
    headers = {'x-token-id': token, 'content-type': 'application/json'}
    r = requests.get(url, headers=headers, verify=False)
    print(r.status_code)
    print(r.text)
    if r.text == '{}':
        return False
    else:
        return True


def get_app_details(ip, token, appname):
    url = "https://%s/api/v1/appmgr/localapps?limit=100" % ip
    headers = {'x-token-id': token, 'content-type': 'application/json'}
    r = requests.get(url, headers=headers, verify=False)
    print(r.status_code)

    apps = json.loads((json.dumps(r.json())))

    for index in range(len(apps['data'])):
        print(apps['data'][index]['name'])
        print(appname)
        if (appname == apps['data'][index]['name']):
            return apps['data'][index]

    return apps


def get_myapp_details(ip, token, myapp_name):
    url = "https://%s/api/v1/appmgr/myapps" % ip
    payload = {"searchByName": myapp_name}
    headers = {'x-token-id': token, 'content-type': 'application/json'}
    r = requests.get(url, headers=headers, params=payload, verify=False)
    print(r.url)
    print(r.text)
    print(r.status_code)
    return json.loads((json.dumps(r.json())))


def get_device_details(ip, token, deviceip):
    url = "https://%s/api/v1/appmgr/devices" % ip
    headers = {'x-token-id': token, 'content-type': 'application/json'}
    r = requests.get(url, headers=headers, verify=False)
    print(r.status_code)

    devices = json.loads((json.dumps(r.json())))

    for index in range(len(devices['data'])):
        if (deviceip == devices['data'][index]['ipAddress']):
            return devices['data'][index]


def create_myapp(ip, token, appname):
    url = "https://%s/api/v1/appmgr/myapps" % ip
    headers = {'x-token-id': token, 'content-type': 'application/json'}

    app_details = get_app_details(ip, token, appname)

    print(app_details)

    data = {"name": appname, "sourceAppName": appname, "version": "v1", "appSourceType": "LOCAL_APPSTORE"}
    data["name"] = appname
    data["sourceAppName"] = app_details["localAppId"] + ":" + app_details["version"]
    data["version"] = app_details["version"]

    print("data is ")
    print(json.dumps(data))
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    print("create_myapp response")
    print(r.text)


def install_app(ip, token, appname, deviceip):
    print("Check whether myapp present in FD")
    myapp_present = is_myapp_present(ip, token, appname)

    if myapp_present != True:
        print("Creating myapp")
        create_myapp(ip, token, appname)

    create_myapp(ip, token, appname)

    myapp_details = get_myapp_details(ip, token, appname)
    device_details = get_device_details(ip, token, deviceip)

    url = "https://%s/api/v1/appmgr/myapps/%s/action" % (ip, myapp_details['myappId'])
    print("url " + url)
    headers = {'x-token-id': token, 'content-type': 'application/json'}

    data = {"deploy": {"config": {}, "metricsPollingFrequency": "3600000", "startApp": True, "devices": [
        {"deviceId": "7", "resourceAsk": {"resources": {"profile": "custom", "cpu": 50, "memory": 50, "network": [
            {"port_map": {"mode": "1to1", "tcp": {"3000": "3000"}, "udp": {}}, "interface-name": "eth0", "network-name": "iox-nat0"}]}}}]}}
    data["deploy"]["devices"][0]["deviceId"] = device_details['deviceId']

    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    print("response")
    print(r.text)


def uninstall_app(ip, token, appname, deviceip):
    myapp_details = get_myapp_details(ip, token, appname)
    device_details = get_device_details(ip, token, deviceip)

    url = "https://%s/api/v1/appmgr/myapps/%s/action" % (ip, myapp_details['myappId'])
    print("url " + url)
    headers = {'x-token-id': token, 'content-type': 'application/json'}

    data = {"undeploy": {"devices": [9]}}
    data["undeploy"]["devices"][0] = device_details['deviceId']

    print("uninstall data")
    print(json.dumps(data))
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    print("response")
    print(r.text)


def stop_app(ip, token, appname):
    myapp_details = get_myapp_details(ip, token, appname)

    url = "https://%s/api/v1/appmgr/myapps/%s/action" % (ip, myapp_details['myappId'])
    print("url " + url)
    headers = {'x-token-id': token, 'content-type': 'application/json'}

    data = {"stop": {}}

    print("Stop data")
    print(json.dumps(data))
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    print("response")
    print(r.text)


def start_app(ip, token, appname):
    myapp_details = get_myapp_details(ip, token, appname)

    url = "https://%s/api/v1/appmgr/myapps/%s/action" % (ip, myapp_details['myappId'])
    print("url " + url)
    headers = {'x-token-id': token, 'content-type': 'application/json'}

    data = {"start": {}}

    print("Start data")
    print(json.dumps(data))
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    print("response")
    print(r.text)


def publish_apps(ip, token):
    url = "https://%s/api/v1/appmgr/localapps?limit=100" % ip
    headers = {'x-token-id': token, 'content-type': 'application/json'}
    r = requests.get(url, headers=headers, verify=False)
    print(r.status_code)

    apps = json.loads((json.dumps(r.json())))

    for index in range(len(apps['data'])):
        appid = apps['data'][index]['localAppId']
        appname = apps['data'][index]['name']
        appversion = apps['data'][index]['version']
        publish_state = apps['data'][index]['published']
        if publish_state == False:
            print("Publishing App %s" % (appname))
            apps['data'][index]['published'] = True
            url = "https://%s/api/v1/appmgr/localapps/%s:%s" % (ip, appid, appversion)
            headers = {'x-token-id': token, 'content-type': 'application/json'}
            data = json.dumps(apps['data'][index])
            r = requests.put(url, headers=headers, data=data, verify=False)
            print(r.status_code)


app_mgr_ip = env_config.app_mgr_ip
username = env_config.username
password = env_config.password
appname = env_config.appname
deviceip = env_config.deviceip
imageTag = env_config.imageTag
if imageTag == "":
    fullappname = appname
else:
    fullappname = appname + ":" + imageTag

# Login to Fog Director
print("Login to Fog Director")
token_id = get_token(app_mgr_ip, username, password)
print(token_id)

print("Adding app to Fog Director")
add_app(app_mgr_ip, token_id, appname, imageTag)

print("Publishing the unpublished apps in FD")
publish_apps(app_mgr_ip, token_id)

install_app(app_mgr_ip, token_id, appname, deviceip)

print("AND YOUR DONE")

