#!/usr/bin/env python3

import sys
import xmltodict
import psycopg2



toursfile = sys.argv[1]


dsn = 'dbname=ght user=pgsql password=xyz host=localhost'

def main():
    conn = _db_new_connection(dsn)
    toursdata = xmltodict.parse(open(toursfile, mode='r', encoding="utf-8").read(),
                                force_list={'tours': True,
                                            'stops': True,
                                            'vehicle': True,
                                            'address': True
                                            }
                                )
    #tours
    tnum = 0
    for t in toursdata['toursdata']['tours']: #yeah, that is a hideous name
        tnum += 1
        #print(str(t))
        
        insert_sql = """ INSERT INTO tours
            (id, status, missing_vehicle_data, license_plate, planned_begin,
            planned_end, haulier, transport_company, customer, vehicle_owner_code)
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s );"""

        update_sql = """UPDATE tours SET (id, status, missing_vehicle_data, license_plate, planned_begin,
            planned_end, haulier, transport_company, customer, vehicle_owner_code) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            WHERE id = %s ;"""

        #t
        values = [
            t['id'], t['status'], t['missing_vehicle_data'], t['license_plate'], t['planned_begin'],
            t['planned_end'], t['haulier'], t['transport_company'], t['customer'], t['vehicle_owner_code']
            ]
        print("t", end='')
        _insert_or_update(conn, insert_sql, update_sql, values)

        #stops
        #sometimes there is a tour with no stops, that's weird.  set empty list
        if not 'stops' in t: t['stops'] = []
        for s in t['stops']:

            insert_sql = """ INSERT INTO stops
                (id, type, time_window_begin, time_window_end, rta, tours_id)
                VALUES ( %s, %s, %s, %s, %s, %s );"""

            update_sql = """UPDATE stops SET (id, type, time_window_begin, time_window_end, rta, tours_id) = (%s, %s, %s, %s, %s, %s )
                WHERE id = %s ;"""

            values = [ s['id'], s['type'], s['time_window_begin'], s['time_window_end'],
                       s['rta'], t['id']
                       ] #t['id'] is deliberatly a foreign key
            print("s", end='')
            _insert_or_update(conn, insert_sql, update_sql, values)
            
            #address(s) yeah I know we should decide whether or not we are pluralizing, that's just the ghtrack way.
            for a in s['address']:

                
                #there should really only be one address per stop, it's just the
                #way the xml is organized.  
                insert_sql = """ INSERT INTO address
                    (location_id, company, country, city, zipcode, street, score, latitude, longitude)
                    VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s );"""
                update_sql = """UPDATE address SET (location_id, company, country, city, zipcode, street, score, latitude, longitude) =
                    ( %s, %s, %s, %s, %s, %s, %s, %s, %s )
                    WHERE location_id = %s ;"""
                values = [ a['location_id'], a['company'], a['country'], a['city'], a['zipcode'],
                           a['street'], a['score'], a['latitude'], a['longitude']
                           ]
                _insert_or_update(conn, insert_sql, update_sql, values)

                #join table stops_address (because addresses probably are used by multiple stops but I am not sure if stops always have just one)
                insert_sql = """ INSERT INTO stops_address
                    (stops_id, address_location_id)
                    VALUES ( %s, %s );"""
                #there is no point in updating since it will be the same as what is there.
                update_sql = "" 

                print("a", end='')
                _insert_or_update(conn, insert_sql, update_sql, [ s['id'], a['location_id'] ])

            
        #vehicles in tours
        vnum = 1
        if not 'vehicle' in t: t['vehicle'] = []
        for v in t['vehicle']:

            #vehicles do not seem to always have a longitude and latitude and timestamp, but may. null them if they do not exist
            if not 'latitude' in v.keys() : v['latitude'] = None
            if not 'longitude' in v.keys(): v['longitude'] = None
            if not 'timestamp' in v.keys(): v['timestamp'] = None
            if not 'name' in v.keys(): v['name'] = None


            #vehicles have to have a uuid don't they?
            if not 'uuid' in v.keys():
                print("no uuid for vehicle in tour: "+t['id'])
                v['uuid']=v['license_plate']
            

            insert_sql = """ INSERT INTO vehicle
                (uuid, data_gate_open, latitude, longitude, timestamp, license_plate, name)
                VALUES ( %s, %s, %s, %s, %s, %s, %s );"""
            update_sql = """UPDATE vehicle SET (uuid, data_gate_open, latitude, longitude, timestamp, license_plate, name) =
                    ( %s, %s, %s, %s, %s, %s, %s )
                    WHERE uuid = %s ;"""

            values = [ v['uuid'], v['data_gate_open'], v['latitude'], v['longitude'], v['timestamp'], v['license_plate'], v['name'] ]

            print()
            print('tour: ' + t['id'] + ' vehicle: ' +str(vnum))
            vnum += 1
            print("v", end='')
            _insert_or_update(conn, insert_sql, update_sql, values)


            #join table tours_vehicle (are vehicles in more than one tour at a time? possibly!)
            insert_sql = """ INSERT INTO tours_vehicle
                (tours_id, vehicle_uuid)
                VALUES ( %s, %s );"""
            #there is no point in updating since it will be the same as what is there.
            update_sql = ''
            _insert_or_update(conn, insert_sql, update_sql, [ t['id'], v['uuid'] ])


        #just do one tour for debug
        #exit()

def _insert_or_update(conn, insert_sql, update_sql, values):
        try:
            cur = conn.cursor()
            res = cur.execute(insert_sql, values)
            conn.commit()
            print("i", end=' ')

            return()
            print("should not get here")
        except psycopg2.IntegrityError as e:
            #update existing row instead
            #extra id/primary key on the end so we can fill the "where" clause parameter
            print("u", end=' ')
            conn.commit()

        if update_sql == "":
            #don't bother if we have no update_sql
            return()

        #try updating existing row
        try:
            values.append(values[1])
            cur = conn.cursor()
            res = cur.execute(update_sql, values)
            conn.commit()
        except Exception as e:
            print("error updating: "+str(e))

#new db connection 
def _db_new_connection(dsn):
    print("try to connect..")
    try:
        myConn = psycopg2.connect(dsn)
        print("DB connection established")
    except Exception as e:
        print("Can\'t connect to the database: "+str(e))
        #raise IOError
        exit()
        
    print("OK new connection")
    return myConn


if __name__ == '__main__':
    main()
        
