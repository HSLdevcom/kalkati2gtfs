"""
Kalkati to GTFS converter
Beware: it simplifies some things.

(c) 2011 Stefan Wehrmeyer http://stefanwehrmeyer.com
License: MIT License

"""

from datetime import timedelta
import os, errno
import sys
import xml.sax
from xml.sax.handler import ContentHandler

from calendar import to_ints, splice, true_for_all, true_for_some, true_for_weeks, get_date, get_dates
from coordinates import KKJxy_to_WGS84lalo

#from django.contrib.gis.geos import Point # needed for transformations

timezone = "Europe/Helsinki"

"""
Kalkati Transport modes
1   air
2   train
21  long/mid distance train
22  local train
23  rapid transit
3   metro
4   tramway
5   bus, coach
6   ferry
7   waterborne
8   private vehicle
9   walk
10  other

GTFS Transport Modes
0 - Tram, Streetcar, Light rail.
1 - Subway, Metro.
2 - Rail.
3 - Bus.
4 - Ferry.
5 - Cable car.
6 - Gondola, Suspended cable car.
7 - Funicular.
"""

KALKATI_MODE_TO_GTFS_MODE = {
    "2": "2",
    "21": "2",
    "22": "2",
    "23": "2",
    "3": "1",
    "4": "0",
    "5": "3",
    "6": "4",
    "7": "4"
}


