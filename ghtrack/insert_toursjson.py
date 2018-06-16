#!/usr/bin/env python3

import sys, datetime
import json
import psycopg2



toursfile = sys.argv[1]


#dsn = 'dbname=ght user=pgsql password=xyz host=localhost'
dsn = 'dbname=ght user=jlovell host=localhost'

def main():
    conn = _db_new_connection(dsn)
    
    with open(toursfile, mode='r', encoding='utf-8') as toursjson:
        toursdata = json.load(toursjson)

    #tours
    tnum = 0
    
    for t in toursdata: 
        tnum += 1
        #print(json.dumps(str(t)))

        if 'vehicle' in t:
            #insert vehicle first.   There is just the one per tour (although same vehicle can be in more than one tour)
            #generally such "shared" vehicles will have redundant data.
            v = t['vehicle']

            #vehicles do not seem to always have a longitude and latitude and timestamp, but may. null them if they do not exist
            #this is ok when tour is not status: active
            if not 'latitude' in v.keys() : v['latitude'] = None
            if not 'longitude' in v.keys(): v['longitude'] = None

            if not 'timestamp' in v.keys():
                v['timestamp'] = datetime.datetime(1978, 1, 1)
            else:
                try:
                    datetime.datetime.strptime(v['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
                except:
                    print("bad dates "+str(v['timestamp']))
                    v['timestamp'] = datetime.datetime(1978, 1, 1)
            
            if not 'name' in v.keys(): v['name'] = None

            #clean these up
            v['name'] = _clean_plate(v['name'])
            v['license_plate'] = _clean_plate(v['license_plate'])

            
            #uuid is fairly worthless and I chose to discard it in favor of 'name' as a unique identifier.
            insert_sql = """ INSERT INTO vehicles
                (name, data_gate_open, latitude, longitude, timestamp, license_plate)
                VALUES ( %s, %s, %s, %s, %s, %s );"""
            update_sql = """UPDATE vehicles SET (name, data_gate_open, latitude, longitude, timestamp, license_plate) =
                    ( %s, %s, %s, %s, %s, %s )
                    WHERE name = %s AND timestamp = %s;"""

            values = [
                v['name'],
                v['data_gate_open'],
                v['latitude'],
                v['longitude'],
                v['timestamp'],
                v['license_plate']
                ]
            #print(values)

            keys = [v['name'], v['timestamp']]
            #print(keys)
            
            print()
            print('vehicle: '+ v['name'], end=' ')
            print("v", end='')
            _insert_or_update(conn, insert_sql, update_sql, values, keys)
            
        else:
            t['vehicle'] = {'name': None}


        #tour
        print('tour: ' + t['id'], end=' ')
        insert_sql = """ INSERT INTO tours
            (id, vehicles_name, status, missing_vehicle_data, license_plate, planned_begin,
            planned_end, completion_time, haulier, transport_company, vehicle_owner_code)
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s );"""

        update_sql = """UPDATE tours SET (id, vehicles_name, status, missing_vehicle_data, license_plate, planned_begin,
            planned_end, completion_time, haulier, transport_company, vehicle_owner_code) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            WHERE id = %s;"""

        values = [
            t['id'],
            t['vehicle']['name'],
            t['status'],
            t['missing_vehicle_data'],
            t['license_plate'],
            t['planned_begin'],
            t['planned_end'],
            t['completion_time'],
            t['haulier'],
            t['transport_company'],
            t['vehicle_owner_code']
            ]
        
        keys = [t['id'],]
        print("t", end='')
        _insert_or_update(conn, insert_sql, update_sql, values, keys)

        #stops
        #sometimes there is a tour with no stops, that's weird.  set empty list
        if not 'stops' in t: t['stops'] = []
        for s in t['stops']:
            a = s['address']
            print('stop: ' + s['id'] + ' @ ' + a['location_id'], end=' ')


            insert_sql = """ INSERT INTO stops
                (id, tours_id, type, status, time_window_begin, time_window_end, rta,
                location_id, company, country, city, zipcode, street, score, latitude, longitude)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s );"""

            update_sql = """ UPDATE stops SET (id, tours_id, type, status, time_window_begin, time_window_end, rta,
                location_id, company, country, city, zipcode, street, score, latitude, longitude) =
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                WHERE id = %s AND tours_id = %s;"""

            values = [
                s['id'],
                t['id'],
                s['type'],
                s['status'],
                s['time_window_begin'],
                s['time_window_end'],
                s['rta'],
                a['location_id'],
                a['company'],
                a['country'],
                a['city'],
                a['zipcode'],
                a['street'],
                a['score'],
                a['latitude'],
                a['longitude']
                ]
            keys = [ s['id'], t['id'] ]
            

            print("s", end='')
            _insert_or_update(conn, insert_sql, update_sql, values, keys)

            print()

def _insert_or_update(conn, insert_sql, update_sql, values, keys):
    def update(conn, update_sql, values, keys):
        print("u", end=' ')
        if update_sql == "":
            #don't bother if we have no update_sql
            return()
        #try updating existing row
        try:
            update_values = values + keys  #this is concatenating two lists so the WHERE clause can be satisfied
            cur = conn.cursor()
            res = cur.execute(update_sql, update_values)
            conn.commit()
        except Exception as e:
            print("error updating: "+str(e))
    
    try:
        cur = conn.cursor()
        res = cur.execute(insert_sql, values)
        conn.commit()
        print("i", end=' ')

        return()
        print("should not get here")
    except Exception as e:
        if "duplicate key" in str(e):
            #update existing row instead
            #extra id/primary key on the end so we can fill the "where" clause parameter
            conn.commit()
            update(conn, update_sql, values, keys)
        else:
            print(e)


def _clean_plate(vid):
    """
    takes a vid string and removes whitespace and dashes, and converts all letters to uppercase
    @param vid: a string representing a vehicle identification
    @return: samve vid, but with spaces and dashes removed and all letters uppercase
    """
    try:
        ascii = ''.join([i if ord(i) < 128 else '' for i in vid])
        name = "".join("".join(ascii.split()).split('-')).upper()
    except:
        name = "NONAME"
    return(name)


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
        
