import fnmatch

field_types=["core","custom","date","address"]
entity_types=["person","organisation","opportunities","entries"]

person_filter = {"filter": { "conditions": [ {"field":"type", "operator":"is", "value":"person"} ] } }
organisation_filter = {"filter": { "conditions": [ {"field":"type", "operator":"is", "value":"organisation"} ] } }

# person
person_core_fields=["Contact Owner","firstName","id","jobTitle","lastName","organisation","owner","phoneNumbers","team","title"]
person_custom_fields=["Job Type","Department","Sub Department","Seniority","LinkedInURL","Notes"]
person_date_fields=["lastContactedAt","createdAt","updatedAt"]
person_address_fields=["emailAddresses"]
person_dict_fields=[]

person_fields_empty_dict = [{"id":255727892,"definition":{"id":680167,"name":"Seniority"},"tagId":None,"value":None}, 
                             {"id":255727891,"definition":{"id":680168,"name":"Department"},"tagId":None,"value":None}, 
                             {"id":255727888,"definition":{"id":749750,"name":"Relationship"},"tagId":None,"value":None}, 
                             {"id":255727889,"definition":{"id":750541,"name":"Contact Owner"},"tagId":None,"value":None}, 
                             {"id":255727885,"definition":{"id":776043,"name":"LinkedInURL"},"tagId":None,"value":None}, 
                             {"id":255727890,"definition":{"id":784455,"name":"Sub Department"},"tagId":None,"value":None}, 
                             {"id":255727886,"definition":{"id":784456,"name":"Job Type"},"tagId":None,"value":None},
                             {"id":255727887,"definition":{"id":794404,"name":"Notes"},"tagId":None,"value":None}]

person_empty_dict = {'phoneNumbers': [],'fields': person_fields_empty_dict, 'firstName': "", 'title': "", 'jobTitle': "", 
                     'organisation':None , 'team': None, 'Contact Owner': "", 'updatedAt': "", 'lastName': "", 
                     'owner':"", 'emailAddresses': [], 'id': 0, 'createdAt': "", 'lastContactedAt': ""}




{"Job Type":None,"Department":None,"Sub Department":None,"Seniority":None,"LinkedInURL":None,"Notes":None}

# organisation
organisation_core_fields=["name","phoneNumbers","team","owner","id"]
organisation_custom_fields=["Company Type","Company Size","Head Region","Notes"]
organisation_date_fields=["createdAt","updatedAt"]
organisation_dict_fields=[]
#organisation_address_fields=[]
organisation_address_fields=["emailAddresses"]

organisation_update_fields ={"person":"organisation","opportunities":"party","entries":"party"}

organisation_fields_empty_dict = [{"id":260712826,"definition":{"id":680169,"name":"Company Type"},"tagId":None,"value":None}, 
                                            {"id":260712827,"definition":{"id":680171,"name":"Company Size"},"tagId":None,"value":None}, 
                                            {"id":260712828,"definition":{"id":680288,"name":"Head Region"},"tagId":None,"value":None}, 
                                            {"id":260712829,"definition":{"id":794404,"name":"Notes"},"tagId":None,"value":None}]

organisation_empty_dict= {'phoneNumbers': [], 'name': "", 'fields':  organisation_fields_empty_dict,'updatedAt':"", 'team': None, 
                          'owner': None, 'emailAddresses': [], 'id': 0, 'createdAt': ""}

# opportunities
opportunities_core_fields=["name","description","value","owner","durationBasis","milestone","duration","party","lostReason","id"]
opportunities_custom_fields=["Product","Rev Model","Lead Source","Campaign"]
opportunities_date_fields=["expectedCloseOn","lastContactedAt","lastStageChangedAt","closedOn","createdAt","updatedAt"] 
opportunities_address_fields=[]
opportunities_dict_fields=["milestone"]

#entries
entries_core_fields=["id","content","subject","creator","activityType"]
entries_custom_fields=[]
entries_address_fields=[]
entries_date_fields=["entryAt","createdAt","updatedOn"]
entries_dict_fields=["creator","activityType","party"]

#person_join
join_core_fields=list(set(organisation_core_fields)-set(["owner","id","phoneNumbers","team"]))
join_core_fields=join_core_fields+person_core_fields+["Email Flag","orgId"]

join_custom_fields=list(set(organisation_custom_fields)-set(["Notes"]))
join_custom_fields=join_custom_fields+person_custom_fields

join_address_fields=person_address_fields
join_date_fields=person_date_fields + ["orgCreatedAt","orgUpdatedAt"]
join_dict_fields=person_dict_fields+organisation_dict_fields


