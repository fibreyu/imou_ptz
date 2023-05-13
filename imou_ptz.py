#!/bin/python
########################################################
## API: https://open.imou.com/document/pages/fef620/  ##
## usage: python ./imou_ptz.py deviceID operation     ##
########################################################

import time, uuid, json, requests, sys, os
from hashlib import md5

TIMES_TO_GET_TOKEN=0
# config file data struct
IMOU_CONFIG={
	"appId": "",
	"appSecret": "",
	"baseUrl": "",
	"token": "",
	"devices": {

	}
}

# request base data struct
BASE_DATA={
	"system":{
		"ver":"1.0",
		"appId": "",
		"sign":"",
		"time":"",
		"nonce":""
	},
	"id":"",
	"params":{}
}

CONF_PATH = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'imou_config.json'


def getTimeStamp():
	return int(time.time())

def getNonce():
	return str(uuid.uuid4())

def getId():
	return getNonce()

def genSign():
	origin_str_list=[	
						"time:", 
						str(BASE_DATA["system"]["time"]),
						","
						"nonce:",
						# "".join(BASE_DATA["system"]["nonce"].split('-')),
						BASE_DATA["system"]["nonce"],
						",",
						"appSecret:",
						IMOU_CONFIG['appSecret']
					]
	return md5("".join(origin_str_list).encode('utf8')).hexdigest()

# generate request data
def genReqData(params):
	BASE_DATA["system"]["time"] = getTimeStamp()
	BASE_DATA["system"]["nonce"] = getNonce()
	BASE_DATA["system"]["appId"] = IMOU_CONFIG['appId']
	BASE_DATA["id"] = getId()
	BASE_DATA["params"] = params
	BASE_DATA["system"]["sign"] = genSign()

# send request
def sendReq(addr):
	r = requests.post(IMOU_CONFIG['baseUrl'] + addr, json=BASE_DATA)
	return json.loads(r.text)

# get token and write to config file
def getToken():
	genReqData({})
	r = sendReq('accessToken')
	IMOU_CONFIG['token'] = r['result']['data']['accessToken']
	print("Set Token: ", IMOU_CONFIG['token'])
	with open(CONF_PATH, "w", encoding="utf8") as f:
		json.dump(IMOU_CONFIG, f, indent=4, ensure_ascii=False)

# load config file when promgram start
def load_config():
	global IMOU_CONFIG
	with open(CONF_PATH, encoding='utf8') as f:
		config = json.load(f)
		IMOU_CONFIG = config

# check if token is in config file
# if return True ,should repeat last process
def checkToken(code):
	global TIMES_TO_GET_TOKEN
	if TIMES_TO_GET_TOKEN == 3:
		print("get token error !")
		exit()
	if code == '0':
		return False
	if IMOU_CONFIG['token'] == "":
		getToken()
		return False
	if code in ("TK1002", "P2P003", "SUB1005"):
		getToken()
		TIMES_TO_GET_TOKEN += 1
		return True

# load device from imou server
def load_device(deviceId):
	genReqData({
		"deviceId": deviceId,
        "token": IMOU_CONFIG['token']
		})
	r = sendReq('bindDeviceInfo')
	if checkToken(r['result']['code']):
		load_device(deviceId)
		return
	IMOU_CONFIG['devices'][deviceId] = r['result']['data']
	with open(CONF_PATH, "w", encoding="utf8") as f:
		json.dump(IMOU_CONFIG, f, indent=4, ensure_ascii=False)

# check device list
# if no device list get from iomu server
def checkDevice(deviceId):
	if 'devices' not in IMOU_CONFIG:
		IMOU_CONFIG['devices'] = {}
	if deviceId not in IMOU_CONFIG['devices']:
		load_device(deviceId)
	# check again
	if deviceId not in IMOU_CONFIG['devices']:
		print("get device err")
		exit()

# camera up
def ptz_up(deviceId):
	params={
		"token": IMOU_CONFIG['token'],
        "deviceId": deviceId,
        "channelId": IMOU_CONFIG['devices'][deviceId]['channels'][0]['channelId'],
        "operation":"0",
        "duration":"100"
	}
	genReqData(params)
	r = sendReq('controlMovePTZ')
	if checkToken(r['result']['code']):
		ptz_up()

# camera down
def ptz_down(deviceId):
	params={
		"token": IMOU_CONFIG['token'],
        "deviceId": deviceId,
        "channelId": IMOU_CONFIG['devices'][deviceId]['channels'][0]['channelId'],
        "operation":"1",
        "duration":"100"
	}
	genReqData(params)
	r = sendReq('controlMovePTZ')
	if checkToken(r['result']['code']):
		ptz_down()

# camera left
def ptz_left(deviceId):
	params={
		"token": IMOU_CONFIG['token'],
        "deviceId": deviceId,
        "channelId": IMOU_CONFIG['devices'][deviceId]['channels'][0]['channelId'],
        "operation":"2",
        "duration":"100"
	}
	genReqData(params)
	r = sendReq('controlMovePTZ')
	if checkToken(r['result']['code']):
		ptz_left()

# camera right
def ptz_right(deviceId):
	params={
		"token": IMOU_CONFIG['token'],
        "deviceId": deviceId,
        "channelId": IMOU_CONFIG['devices'][deviceId]['channels'][0]['channelId'],
        "operation":"3",
        "duration":"100"
	}
	genReqData(params)
	r = sendReq('controlMovePTZ')
	if checkToken(r['result']['code']):
		ptz_right()

# camera zoom in
def ptz_zoom_in(deviceId):
	params={
		"token": IMOU_CONFIG['token'],
        "deviceId": deviceId,
        "channelId": IMOU_CONFIG['devices'][deviceId]['channels'][0]['channelId'],
        "operation":"9",
        "duration":"100"
	}
	genReqData(params)
	r = sendReq('controlMovePTZ')
	if checkToken(r['result']['code']):
		ptz_zoom_in()

# camera zoom out
def ptz_zoom_out(deviceId):
	params={
		"token": IMOU_CONFIG['token'],
        "deviceId": deviceId,
        "channelId": IMOU_CONFIG['devices'][deviceId]['channels'][0]['channelId'],
        "operation":"8",
        "duration":"100"
	}
	genReqData(params)
	r = sendReq('controlMovePTZ')
	if checkToken(r['result']['code']):
		ptz_zoom_out()

# camera block
def ptz_block(deviceId):
	pass

# camera locate
def ptz_locate(deviceId):
	pass

def operate(deviceId, op):
	if op == "up":
		ptz_up(deviceId)
		return 
	if op == "down":
		ptz_down(deviceId)
		return 
	if op == "left":
		ptz_left(deviceId)
		return 
	if op == "right":
		ptz_right(deviceId)
		return 
	if op == "ptz_zoom_in":
		ptz_zoom_in(deviceId)
		return 
	if op == "zoom_out":
		ptz_zoom_out(deviceId)
		return 
	if op == "block":
		ptz_block(deviceId)
		return 
	if op == "locate":
		ptz_locate(deviceId)
		return 

def main():
	args = sys.argv
	if len(args) != 3:
		print(" wrong arguments ！")
		return
	deviceId = args[1]
	op = args[2]
	load_config()
	checkToken("")
	checkDevice(deviceId)
	operate(deviceId, op)

if __name__ == '__main__':
	main()
	
