# tests

import requests
import json
import time

from datetime import datetime, timezone, timedelta

test_username = "b2756d6e-906d-46a9-8031-a3f60956b6dc"


def PostRideData():
	username = test_username
	flow= "testFlow"
	rideID = "5769"

	min_30 = timedelta(minutes=30)

	time_now = datetime.now()
	time_30_min_ago = time_now - min_30	 
	
	time_start_formatted = time_now.astimezone(tz=timezone.utc).isoformat() # time for system resources
	time_end_formatted = time_30_min_ago.astimezone(tz=timezone.utc).isoformat() # time for system resources



	endTime = "2022-05-27T17:08:42.000Z"
	startTime = "2022-05-27T17:08:42.000Z"

	createdAt = "2022-05-27T04:12:13.679Z"
	updatedAt = "2022-05-27T04:12:13.679Z"

	data = {
		"trajectoryData": {
			"waypoints": [
				{
					"type": "TrajectoryWaypoint", 
					"latitude": 34.04614, "longitude": -118.35753, 
					"timestamp": "2022-05-27T20:40:18.000-07:00", 
					"road_type": "footway", 
					"speed": 55.3, 
					"distance": 100.9, 
					"speed_limit": 104.585
				}
			], 
			"encoded": "ksxnEpdxpUmCgC{@w@OMz@yAt@qAJSGGIIsAmAu@q@QO][eAaAOMOMSSQQw@s@GEEEQOaA}@y@s@UWKKUSMMCAcB}Ay@w@CCk@g@IGMOUQm@i@CCUUcA}@e@c@CAB@LLMMCCcA{@s@o@w@q@II{@u@QOMMOO[[s@u@IEIIAAk@i@e@a@AAg@e@QO{@w@SQFa@KKfBaD?GLWLUFGfBaDBE?HCCGGsBiBYWIIk@g@u@q@F[_@[US}@y@QOA]MJONCHoBbCC?ORCh@EFWXQVKLyAhBA@UX}@fA{@dAQT@AQMUWYYUUc@_@SUA???wA}A_@e@oAqAOQu@y@CCEEQS]a@Ea@AAJOLWHQ`@u@JUVi@P]JYb@_A~AqD|@mBHMBId@gADILYWQk@SaA_@eAa@c@Q]MWKo@WOGMGICYKUKcBq@IEaA_@mAe@CAy@]IEOE?Aa@OyB_A]Oe@Q[Mo@UICMEKGIEe@Q]M_@OaAa@IC_@OGCGC[Mc@SOINHb@RZLFBFB^NHB`A`@PFLF\\Ld@PDBB@JFLDDBECMEFW@GNgABIHm@VoADSDSBGZaAb@oABIRi@n@eB\\cANMDGiBwAUOECOOSSOYeAgBMUU_@e@y@MUXUzCcCv@o@JKDKDI@K?MMeBG{@IuACa@GaANKt@i@fBsAWeAKWMUKQQQ}@h@gAn@iBjA}CnBk@\\uAx@]Ta@TYs@KWCESg@mBwEi@sAi@qAEKoB{EaEnCDHEIMYaAcCGMSi@Sg@KUBDFNTj@Pd@FLnA|C{@j@EBqBpAaAd@GLBDP\\L^Zx@HN?AJIECOSQg@CG??"
		},
		"flow": {}, 
		"endTime": endTime, 
		"startTime": startTime, 
		"cibicUser": {
			"roleApprovedAt": None, 
			"role": "testRole", 
			"username": username, 
			"_id": "628c0e22664d59c413e69651"
		},
		"username": username, 
		"_id": rideID, 
		"createdAt": createdAt, 
		"updatedAt": updatedAt, 
		"__v": 0, 
		"id": rideID
	}

	x = requests.post('https://m609zw34z5.execute-api.us-west-1.amazonaws.com/prod/ride-data', data=json.dumps(data), headers={'x-api-key': 'xOsPBbAKQjAnfmQ11O2haoocwbwXZ7map1cEUcgf'})
	return x


def PostJournalData():
	data = {
		"type": "reflection", 
		"answers": [None, None, None, None], 
		"journal": [
			{
				"prompt": "Rate your commute satisfaction:", 
				"formType": "satifaction", 
				"options": [
					{
						"label": "terrible", "face": "/static/media/Bad.e5809ad7.svg"
					}, {
						"label": "bad", "face": "/static/media/Meh.573478ce.svg"
					}, {
						"label": "okay", "face": "/static/media/Okay.db50e43b.svg"
					}, {
						"label": "good", "face": "/static/media/Good.679a76c9.svg"
					}, {
						"label": "great", "face": "/static/media/Great.d9a647bb.svg"
					}
				]
			},
			{
				"prompt": "Select all the characteristics of your ride:", 
				"formType": "multpleSelect", 
				"options": 
				[
					"Playful", "Hazardous", "Relaxing", "Healthy", "Tiring", "Rushed", "Stressful", "Unsafe", "Easy", "Liberating", "Slow", "Safe"
				]
			}, 
			{
				"prompt": "Describe your ride with one word or short phrase:", 
				"formType": "freeEntry", 
				"options": "My ride was..."
			},
			{
				"prompt": "What color best expresses how you feel about your last CiBiC ride?", 
				"formType": "colorEntry", 
				"options": ["blue", "yellow", "magenta", "light blue", "green", "pink"]
			},
			{
				"prompt": "Upload photos of your ride:", 
				"formType": "photo", 
				"optional": True
			}
		], 
		"image": None, 
		"userId": test_username, 
		"paveData": {
			"role": "testRole", 
			"username": test_username, 
			"name": "TEST USER", 
			"qs": "username="+test_username+"&name=CiBiCManagement&timestamp=2022-06-07T17:58:27.703437-05:00"
		}, 
		"role": None
		}
	x = requests.post( "https://73oajmp3pd.execute-api.us-west-1.amazonaws.com/prod", data=json.dumps(data), headers={'x-api-key': 'xOsPBbAKQjAnfmQ11O2haoocwbwXZ7map1cEUcgf', 'Content-Type': 'application/json'} )
	return x


# submit ride, submit journal
result1 = PostRideData()
print(result1.status_code, result1.content)
time.sleep(10)
result2 = PostJournalData()
print(result2.status_code, result2.text)

# submit journal, submit ride
#PostJournalData()
#PostRideData()
#
## submit journal for old ride after cut-off (accepted)
## submit journal for old ride before cut-off (declined)
#
## submit ride, submit ride, submit journal
#PostRideData()
#PostRideData()
#PostJournalData()
#
## submit journal, submit journal, submit ride
#PostJournalData()
#PostJournalData()
#PostRideData()
