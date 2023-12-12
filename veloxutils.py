import datetime
import sys
import requests
import json
import os
import time
import pprint
import unicodedata
import pickle
import ast
from types import BooleanType,UnicodeType, IntType, DictType, ListType
from velox_capsule_utils import *


def now(dayonly=False,timeonly=False,format="%m%d%y-%H%M%S"):
    if dayonly:
        return datetime.datetime.now().strftime("%m%d%y")
    if timeonly:
        return datetime.datetime.now().strftime("%H%M%S")
    return datetime.datetime.now().strftime(format)

def get_intersect(results):
    _intersect=results[0]
    for i in range(1,len(results)):
        _intersect = set(_intersect).intersection(results[i])

    return _intersect

def _get_set(db,term):
        category=term[0]
        value=term[1]
        return set(db[category][value])

def get_query(db,all_terms):

    superset=set()
    for terms in all_terms:
        term =ast.literal_eval(terms)

        set1=_get_set(db,term[0])
        for _term in term[1:]:
             nextset=_get_set(db,_term)
             nextset=list(set1.intersection(nextset))
        superset=superset.union(nextset)

    return superset

def get_now(datestr='%Y-%m-%d_%I:%M'):
    return datetime.datetime.now().strftime(datestr)
    #return datetime.datetime.now().strftime('%Y-%m-%d_%I:%M')

def get_field_uniq_value_counts(records,field,numchars=100):
    uniq_created={}
    for _id in records.keys():
        if _id!="timestamp":
            if records[_id].has_key(field):
                _value =records[_id][field]
                _value = _value[:numchars]
                if uniq_created.has_key(_value)==False:
                    uniq_created[_value]=1
                else:
                    uniq_created[_value]=uniq_created[_value]+1
            else:
                sys.stderr.write("error field:" + field + " does not exist for :" + str(_id))
    return uniq_created

def sort_dict_by_value(d,topn=100):
    return sorted(d, key=d.get, reverse=True)[0:topn]

def sort_dict_of_lists_by_count(d,topn=100):
    return sorted(d, key=len(d.get), reverse=True)[0:topn]

def recover(dbname,index=False,pickledir=None):
    t1=datetime.datetime.now()
    result={}
    for _shard in get_pickle_shards(dbname,index,pickledir):
        with open(_shard, 'rb') as f:
            result.update(pickle.load(f))
    print "loaded " + dbname + " in " + str(datetime.datetime.now()-t1) + " secs"
    return result

def persist(dbname,persistfile,index=False,pickledir=None):
    if index==False:
        if pickledir==None:
            picklepath = os.environ["DIRCAPSULEPICKLE"]
        else:
            picklepath = pickledir
    else:
        if pickledir==None:
            picklepath = os.environ["DIRCAPSULEPICKLEINDEX"]
        else:
            picklepath = pickledir

    if isinstance(dbname, dict):
        dbname["timestamp"]=get_now()

    with open(os.path.join(picklepath,persistfile), 'wb') as f:
        pickle.dump(dbname, f, pickle.HIGHEST_PROTOCOL)

def get_pickle_shards(dbname,index=False,pickledir=None):
    if index==False:
        if pickledir==None:
            picklepath = os.environ["DIRCAPSULEPICKLE"]
        else:
            picklepath = pickledir
    else:
        if pickledir==None:
            picklepath = os.environ["DIRCAPSULEPICKLEINDEX"]
        else:
            picklepath = pickledir

    results=[]
    for _file in os.listdir(picklepath):
        if os.path.isfile(os.path.join(picklepath,_file))==True and \
            _file.startswith(dbname) == True and \
            _file[-6:]=="pickle":
                results.append(os.path.join(picklepath,_file))

    return results
 
def removeunicode(s):
    if s==-1:
        return s
    else:
        s_en = s.encode("ascii", "ignore")

    return(s_en.decode())

def remove_non_ascii(s):
    import string

    if isinstance(s,BooleanType) != True and s != None and isinstance(s,IntType) != True \
       and isinstance(s,DictType) != True    and isinstance(s,ListType) != True:
        printable = set(string.printable)
        return ''.join(filter(lambda x: x in string.printable, s))
    else:
        return s