_list_name = "all_address_fields"
locals()[_list_name] =[]
for _entity_type in entity_types:
    locals()[_list_name] = locals()[_list_name] + locals()[_entity_type+"_address_fields"]

for _field_type in field_types + ["dict"]:
    _list_name = "all_"+_field_type+"_fields"
    locals()[_list_name] =[]
    for _entity_type in entity_types:
        locals()[_list_name] = locals()[_list_name] + locals()[_entity_type+"_"+_field_type+"_fields"]

def matchkey(index,pattern):
    return  fnmatch.filter(index.keys(), pattern)

def has_a(index,parent_id):
    if index.has_key(parent_id)==True:
        if len(index[parent_id]) > 0:
            return index[parent_id]
    return []

def get_multi_field(entities,entity_id,entity_fields):
    result=[]
    for _entity_field in entity_fields:
        try:
            result.append(get_field(entities,entity_id,_entity_field))
        except Exception, e:
            result.append(e.message)
    return result

def get_multi_field_raw(entities,entity_id,entity_fields,header=False):
    # leave fields in original format
    result=[]
    for _entity_field in entity_fields:
        try:
            result.append(get_field_raw(entities,entity_id,_entity_field))
        except Exception, e:
            result.append(e.message)     
            
    if header==False:
        return result
    else:
        result_dict={}
        for i in range(0,len(entity_fields)):
            field = entity_fields[i]
            value = result[i]
            
            result_dict[field]=value
        return result_dict
    
def get_field_raw(entities,entity_id,entity_field):
    # leave fields in original format
    if entities[entity_id].has_key(entity_field)==True:
        return entities[entity_id][entity_field]
    else:
        return -1
    
def get_field(entities,entity_id,entity_field):

    if globals().has_key("get_"+entity_field+"_field"):
        return globals()["get_"+entity_field+"_field"](entities,entity_id,entity_field)

    for field_type in field_types:
        if entity_field in globals()["all_"+field_type+"_fields"]:
            _field_value = globals()["get_"+field_type+"_field"](entities,entity_id,entity_field)
            if _field_value == None:
                _field_value=""
            return _field_value
    return -1


def get_id_field(entities,entity_id,entity_field):
    return str(entities[entity_id][entity_field])

def get_content_field(entities,entity_id,entity_field):
    _content =  entities[entity_id][entity_field]
    if _content != None:
        return _content.replace("\n","$$")
    else:
        return "None"

def get_phoneNumbers_field(entities,entity_id,entity_field):
    _result=""
    for _number in entities[entity_id][entity_field]:
        if _result == "":
            _result = _number["number"]
        else:
            _result = _result + " " + _number["number"]

    return _result

def get_address_field(entities,entity_id,entity_field):
    #if entity_field in globals()["all_address_fields"]:
        _result=""
        for _address in entities[entity_id][entity_field]:
            if _result == "":
                _result = _address["address"]
            else:
                _result = _result + " " + _address["address"]

        return _result

def get_core_field(entities,entity_id,entity_field):

    for field_type in field_types:
        if entity_field in globals()["all_dict_fields"]:
            if entities[entity_id][entity_field] != None and entities[entity_id][entity_field].has_key("name"):
                return entities[entity_id][entity_field]["name"]
            else:
                return "no name field"
    try:
        return entities[entity_id][entity_field]
    except:
        return "field not exist"

def get_date_field(entities,entity_id,entity_field):
    return entities[entity_id][entity_field][:10]

def get_custom_field(entities,entity_id,entity_field):
    fields=entities[entity_id]["fields"]
    for _field in fields:
        if _field["definition"]["name"].replace(" ","_").lower() == entity_field.replace(" ","_").lower():
            return _field["value"]
    return -1

def parse_custom_fields(entity):
    _pcf = {}
    if isinstance(entity["fields"],int)==True:
        # this is the empty row case where fields is set to 0
        _pcf[_field]=entity["fields"]
    else:
        for i in range(0,len(entity["fields"])):
            _field = entity["fields"][i]["definition"]["name"]
            _value = entity["fields"][i]["value"]
            _pcf[_field]=_value

    return _pcf

def iter_entity_fields(field_type,entity):
    return(iter(globals()[entity+"_"+field_type+"_fields"]))

def get_entity_fields(entity):
    return(globals()[entity+"_address_fields"]+globals()[entity+"_core_fields"]+globals()[entity+"_date_fields"]+globals()[entity+"_custom_fields"])

def get_entity_fields_raw(entity):
    # used to get all the fields in original format
    return(globals()[entity+"_address_fields"]+globals()[entity+"_core_fields"]+globals()[entity+"_date_fields"]+["fields"])
