import RPi.GPIO as GPIO
import sys, time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
preheatport = 18
shotport=23
steamport=24
ledport=25


# Set button and PIR sensor pins as an input
GPIO.setup(preheatport, GPIO.OUT)
GPIO.setup(shotport, GPIO.OUT)
GPIO.setup(steamport, GPIO.OUT)
#GPIO.setup(ledport, GPIO.OUT)
GPIO.output(preheatport, GPIO.HIGH)
GPIO.output(shotport, GPIO.HIGH)
GPIO.output(steamport, GPIO.HIGH)
#GPIO.output(ledport, GPIO.LOW)


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

#trigger preheat mode
@app.route("/preheat", methods=['POST'])
def action():
	GPIO.output(preheatport, GPIO.LOW)
	GPIO.output(shotport, GPIO.HIGH)
	GPIO.output(steamport, GPIO.HIGH)
#	GPIO.output(ledport, GPIO.HIGH)
	return "0"

#trigger pump
@app.route("/shot", methods=['POST'])
def action2():
	GPIO.output(preheatport, GPIO.LOW)
	GPIO.output(shotport, GPIO.LOW)
	GPIO.output(steamport, GPIO.HIGH)
#       GPIO.output(ledport, GPIO.HIGH)

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
        GPIO.output(preheatport, GPIO.LOW)
        GPIO.output(shotport, GPIO.HIGH)
        GPIO.output(steamport, GPIO.LOW)
#	GPIO.output(ledport, GPIO.HIGH)
	return "0"

#turn off
@app.route("/off", methods=['POST'])
def action4():
	GPIO.output(preheatport, GPIO.HIGH)
	GPIO.output(shotport, GPIO.HIGH)
	GPIO.output(steamport, GPIO.HIGH)
#	GPIO.output(ledport, GPIO.LOW)
	return "0"

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80, debug=False)
    
