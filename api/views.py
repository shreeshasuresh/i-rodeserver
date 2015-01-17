
##############################################
#                                            #
#           Developer: Shreesha S            #
#     Contact: shreesha.suresh@gmail.com     #
#               Version 1.0                  #
#                                            #
##############################################

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json

from api.models import reviews
from api.models import tripInfo
from api.models import vehicleInfo


# 1. API to add infromation to the database when the user gives a feedback.
@csrf_exempt
def addInformation(request):
	
	if request.method == 'POST':
		try:
			vehicle_number = request.POST['vehiclenumber']
			# Replace vehicle number to upper case and remove spaces for uniformity in database
			vehicle_number = vehicle_number.upper()
			vehicle_number = vehicle_number.replace(" ", "")
			
			# Check if vehicle number is missing. If yes, print error message.
			if vehicle_number == "":
				response_message = {}
				response_message['message'] = 'Aborted. Critical information missing.'
				return HttpResponse(json.dumps(response_message))

			# Check the database to find any matching entries. If yes, get the id, else assign a None value.
			try:	
				vehicle_present_in_db = vehicleInfo.objects.get(vehicleNumber=vehicle_number)			
				vehicle_id_in_db = vehicle_present_in_db.id
		
			except:
				vehicle_id_in_db = None

			# If vehicle is already present in DB, add only trip information and review to the DB.
		
			if vehicle_id_in_db:
				trip_info = tripInfo(date = request.POST['date'],
								time = request.POST['time'],
								location = request.POST['location'],
								driverName = request.POST['drivername'],
								photoLink = request.POST['photolink'],
								vehicle = vehicleInfo.objects.get(id = vehicle_id_in_db))

				trip_info.save()
				review_info = reviews( review = request.POST['review'],
								rating = request.POST['rating'],
								sourceInfo = vehicleInfo.objects.get(id = vehicle_id_in_db))
				review_info.save()
				response_message = {}
				response_message['message'] = 'Success'
				return HttpResponse(json.dumps(response_message))

			# If vehicle information not present in the DB, then add all information to the DB.
			else:
				vehicle_info = vehicleInfo(vehicleNumber = vehicle_number,
								transportMode = request.POST['transportmode'],)

				vehicle_info.save()
				
				trip_info = tripInfo(date = request.POST['date'],
								time = request.POST['time'],
								location = request.POST['location'],
								driverName = request.POST['drivername'],
								photoLink = request.POST['photolink'],
								vehicle = vehicleInfo.objects.get(id = vehicle_info.id))
				
				trip_info.save()

				review_info = reviews(rating = request.POST['rating'],
								review = request.POST['review'],
								sourceInfo = vehicleInfo.objects.get(id = vehicle_info.id))
				review_info.save()

				response_message = {}
				response_message['message'] = 'Success'
				return HttpResponse(json.dumps(response_message))
		except:
			response_message = {}
			response_message['message'] = 'Aborted. Critical information missing.'
			return HttpResponse(json.dumps(response_message))


	else:
		response_message = {}
		response_message['message'] = 'Aborted. Not a valid POST request.'
		return HttpResponse(json.dumps(response_message))



# 2. API to get the reviews/ratings of a particular vehicle using the search query provided by the user. 
@csrf_exempt
def getInformation(request):

	if request.method == 'POST':
		vehicle_number = request.POST['vehiclenumber']
		vehicle_number = vehicle_number.upper()
		vehicle_number = vehicle_number.replace(" ", "")
		
		# Check if vehicle number is missing. If yes, print error message.
		if vehicle_number == "":
			response_message = {}
			response_message['message'] = 'Aborted. Critical information missing.'
			return HttpResponse(json.dumps(response_message))

		# Check if any reviews are there against vehicle number (POST request)
		try:
			vehicle_present_in_db = vehicleInfo.objects.get(vehicleNumber=vehicle_number)			
			vehicle_id_in_db = vehicle_present_in_db.id
			review_data = reviews.objects.filter(sourceInfo = vehicle_id_in_db)

			dictionary = {}
			count = 0
			total_rating = 0
			dict_list = []
			
			# Loop over all ratings to calculate the total and hence find the average.
			# And also loop over all non-void reviews to add to a dictionary.
			for i in review_data:
				count += 1
				total_rating = total_rating + i.rating
				if i.review == "":
					continue
				dictionary[count] = i.review
			
			# Calculate the average rating and append all reviews to a list.
			average_rating = total_rating / count
			avg_rating = {}
			avg_rating["Average_Rating"] = average_rating
			dict_list.append(avg_rating)
			dict_list.append(dictionary)
		
			return HttpResponse(json.dumps(dict_list))
		
		except:
			dictionary = {}
			dictionary['Status'] = "Rating / Review not available."
			return HttpResponse(json.dumps(dictionary))

	else:
		response_message = {}
		response_message['message'] = 'Aborted. Not a valid POST request.' 
		return HttpResponse(json.dumps(response_message))



# 3. API to get the average rating of a particular vehicle using the search query provided by the user. 
@csrf_exempt
def getRating(request):

	if request.method == 'POST':
		vehicle_number = request.POST['vehiclenumber']
		vehicle_number = vehicle_number.upper()
		vehicle_number = vehicle_number.replace(" ", "")
		
		# Check if vehicle number is missing. If yes, print error message.
		if vehicle_number == "":
			response_message = {}
			response_message['message'] = 'Aborted. Critical information missing.'
			return HttpResponse(json.dumps(response_message))

		try:
			# Filter the ratings based on the vehicle ID of the input.
			vehicle_present_in_db = vehicleInfo.objects.get(vehicleNumber=vehicle_number)			
			vehicle_id_in_db = vehicle_present_in_db.id
			rating_data = reviews.objects.filter(sourceInfo = vehicle_id_in_db)

			count = 0
			total_rating = 0

			# Loop over all ratings to calculate the total and hence find the average.
			for i in rating_data:
				count += 1
				total_rating = total_rating + i.rating
				
			average_rating = total_rating / count
			avg_rating = {}
			avg_rating["Average_Rating"] = average_rating
		
			return HttpResponse(json.dumps(avg_rating))
		
		except:
			dictionary = {}
			dictionary['Status'] = "Rating / Review not available."
			return HttpResponse(json.dumps(dictionary))

	else:
		response_message = {}
		response_message['message'] = 'Aborted. Not a valid POST request.' 
		return HttpResponse(json.dumps(response_message))