class KalkatiHandler(ContentHandler):
    agencies = []
    data = {}

    route_count = 0
    service_count = 0
    routes = {}

    stations = {}
    stops = []

    synonym = False
    stop_sequence = None
    trip_id = None
    route_agency_id = None
    route_name = None
    service_validities = None
    service_mode = None
    transmodes = {}
    transattrs = {}

    gtfs_files = {}

    def add_stop(self, attrs):
        #point = Point(x=float(attrs['X']), y=float(attrs['Y']), srid=2393) # KKJ3
        #point.transform(4326) # WGS84
        KKJNorthing = float(attrs['Y'])
        KKJEasting = float(attrs['X'])
        KKJLoc = {'P': KKJNorthing, 'I' : KKJEasting}
        WGS84lalo = KKJxy_to_WGS84lalo(KKJin=KKJLoc, zone=3)
	(company, stop) = attrs['StationId'].split(":",1)
        self._store_data(company, "stops", [attrs['StationId'].split(":",1)[-1],
                attrs.get('Name', "Unnamed").replace(",", " "),
                str(WGS84lalo['La']), str(WGS84lalo['Lo'])])

    def add_agency(self, attrs):
        id = attrs['CompanyId']
        agency_name = attrs['Code'].split(":")[-1].replace(",", " ")
        
        self.agencies.append(id)
        self.data[id] = {}
        self.stations[id] = {}
        self.routes[id] = {}
        self.transmodes[id] = {}
        self.transattrs[id] = {}
        self._store_data(id, "agency", [id, agency_name, "http://www.matka.fi", timezone]) # can't know

        self.gtfs_files[id] = {}
        names = ['stops', 'agency', 'calendar', 'stop_times', 'trips', 'routes', 'calendar_dates']
        
        try:
            os.makedirs(self.directory + "/" + agency_name)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(self.directory + "/" + agency_name):
                pass
            else: raise

        for name in names:
            self.gtfs_files[id][name] = file(os.path.join(self.directory + "/" + agency_name, "%s.txt" % name), "w")

        init_files(self.gtfs_files[id])

    def add_calendar(self, attrs):
        service_id = attrs['FootnoteId']
        first = attrs['Firstdate']
        first_date = get_date(first)
        vector = attrs['Vector']

        if not len(vector):
            null = ["0",] * 7
            empty_date = first.replace("-", "")
            self._store_data("all", "calendar", [service_id,] + null +
                    [empty_date, empty_date])
            return

        end_date = first_date + timedelta(days=len(vector))

        days = to_ints(list(vector))
        overlaps = true_for_all(days)
        sub = true_for_some(days)
        week_overlaps = true_for_weeks(overlaps, first_date)[:7]

        fd = str(first_date).replace("-", "")
        ed = str(end_date).replace("-", "")
        self._store_data("all", "calendar", [service_id,] + map(str, week_overlaps) +
                [fd, ed])

        # add irregular dates
        for d in get_dates(sub, first_date):
            self._store_data("all", "calendar_dates", [service_id, str(d).replace("-", ""), '1'])

    def add_stop_time(self, attrs):
        self.stop_sequence.append(attrs['StationId'])
        arrival_time = ":".join((attrs["Arrival"][:2],
                attrs["Arrival"][2:], "00"))
        if "Departure" in attrs:
            departure_time = ":".join((attrs["Departure"][:2],
                    attrs["Departure"][2:], "00"))
        else:
            departure_time = arrival_time
        self._write_data(self.route_agency_id, "stop_times", [self.trip_id, arrival_time,
                departure_time, attrs["StationId"].split(":",1)[-1], attrs["Ix"]])

    def add_route(self, route_id):
        route_type = "3"  # fallback is bus
        route_type_original = ""
        (company, id) = self.service_mode.split(":",1) 
        if id in self.transmodes[company]:
            trans_mode = self.transmodes[company][id]
            if trans_mode[0] in KALKATI_MODE_TO_GTFS_MODE:
                route_type = KALKATI_MODE_TO_GTFS_MODE[trans_mode[0]]
                route_type_original = trans_mode[1]

        self._store_data(self.route_agency_id, "routes", [route_id, self.route_agency_id,
                self.route_short_name, self.route_name.replace(",", "."), 
                route_type, route_type_original], {
            "stops": self.stops
        })

    def add_trip(self, route_id):
        for service_id in self.service_validities:
            self._store_data(self.route_agency_id, "trips", [route_id, service_id, self.trip_id,])

    def _store_data(self, company, key, data, extra=None):
        if (company == "all"):
            for a in self.agencies:
                self._store_data(a, key, data)
            return
        
        if(key not in self.data[company]): self.data[company][key] = []

        d = {
            "data": data
        }

        if extra:
            d.update(extra)

        self.data[company][key].append(d)

    def _write_data(self, company, key, data):
        """Write data entry directly to file that corresponds to key."""
        write_values(self.gtfs_files[company], key, data)

    def startElement(self, name, attrs):
        if not self.synonym and name == "Company":
            self.add_agency(attrs)
        elif not self.synonym and name == "Station":
            self.add_stop(attrs)
            (company, id) = attrs['StationId'].split(":",1)
            self.stations[company][id] = {
                "name": attrs["Name"]
            }
        elif not self.synonym and name == "Trnsattr":
            (company, id) = attrs['TrnsattrId'].split(":",1)
            self.transattrs[company][id] = attrs['Name'].replace(",", ".")
        elif not self.synonym and name == "Trnsmode":
            if "ModeType" in attrs:
                (company, id) = attrs['TrnsmodeId'].split(":",1)
                self.transmodes[company][id] = (attrs['ModeType'], attrs['Name'])
        elif name == "Footnote":
            self.add_calendar(attrs)
        elif name == "Service":
            self.service_count += 1
            if self.service_count % 1000 == 0:
                print "Services processed: %d" % self.service_count
            self.trip_id = attrs["ServiceId"]
            self.service_validities = []
            self.stop_sequence = []
            self.stops = []
        elif name == "ServiceNbr":
            self.route_agency_id = attrs["CompanyId"]
            self.route_name = attrs.get("Name", "")
            self.route_short_name = attrs.get("Variant", attrs.get("ServiceNbr", ""))
        elif name == "ServiceValidity":
            self.service_validities.append(attrs["FootnoteId"])
        elif name == "ServiceTrnsmode":
            self.service_mode = attrs["TrnsmodeId"]
        elif name == "Stop":
            (company, id) = attrs["StationId"].split(":",1)
            if id in self.stations[company]:
                self.add_stop_time(attrs)
                self.stops.append(self.stations[company][id])
            else:
                print "Skipping " + attrs["StationId"]
        elif name == "Synonym":
            self.synonym = True

    def endElement(self, name):
        if name == "Synonym":
            self.synonym = False
        elif name == "Service":
            route_seq = "-".join(self.stop_sequence)
            if route_seq in self.routes:
                route_id = self.routes[self.route_agency_id][route_seq]
            else:
                self.route_count += 1
                route_id = str(self.route_count)
                self.routes[self.route_agency_id][route_seq] = route_id
                self.add_route(route_id)
            self.add_trip(route_id)
            self.trip_id = None
            self.stop_sequence = None
            self.route_agency_id = None
            self.route_name = None
            self.route_short_name = None
            self.service_validities = None
            self.service_mode = None


