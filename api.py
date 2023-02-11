from flask import Flask, make_response, jsonify, Response, request, session
# from flask_session import Session
import requests
import json

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = "abnddjb84803230c"  

@app.route('/')  
def home():
    res = make_response("<h4>Welcome :) Click <a href='/api/allmeterreadings/HFDA5A'>Meter ID</a> for a test! I am a live meter id</h4>")  
    return res;  

@app.route('/api/allmeterreadings/<string:meter_id>', methods=['GET'])
def meter_view(meter_id):
	"""
		GET THE LAST READING FOR A PARTICULAR METER
	"""
	req = requests.get(f'https://fornewhft.herokuapp.com/api/allmeterreadings/{meter_id}')
	data = json.loads(req.content)
	if request.method == 'GET':
		try:
			last_data = data[0]
			get_meter = last_data['meter']
			gas_supplied = last_data['quantity_supplied']
			gas_level = last_data['quantity_remaining']

			#print(f'requested meter==>{last_data}')
			print(f"For meter {get_meter}, quantity_supplied:quantity_remaining ==> {gas_supplied}:{gas_level}")
			
			# Store meter details	
			session['gas_level'] = gas_level
			session['get_meter'] = get_meter

			return(last_data)
		except IndexError:
			return('Oops! Your request is outta range. Please request for a different meter :)')
	else:
		return ('ONLY A GET REQUEST IS ALLOWED!!!')

@app.route('/api/gaslevel-notification/<string:meter_id>', methods=['GET'])
def gas_usage_alert(meter_id):
	"""
	Check for gas level and compare with the message scale 
	"""
	if 'gas_level' in session and 'get_meter' in session:
		gas_level = session['gas_level']
		get_meter = session['get_meter']
		print(f'gas meter & level ==> {get_meter} => {gas_leve}')

		# Gas usage scale
		scale = {
	            'track 1':f'Dear customer, you have {gas_level}kg of gas left. Relax, you are good!', #12kg - 10kg
	            'track 2':f'Dear customer, you have {gas_level}kg of gas left. Keep the fire burning!', #9.99kg - 8kg
	            'track 3':f'Dear customer, you have {gas_level}kg of gas left. We’ve got your back: do the cooking!', #7.99 – 6kg
	            'track 4':f'Dear customer, you have {gas_level}kg of gas left. We are actively monitoring your gas level. Relax!', #5.99 – 4kg
	            'track 5':f'Dear customer, you have {gas_level}kg of gas left. We will contact you for a bottle swap when you get to 2kg!', #3.99kg – 2.1kg
	            'track 6':f'Dear customer, you have {gas_level}kg of gas left. Your gas level is low. You will be contacted for a bottle swap. You are covered!', #<=1.9kg
	            'track 7':f'Dear customer, you have {gas_level}kg of gas left. 12kg of gas has been delivered to you. Go explore your culinary skills!' #12kg
	        }

		# Check gas level and return a message
		if gas_level <= 2:
			res = scale['track 6']
			return Response ({
				'meter':get_meter,
				'last_gas_quantity_used':gas_level,
				'alert message': res
            })
		elif gas_level > 2 and gas_level <= 3.9:
			res = scale['track 5']
			return Response ({
				'meter':get_meter,
				'last_gas_quantity_used':gas_level,
				'alert message': res
            })
		elif gas_level >= 4 and gas_level < 6:
			res = scale['track 4']
			return Response ({
				'meter':get_meter,
				'last_gas_quantity_used':gas_level,
				'alert message': res
            })
		elif gas_level >= 6 and gas_level <= 7.9:
			res = scale['track 3']
			return Response ({
				'meter':get_meter,
				'last_gas_quantity_used':gas_level,
				'alert message': res
            })
		elif gas_level >= 8 and gas_level <= 9.9:
			res = scale['track 2']
			return Response ({
				'meter':get_meter,
				'last_gas_quantity_used':gas_level,
				'alert message': res
            })
		elif gas_level >= 10 and gas_level <= 11.9:
			res = scale['track 1']
			return Response ({
				'meter':get_meter,
				'last_gas_quantity_used':gas_level,
				'alert message': res
            })
		elif gas_level == 12:
			res = scale['track 7']
			return Response ({
				'meter':get_meter,
				'last_gas_quantity_used':gas_level,
				'alert message': res
            })
	else:
		print('Gas level is Null or Meter not found!')
		return ({
				'message':'Oops! This meter id is not found !!!',
				'status':204
			})

if __name__ == '__main__':
    app.run(debug=True)