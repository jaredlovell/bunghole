#!/usr/bin/env python3

import sys
import xmltodict
import psycopg2
import json



inputfile = sys.argv[1]


dsn = 'dbname=ght user=pgsql password=xyz host=localhost'

def main():
    conn = _db_new_connection(dsn)
    data = xmltodict.parse(open(inputfile, mode='r', encoding="utf-8").read(),
                                force_list={'status': True,
                                           }
                                )

    #there is nothing in this file not inside <vehicle_samples><samples>
    s = data['vehicle_samples']['samples']

    for sample_type in ['coupling', 'ignition', 'motion', 'status']:
        count = 0
        trailer_count = 0
        tractor_count = 0 

        
        vehicle_samples = s[sample_type]
        #[1]['vehicle']
        print('sample type: ' +  sample_type)
        #print(json.dumps(vehicle_samples, indent=4, sort_keys=True))
        #exit()

            
        #vehicle could be a trailer or a tractor, and obviously the way to indicate
        #that is to enclose every other thing in <trailer> or <tractor>

        for sample in vehicle_samples:
            count += 1

            sample = sample['vehicle'] #dumdumdumdumdum
            if 'tractor' in sample:
                #print("sample_type: " + sample_type + ",tractor")
                tractor_sample = sample['tractor']
                tractor_count += 1

                if 'ebs' in tractor_sample:
                    print(sample_type + " tractor")
                    print(json.dumps(tractor_sample['ebs'], indent=4, sort_keys=True))

                    
            elif 'trailer' in sample:
                #print("sample_type: " + sample_type + ",trailer")
                trailer_sample = sample['trailer']
                trailer_count += 1

                if 'ebs' in trailer_sample:
                    print(sample_type + " trailer")
                    print(json.dumps(trailer_sample['ebs'], indent=4, sort_keys=True))


            else:
                print("what is this derpy derp sample?: ")
                print(json.dumps(sample, indent=4, sort_keys=True))


        print(str(tractor_count) + " tractors")
        print(str(trailer_count) + " trailers")

            #pretty much flatten the rest of this horror.
            #print(vehicle_base['id'])

    exit()




def _insert_or_update(conn, insert_sql, update_sql, values):
        try:
            cur = conn.cursor()
            res = cur.execute(insert_sql, values)
            conn.commit()
            return()
            print("should not get here")
        except psycopg2.IntegrityError as e:
            #update existing row instead
            #extra id/primary key on the end so we can fill the "where" clause parameter
            print("duplicate, no problem")
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
        
