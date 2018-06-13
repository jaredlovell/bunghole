#!/usr/bin/env python3

import sys, argparse, json
import xmltodict


def _get_args():
    '''
 --vehicles vehicles.xml
 --tours tours.xml
    '''
    
    parser = argparse.ArgumentParser()
    #parser.add_argument('--vehicles', required=True, help='json input file.  --threads will be ignored unless --test is defined')
    parser.add_argument('--tours', required=True, help='json input file')
    parser.add_argument('--vehicle', required=True, help='vid')
    args = parser.parse_args()
    return(args)


class Main():
    def __init__(self):
        self.args = _get_args()


        self.registry = {
                            'tractors': {},
                            'trailers': {},
                            'vehicles': {},
                            'tours': {},
                            'tour_vehicles': {},
                            'tour_stops': {}
                        }

        #self.vehicles_injest(self.registry)
        self.tours_injest(self.registry)

        #run reports
        #self.report_tours_and_vehicles(self.registry)

        #self.report_tours_only(self.registry)

        self.tour_vehicle_report(self.registry, self.args.vehicle)
        

    def tours_injest(self, registry):


        tours_data = xmltodict.parse(open(self.args.tours, mode='r', encoding="utf-8").read(),
                                force_list={'tours': True,
                                            'stops': True,
                                            'vehicle': True,
                                            'address': True
                                            }
                                )
        tnum = 0

        for t in tours_data['toursdata']['tours']: #yeah, that is a hideous name
            tnum += 1
            #some tours are missing whole sections, for instance, they may have no "stops".  set empty list
            if not 'vehicle' in t: t['vehicle'] = []
            if not 'stops' in t: t['vehicle'] = []

            #root of tour
            try:
                tour = {
                    'id': t['id'],
                    'status': t['status'],
                    'missing_vehicle_data': t['missing_vehicle_data'],
                    'license_plate': t['license_plate'],
                    'planned_begin': t['planned_begin'],
                    'planned_end': t['planned_end'],
                    'haulier': t['haulier'],
                    'transport_company': t['transport_company'],
                    'customer': t['customer'],
                    'vehicle_owner_code': t['vehicle_owner_code'],
                    'vehicles': [],
                    'stops': []
                    }
            except Exception as e:
                print("missing data for tour: " +str(tour) +': '+str(e))
                    
            else: 
                registry['tours'][tour['id']] = tour


            #list of vehicles we may have
            registry['tours'][tour['id']]['vehicles'] = []
            
            #print("tour: "+ str(tour['id']) )

            #stops in tours
            #sometimes there is a tour with no stops, that's weird.  set empty list
            if not 'stops' in t: t['stops'] = []
            for s in t['stops']:

                stop = { 'id': s['id'],
                         'type': s['type'],
                         'time_window_begin': s['time_window_begin'],
                         'time_window_end': s['time_window_end'],
                         'rta' : s['rta'],
                         'addresses': [],
                         'facility': ""
                         }


                
                #address(s) yeah I know we should decide whether or not we are pluralizing, that's just the ghtrack way.
                for a in s['address']:
                    facility = a['location_id']
                    #registry['tours'][tour['id']]['stops']
                    stop['facility'] = facility
                    #print("facility: "+facility)
                    
                    #there should really only be one address per stop, it's just the
                    #way the xml is organized.  
                    
                #update tour list of stops
                registry['tours'][tour['id']]['stops'].append(stop)


            # end stops#
            
            #vehicles in tours
            vnum = 0
            for v in t['vehicle']:
                vnum += 1
                #vehicles do not seem to always have a longitude and latitude and timestamp, but may. null them if they do not exist
                if not 'latitude' in v.keys() : v['latitude'] = None
                if not 'longitude' in v.keys(): v['longitude'] = None
                if not 'timestamp' in v.keys(): v['timestamp'] = None
                if not 'name' in v.keys(): v['name'] = None


                #vehicles have to have a uuid don't they?
                if not 'uuid' in v.keys():
                    #print("no uuid for vehicle in tour: "+t['id'])
                    v['uuid']=v['license_plate']
                

                try:
                    #this isn't necessary due to how simple the structure is, but it does verify that we have all these fields in registry
                    vehicle = {
                        'name': self._clean_plate(v['name']),
                        'license_plate': self._clean_plate(v['license_plate']),
                        'uuid': v['uuid'],
                        'data_gate_open': v['data_gate_open'],
                        'latitude': v['latitude'],
                        'longitude': v['longitude'],
                        'timestamp': v['timestamp'],
                        }

                except Exception as e:
                    print("missing data for tour vehicle: " +str(vehicle) +': '+str(e))
                    
                else:
                    #add to tour under vehicles list
                    registry['tours'][t['id']]['vehicles'].append(vehicle)

                #also add to 'join' dict tour_vehicles, which maps the other way from vehicle -> tours
                #vehicles can be in more than one tour
                #print("tour_vehicle: "+vehicle['name'])
                if not vehicle['name'] in registry['tour_vehicles']:
                    registry['tour_vehicles'][vehicle['name']] = []
                #else:
                #    print("another tour had this vehicle already")

                registry['tour_vehicles'][vehicle['name']].append(tour['id'])
                        
                #print("tour vehicle: "+ str(vehicle['name']) )

            #end vehicles
                
    def tour_vehicle_report(self, registry, vehicle):
        mytours = registry['tour_vehicles'][vehicle]
        print("vehicle "+vehicle + "is in "+str(len(mytours)) + "tours: " )
        for t in mytours:
            stops = registry['tours'][t]['stops']
            #print(str(stops))
            if len(stops) == 2:
                msg="src: " + registry['tours'][t]['stops'][0]['facility'] + " dst: " + registry['tours'][t]['stops'][1]['facility']
            
            else:
                msg = "more than two stops"
                
            print("tourid: "+t +
                  " " + msg + 
                  " begin: " + registry['tours'][t]['planned_begin'] +
                  " end: "+ registry['tours'][t]['planned_end'] +
                  " status: " + registry['tours'][t]['status']
                  )



    def _clean_plate(self, vid):
        """
        _clean_plate takes a vid string and removes whitespace and dashes, and converts all letters to uppercase
        @param vid: a string representing a vehicle identification
        @return: samve vid, but with spaces and dashes removed and all letters uppercase
        """
        try:
            name = "".join("".join(vid.split()).split('-')).upper()
        except:
            name = "NONAME"
        return(name)

    def _clean_tourid(self, tid):
        '''just remove spaces and make everything uppercase'''
        try:
            name = "".join("".join(tid.split())).upper()
        except:
            name = "NONAME"
        return(name)


if __name__ == "__main__":
    m = Main()
    
