import RPi.GPIO as GPIO
import sys, time, threading, datetime, hashlib
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
preheatport = 18
ledport=25
switchport=17

preheattime=1800
elapsed=0
current_mode="off"
requested_mode="off"
laststatusreason="PREHEATER OFF - Controller was rebooted at "+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+"."

loglocation="/root/pfcpreheat/log.dat"

#script start log entry
orgf=open(loglocation,"a+")
orgf.write(str(datetime.datetime.now())+"  SCRIPT START\n")
orgf.close()

# Set button and PIR sensor pins as an input
GPIO.setup(preheatport, GPIO.OUT)
GPIO.setup(ledport, GPIO.OUT)
GPIO.setup(switchport, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(preheatport, GPIO.HIGH)
GPIO.output(ledport, GPIO.LOW)


@app.before_first_request
def heattimer():
	def run():
		global current_mode
		global requested_mode
		global elapsed
		global glcissuer
		global laststatusreason
		while 1:
			#see if preheat is requested by GSM module
			input_state=GPIO.input(switchport)
			if (input_state==False and current_mode!="preheat"):
				if (current_mode!="GSMpreheat"):
					orgf=open(loglocation,"a+")
					orgf.write(str(datetime.datetime.now())+"  START  SMS Module\n")
					orgf.close()
					laststatusreason="PREHEATER ON - started at "+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+" by the SMS module.  Text SMS module to stop preheating."
					GPIO.output(preheatport, GPIO.LOW)
					requested_mode="GSMpreheat"
					current_mode=requested_mode
			else:
				#stop preheat if GSM module turned it on
				if (current_mode=="GSMpreheat"):
					GPIO.output(preheatport, GPIO.HIGH)
					requested_mode="off"
					current_mode=requested_mode
					orgf=open(loglocation,"a+")
					orgf.write(str(datetime.datetime.now())+"  STOP   SMS Module\n")
					orgf.close()
					laststatusreason="PREHEATER OFF - stopped at "+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+" by the SMS module."
				if (current_mode!=requested_mode):
					if (requested_mode=="preheat"):
					        GPIO.output(preheatport, GPIO.LOW)
						current_mode=requested_mode
						elapsed=0
						orgf=open(loglocation,"a+")
						orgf.write(str(datetime.datetime.now())+"  START  "+glcissuer+"\n")
						orgf.close()
						laststatusreason="PREHEATER ON - started at "+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+" by "+glcissuer+"."
					elif (requested_mode=="timeroff"):
                                                GPIO.output(preheatport, GPIO.HIGH)
						current_mode=requested_mode
						orgf=open(loglocation,"a+")
                                                orgf.write(str(datetime.datetime.now())+"  STOP   TIMER\n")
                                                orgf.close()
						laststatusreason="PREHEATER OFF - stopped at "+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+" by the timer."
					else:
					        GPIO.output(preheatport, GPIO.HIGH)
						current_mode="off"
						orgf=open(loglocation,"a+")
						orgf.write(str(datetime.datetime.now())+"  STOP   "+glcissuer+"\n")
						orgf.close()
						laststatusreason="PREHEATER OFF - stopped at "+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+" by "+glcissuer+"."
			time.sleep(1.5)
			if (current_mode=="preheat"):
				elapsed+=1.5
			if (elapsed>preheattime):
				requested_mode="timeroff"
				#reset elapsed so preheat does not keep becoming requested mode
				elapsed=0
	thread=threading.Thread(target=run)
	thread.start()
'''	def switch():
		global requested_mode
		while 1:
			input_state=GPIO.input(switchport)
			if input_state==False:
				if (current_mode=="preheat"):
					time.sleep(.5)
					requested_mode="off"
					time.sleep(2)
				elif (current_mode=="off"):
					requested_mode="preheat"
					time.sleep(2)
				else:
					requested_mode="off"
					time.sleep(2)
			#prevent CPU usage
			time.sleep(.1)
	thread=threading.Thread(target=switch)
	thread.start()
	#flash led
	def ledblink():
		while 1:
			if (current_mode=="preheat" or current_mode=="GSMpreheat"):
				GPIO.output(ledport, GPIO.HIGH)
			else:
				GPIO.output(ledport, GPIO.LOW)
			#prevent CPU usage
			time.sleep(.1)
	thread=threading.Thread(target=ledblink)
	thread.start()'''
#serve index page
@app.route("/")
def index():
	return render_template('index.html')

#authentication
@app.route("/authenticate/<password>", methods=['POST'])
def valid_password(password):
	userhash="534e34d7dd9100307f970d2d00f0880f91ebcd6d7b825ccf00e3338b6d7eb83e"
	pw_hash=hashlib.sha256(password).hexdigest()
	if (userhash == pw_hash):
		return "true"
	else:
		return "false"

#get current status
@app.route("/powersts", methods=['GET'])
def info():

	#preheatsts = str(GPIO.input(preheatport))
	#if (preheatsts=="0"):
	#	return "preheat"
	#else:
	#	return "off"
	return current_mode

#get seconds left
@app.route("/secleft", methods=['GET'])
def info2():
	if (current_mode=="preheat"):
		#return str(int(preheattime-elapsed))+" sec left"
		return str(datetime.timedelta(seconds=int(preheattime-elapsed)))+" left"
	else:
		return ""

#get lcissuer
@app.route("/laststatusreason", methods=['GET'])
def info3():
	return laststatusreason

#trigger preheat mode
@app.route("/preheat/<lcissuer>", methods=['POST'])
def action(lcissuer):
	global requested_mode
	global glcissuer
	requested_mode="preheat"
	glcissuer=lcissuer
	return "0"

#turn off
@app.route("/off/<lcissuer>", methods=['POST'])
def action2(lcissuer):
	global requested_mode
	global glcissuer
	requested_mode="off"
	glcissuer=lcissuer
	return "0"

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80, debug=False, threaded=True)
    
