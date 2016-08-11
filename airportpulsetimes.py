import csv
from datetime import datetime
from operator import itemgetter


schedule_file = "Flights2015.csv"

DAYS_IN_WEEK = 7

def build_airport_database():

	# Open the CSV and Upsert each row - rows already in will be skipped, new rows added, updated rows updated
	print "Creating Flight Database..."
	keys = []
	airports = dict()
	carriers = dict()
	r = open(schedule_file)
	# File must be saved as windows csv
	raw_schedule_reader = csv.reader(r)
	rownum = 0
	for row in raw_schedule_reader:
		if (rownum == 0):
			keys = row
			
			rownum += 1
		
		else:

			carrier = row[keys.index('carrier')]
			opcarrier = row[keys.index('opcarrier')]
			number = row[keys.index('fltno')]
			departure_time = datetime.strptime(row[keys.index('departure_time')], "%H:%M:%S")
			arrival_time = row[keys.index('arrival_time')]
			origin = row[keys.index('origin')]
			destination = row[keys.index('destination')]
			
			equip = row[keys.index('equip')]
			seats_f = int(row[keys.index('seats_fst')])
			seats_c = int(row[keys.index('seats_bus')])
			seats_y = int(row[keys.index('seats_eco')])

			seats_total = seats_f + seats_c + seats_y

			#Filter out freighters and flights with 0 seats
			#print seats_y, seats_c, seats_f

			if(not airports.has_key(origin)):
				airports[origin] = Airport(origin)

			if(not carriers.has_key(carrier)):
				carriers[carrier] = Carrier(carrier)

			carriers[carrier].number_of_flights += 1

			if(origin not in carriers[carrier].airports):
				carriers[carrier].airports.append(origin)

			if(seats_y + seats_c + seats_f > 0):


				effective_from = row[keys.index('effective_from')]
				effective_to = row[keys.index('effective_to')]
				opdays = []
				#assign opdays to list - these will be used to generate individual departures based on seed date
				## KEEP TRACK that we're moving 1-7 opday array into a 0-6 indexed list!!! ##
				for day in range(1,8):
					
					if(row[keys.index('opday%d' % day)] == 't'):
						opdays.append(True)
					else:
						opdays.append(False)

				flights = list()
			
				start_date = datetime.strptime(effective_from, "%m/%d/%y").date()
				end_date = datetime.strptime(effective_to, "%m/%d/%y").date()
				
				number_of_valid_days = (end_date - start_date).days
				
				#remember that Monday is 0, Sunday is 6
				start_day_of_week = start_date.weekday()
				
				#need to go through each valid day and determine if the flight operates by checking the opday list
				#k is a day counter - start_day_of_week is the offset to start countring from - (say "start on Thursday and check the next 100 days")
				num_departures = 0

				for k in range(0, number_of_valid_days):
					if(opdays[(k+start_day_of_week)%DAYS_IN_WEEK] == True):
						num_departures += 1

			airports[origin].departures_per_hour[departure_time.hour] += seats_total * num_departures
			airports[origin].number_seats_tot += seats_total * num_departures
			airports[origin].total_flights += num_departures

			if(airports[origin].total_flights == 0):
				airports[origin].number_seats_per_departure = 0
			else:
				airports[origin].number_seats_per_departure = airports[origin].number_seats_tot / airports[origin].total_flights

			


	row = 0
	sorted(airports)
	for key in airports:

		for elem in range(0,24):
			if(max(airports[key].departures_per_hour) == 0):
				airports[key].capacity_per_hour[elem] = 0.00
			else:
				airports[key].capacity_per_hour[elem] = '{:.2f}'.format(airports[key].departures_per_hour[elem] / float(max(airports[key].departures_per_hour)))
		print airports[key].__dict__
		print row
		row += 1

	for carrier in carriers:
		print carriers[carrier].__dict__
		#print carriers[carrier].number_of_flights.size


	with open('airport_pulses.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, dialect='excel')
		str_output = ""
		writer.writerow(['Name', 'Total Flights', 'Number of Seats', 'Seats per Departures', '0:00', '1:00', '2:00', '3:00', '4:00', '5:00', '6:00', '7:00','8:00','9:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00'])
		
		row = list()
		# Write to CSV
		for key in airports:
			row = [airports[key].name, airports[key].total_flights, airports[key].number_seats_tot, airports[key].number_seats_per_departure]
			row += airports[key].capacity_per_hour
			writer.writerow(row)

			
		
		
		
class Carrier:

	def __init__(self, carrier_name):
		self.name = carrier_name
		self.number_of_flights = 0
		self.airports = []
	

class Airport:

	def __init__(self, airport_code):
		self.name = airport_code
		self.total_flights = 0
		self.departures_per_hour = [0] * 24
		self.capacity_per_hour = [0] * 24
		self.number_seats_tot = 0
		self.number_seats_per_departure = 0.0


# create airports, unique, 
# read each flight line, calculate number of total flights described, increment TOD element by that amount

build_airport_database()