def clean(s):
    return "".join(ch.replace("\"","") for ch in s)

def _get_data_header(url,access_token,tag):
    data = {"filter": { "conditions": [] } }
    httpfunc = getattr(requests,"get")
    #url = url+'?embed=fields&perPage=100&page=1'+str(start_page)
    response = httpfunc(url,headers=_header(access_token),data=json.dumps(data))
    return response.headers[tag]

def get_remaining_rate(access_code):
    return int(_get_data_header("https://api.capsulecrm.com/api/v2/site",access_code,"X-RateLimit-Remaining"))

def _put_data(url,access_token,tag,data):

#curl -i -X POST -H "Authorization: Bearer {token}" \
#-H "Content-Type: application/json" \
#-H "Accept: application/json" \
#-d '{
#  "party": {
#    "type": "organisation",
#    "name": "Acme INC"
#  }
#}' https://api.capsulecrm.com/api/v2/parties


    _url = url+'?embed=fields,tags'

    response = requests.post(_url, headers=_header(access_token), data=json.dumps(data))

    if response.status_code != 200 and  response.status_code != 201:
        print "code:"+str(response.status_code) + " msg:"+response.text + ":" + url

    return response.json()[tag]['id']

def _get_data_simple(url,access_token):

    httpfunc = getattr(requests,"get")
    url = url+'?embed=fields'
    return httpfunc(url,headers=_header(access_token))

def _get_data(url,access_token,tag,data,start_page=1, max_num_pages=10000):

    results=[]
    if data=="nofilter":
        data = {"filter": { "conditions": [] } }
        httpfunc = getattr(requests,"get")
    else:
        httpfunc = getattr(requests,"post")
        url=url+"/filters/results"

    url = url+'?embed=fields&perPage=100&page='+str(start_page)
    response = httpfunc(url,headers=_header(access_token),data=json.dumps(data))

    if response.status_code != 200:
        print "code:"+str(response.status_code) + " msg:"+response.text + ":" + url
        return results

    results = response.json()[tag]
    morepages = response.links.has_key('next')

    if morepages==False:
        return results


    pagenum=1

    while morepages==True:
        url =  response.links['next']['url']
        print url
        trynum=0
        while trynum<5:
            try:
                response = httpfunc(url,headers=_header(access_token),data=json.dumps(data))
                results = results + response.json()[tag]
                trynum=5
            except Exception, e:
                print e.message
                
            trynum=trynum+1
            
        time.sleep(1)
        morepages = response.links.has_key('next')
        if pagenum > max_num_pages:
            return results
        pagenum=pagenum+1
            


    return results

def _header(access_token):
    _headers = {
        'Content-type': 'application/json',
            'Authorization': 'Bearer {}'.format(access_token),
            'Accept': 'application/json',
            'USER-AGENT' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36'
    }

    return _headers

#def _get_system_envs(l):
#    l["dbentries"] = os.environ["DBENTRIES"]
#    l["dbentries_by_partyid"] = os.environ["DBENTRIES_BY_PARTYID"]
#    l["dbopportunities"] = os.environ["DBOPPORTUNITIES"]
#    l["dbopportunities_by_partyid"] = os.environ["DBOPPORTUNITIES_BY_PARTYID"]
#    l["dbperson"] = os.environ["DBPERSON"]
#    l["dborganisation"] = os.environ["DBORGANISATION"]
#    l["dbperson_by_partyid"] = os.environ["DBPERSON_BY_PARTYID"]