def init_files(files):
    fields = {
        "agency": (u'agency_id', u'agency_name', u'agency_url',
            u'agency_timezone',),
        "stops": (u'stop_id', u'stop_name', u'stop_lat', u'stop_lon',),
        "routes": (u"route_id", u"agency_id", u"route_short_name",
            u"route_long_name", u"route_type", u"route_type_original",),
        "trips": (u"route_id", u"service_id", u"trip_id",),
        "stop_times": (u"trip_id", "arrival_time", "departure_time",
            u"stop_id", u"stop_sequence",),
        "calendar": (u'service_id', u'monday', u'tuesday', u'wednesday',
            u'thursday', u'friday', u'saturday', u'sunday', u'start_date',
            u'end_date',),
        "calendar_dates": (u'service_id', u'date', u'exception_type')
    }

    for name in files:
        write_values(files, name, fields[name])


def write_values(files, name, values):
    for i in range(len(values)):
        # XXX implement full csv escaping rules
        if ',' in values[i]:
            values[i] = '"' + values[i] + '"'
    files[name].write((u",".join(values) + u"\n").encode('utf-8'))


def transform(data):
    if not "routes" in data:
        return data

    new_routes = {}
    route_replacements = {}

    for route in data["routes"]:
        # if the route has no long name, form one based on terminal stations:
        if (not route["data"][3]) or (route["data"][3] == "."):
            name = route["stops"][0]["name"] + ' -- ' + route["stops"][-1]["name"]

            route["data"][3] = name

        route["data"][2] = route["data"][2].strip(", ")

        # filter out some invalid short names:
        if route["data"][2] in ["0", "MH_EI_LINJATUNNUSTA", "MH_Expr", "MH_Pika", "Metro", "Lautta"]:
            route["data"][2] = ""

        # filter out short names that actually are internal long numbers:
        if len(route["data"][2])>4 and route["data"][2].isdigit():
            route["data"][2] = ""

    for route in data["routes"][:]:
        if tuple(route["data"][1:]) in new_routes:
            route_replacements[route["data"][0]] = new_routes[tuple(route["data"][1:])]
            data["routes"].remove(route)
        else:
            new_routes[tuple(route["data"][1:])] = route["data"][0]

    for trip in data["trips"]:
        if trip["data"][0] in route_replacements:
            trip["data"][0] = route_replacements[trip["data"][0]]

    return data


def main(filename, directory):
    handler = KalkatiHandler()
    handler.directory = directory
    xml.sax.parse(filename, handler)

    for a in handler.agencies:
        for k in transform(handler.data[a]):
            for item in handler.data[a][k]:
                write_values(handler.gtfs_files[a], k, item["data"])

        for name in handler.gtfs_files[a]:
            handler.gtfs_files[a][name].close()

if __name__ == '__main__':
    try:
        filename = sys.argv[1]
        output = sys.argv[2]
    except IndexError:
        sys.stderr.write(
                "Usage: %s kalkati_xml_file output_directory\n" % sys.argv[0])
        sys.exit(1)
    main(filename, output)
