import RPi.GPIO as GPIO
import sys, time, threading
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
preheatport = 18
shotport=23
steamport=24
ledport=25

shotseconds=30
elapsed=0
current_mode="off"
requested_mode="off"
usetimer=True

# Set button and PIR sensor pins as an input
GPIO.setup(preheatport, GPIO.OUT)
GPIO.setup(shotport, GPIO.OUT)
GPIO.setup(steamport, GPIO.OUT)
#GPIO.setup(ledport, GPIO.OUT)
GPIO.output(preheatport, GPIO.HIGH)
GPIO.output(shotport, GPIO.HIGH)
GPIO.output(steamport, GPIO.HIGH)
#GPIO.output(ledport, GPIO.LOW)


@app.before_first_request
def shottimer():
	def run():
		global current_mode
		global requested_mode
		global elapsed
		while 1:
			if (current_mode!=requested_mode):
				if (requested_mode=="preheat"):
				        GPIO.output(preheatport, GPIO.LOW)
				        GPIO.output(shotport, GPIO.HIGH)
				        GPIO.output(steamport, GPIO.HIGH)
				#       GPIO.output(ledport, GPIO.HIGH)
					current_mode=requested_mode
				elif (requested_mode=="shot"):
				        GPIO.output(preheatport, GPIO.LOW)
				        GPIO.output(shotport, GPIO.LOW)
				        GPIO.output(steamport, GPIO.HIGH)
				#       GPIO.output(ledport, GPIO.HIGH)
					current_mode=requested_mode
				elif (requested_mode=="steam"):
				        GPIO.output(preheatport, GPIO.LOW)
				        GPIO.output(shotport, GPIO.HIGH)
				        GPIO.output(steamport, GPIO.LOW)
				#       GPIO.output(ledport, GPIO.HIGH)
					current_mode=requested_mode
				else:
				        GPIO.output(preheatport, GPIO.HIGH)
				        GPIO.output(shotport, GPIO.HIGH)
				        GPIO.output(steamport, GPIO.HIGH)
				#       GPIO.output(ledport, GPIO.LOW)
					current_mode="off"
			time.sleep(.25)
			if (current_mode=="shot" and usetimer==True):
				elapsed+=.25
			if (elapsed>shotseconds):
				requested_mode="preheat"
				elapsed=0
	thread=threading.Thread(target=run)
	thread.start()

#serve index page
@app.route("/")
def index():
	return render_template('index.html')

#get current status
@app.route("/powersts", methods=['GET'])
def info():
	preheatsts = str(GPIO.input(preheatport))
	shotsts = str(GPIO.input(shotport))
	steamsts = str(GPIO.input(steamport))
	if (preheatsts=="0"):
		if (steamsts=="0"):
			return "steam"
		elif (shotsts=="0"):
			return "shot"
		else:
			return "preheat"
	else:
		return "off"

#get seconds left
@app.route("/secleft", methods=['GET'])
def info2():
	if (current_mode=="shot" and usetimer==True):
		return str(int(shotseconds-elapsed))+" sec left"
	else:
		return ""

#trigger preheat mode
@app.route("/preheat", methods=['POST'])
def action():
	global requested_mode
	requested_mode="preheat"
	return "0"

#trigger pump
@app.route("/shot/<useshottimer>", methods=['POST'])
def action2(useshottimer):
	global requested_mode
	global usetimer
	global elapsed
	if (useshottimer=="false"):
		usetimer=False
	else:
		usetimer=True
	elapsed=0
	requested_mode="shot"
	#open pull count file and add pulls
	with open("/root/espresso/pullcount.dat","r+") as orgf:
		try:
			currentcount=int(orgf.read())
		except:
			currentcount=0
		finally:
			orgf.seek(0)
			orgf.write(str(currentcount+1))

	return "0"

#trigger steam mode
@app.route("/steam", methods=['POST'])
def action3():
	global requested_mode
	requested_mode="steam"
	return "0"

#turn off
@app.route("/off", methods=['POST'])
def action4():
	global requested_mode
	requested_mode="off"
	return "0"

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80, debug=False, threaded=True)
    