def process_args(_args,_must_be_set=[]):
    _l={}
    for cfg in _args[1:]:
        (k,v) = cfg.split("=")
        if v in ["True","true"]: v =True
        if v in ["False","false"]: v =False
        #sys.stderr.write(k+"="+str(v)+"\n")
        _l[k] = v
        if k in _must_be_set:
            _must_be_set.remove(k)

    if len(_must_be_set) > 0:
        print "error:not set " + ",".join(_must_be_set)
        exit()

    if _l.has_key("filter") == False:
        #sys.stderr.write("filtler arg defaulted to nofilter")
        _l["data_filter"] = "nofilter"
    else:
        if _l["filter"]=="organisation_filter":
            _l["data_filter"] = organisation_filter
            _l["sub_entity"]="organisation"
        elif _l["filter"]=="person_filter":
            _l["data_filter"] = person_filter
            _l["sub_entity"]="person"

    if _l.has_key("entity") == False:
        if "entity" in _must_be_set:
             #sys.stderr.write("mandatory arg \"entity\" missing\n")
             exit()

    if _l.has_key("entity_key") == False:
        if "entity_key" in _must_be_set:
             #sys.stderr.write("mandatory arg \"entity_key\" missing\n")
             exit()

    if _l.has_key("entity_key") == True:
        _l["entity_key"] = _l["entity_key"].replace("__"," ")


    if _l.has_key("index_dict"):
        _id = ast.literal_eval(_l["index_dict"])
        _l["entity"] = _id["entity"].replace("$$"," ")
        _l["entity_key"] = _id["entity_key"].replace("__"," ")
        if _id.has_key("subentity_key") == True:
            if  _id["subentity_key"] != None:
                _l["subentity_key"] = _id["subentity_key"].replace("__"," ")

    if _l.has_key("start_page") == False:
        #sys.stderr.write("start_page arg defaulted to 1\n")
        _l["start_page"] = 1
    else:
        _l["start_page"] = int(_l["start_page"])

    if _l.has_key("topn") == False:
        #sys.stderr.write("topn arg defaulted to -1\n")
        _l["topn"] = -1
    else:
        _l["topn"] = int(_l["topn"])


    if _l.has_key("multipage") == False:
        #sys.stderr.write("multipage arg defaulted to False\n")
        _l["multipage"] = None

    if _l.has_key("outputfields") == False:
        #sys.stderr.write("outputfields arg defaulted to None\n")
        _l["outputfields"] = None
    elif _l["outputfields"] == "model":
        _l["outputfields"] = "model"
    else:
        _l["outputfields"] = ast.literal_eval(_l["outputfields"])

    # output file
    if _l.has_key("dircapsulepickle") == False:
        #sys.stderr.write("picklefile arg defaulted to \"./pickle\n\"")
        _l["dircapsulepickle"] = "./pickle"

    # output file
    if _l.has_key("outputfile") == False:
        #sys.stderr.write("outputfile arg defaulted to \"/tmp/output.csv\n\"")
        _l["outputfile"] = "/tmp/output.csv"
    else:
        if os.path.isdir(os.path.dirname(_l["outputfile"])) == False:
             _l["outputfile"] = "/tmp/output.csv"

    #else:
    #    dir=os.environ["DIRCAPSULECSV"]
    #    _l["outputfile"] = os.path.join(dir, _l["outputfile"])


    # mode (persist|recover|normal)
    if _l.has_key("mode") == False:
        #sys.stderr.write("mode arg defaulted to \"normal\"\n")
        _l["mode"]="normal"

    # persist file
    if _l.has_key("persistfile") == False:
        #sys.stderr.write("persistfile arg defaulted to \"output.pickle\"\n")
        _l["persistfile"]="output.pickle"

    # input file
    if _l.has_key("inputfile") == False:
        #sys.stderr.write("inputfile arg defaulted to \"input.csv\"\n")
        _l["inputfile"]=None

    # this id
    if _l.has_key("thisid") == False:
        #sys.stderr.write("thisid is not enabled\n")
        _l["thisid"]=None

    if _l.has_key("query_terms") == True:
        _tmp = _l["query_terms"].replace("$$"," ")
        _l["query_terms"] = ast.literal_eval(_tmp)

    _l["query"]=[]
    for i in range(0,4):
        qname="query"+str(i)
        if _l.has_key(qname):
            _l["query"].append(_l[qname])

    return _l

if __name__ == "__main__":
    #entity = recover("person")

    #print get_core_field(entity,entity.keys()[0],"firstName")
    #print get_custom_field(entity,entity.keys()[0],"Job Type")

    person = recover("person")
    index = recover("person_lastname",True)
    pattern = 'Mosten*'
        
    for _match in matchkey(index, pattern):
        for _entity in index[_match]:
            print ",".join(get_multi_field(person,_entity,["firstName","lastName","jobTitle","Seniority","id","LinkedInURL","phoneNumber","emailAddresses"]))

