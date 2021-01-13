#
# Functions for dropping, creating, and quering a database of incidents. Note that we are allowing all sqlite3 exceptions to propagate to clients, at least for now.

import sqlite3
import entities

#
# Low level db helper functions
#

__connection = None # share connection across queries

def connection(filename='idb.db'):
  #
  # The filename is only used the first time this function is called. After that the db file name is set.
  
  global __connection
  if __connection == None:
    __connection = sqlite3.connect(filename)
    __connection.row_factory = sqlite3.Row # makes row objects ~dicts
      
  return __connection
  
def cursor():
  return connection().cursor()

def get(stmt, params=()):
  results = get_all(stmt, params)
  
  if len(results) != 1: 
    return None
  return results[0]
    
def get_all(stmt, params=()):
  if not type(params) == tuple:
    params = (params,)
    
  c = cursor().execute(stmt, params)
  return c.fetchall()
  
def _id(obj):
  #
  # This is useful in functions that want to accept either an id or an object that has an id and behave the same regardless. For example and incident object or an incident_id.
  
  if type(obj) in [str, int]:
    return obj
    
  return obj.id

#
# Creating and loading the incident database
#

def drop_database():
  c = cursor()
  c.execute(drop_incidents_table_stmt)
  c.execute(drop_blocks_table_stmt)
  
def create_database():
  c = cursor()
  c.execute(create_incidents_table_stmt)
  c.execute(create_blocks_table_stmt)

def insert_incident(incident):
  p = incident.properties
  connection().execute(insert_incident_stmt, (
    incident.id,
    incident.title, 
    incident.organization,
    incident.product, 
    incident.start_ts,
    incident.end_ts, 
    incident.author, 
    incident.url,
    incident.technologies, 
    incident.quote,
    incident.summary,
    incident.architecture,
    incident.root_cause,
    incident.failure,
    incident.impact,
    incident.how_it_happened,
    incident.mitigation
  ))

def insert_blocks(incident, blocks):
  blocks = [(_id(incident), b.position, b.section_header, b.content)
    for b in blocks]
  
  res = cursor().executemany(insert_block_stmt, blocks)

#
# Functions for reading dimension data from the database.

def years():
  #
  # A list of all years (as ints) referenced in the incidents table (specifically the start_ts column)
  
  sql = "select distinct substr(start_ts, 1,4) as year from incidents order by year"
  return [int(row['year']) for row in get_all(sql)]
  
def organizations():
  #
  # A list of distinct organization names (as strings) referenced in the incidents table.
  
  sql = "select distinct organization from incidents order by organization"
  return[row['organization'] for row in get_all(sql)]

def technologies(all_incidents=None):
  #
  # A set of all technologies found in the database (ie, the technologies column from the incidents table)
  
  if not all_incidents:
    all_incidents = incidents()
  
  technologies = set()
  for incident in all_incidents:
    technologies.update(incident.tech())
  
  return sorted([t for t in technologies if t and t.strip() != ''])

#
# Functions for reading objects from the database, all returning either an instance or a list of instances from the entities modules (Incident, Annotation or Block)

def incidents():
  #
  # All incidents in the incident table of the database. The dataset is small enough that reading them all into memory is reasonable, so little in database filtering is used, atm.
  
  sql = "select * from incidents order by id"
  return [entities.Incident(row) for row in get_all(sql)]

def incident(id):
  #
  # The incident from the database with the given id.

  return entities.Incident(get("select * from incidents where id=?", id))

def block(id=None, incident=None, position=None):
  #
  # Get the block with the given id, or alternatively an incident (or incident id) and position pair, which pair should also uniquely identify one block from the database.
    
  if id is not None:
    return entities.Block(get("select * from blocks where id=?", id))
    
  elif incident is not None and position is not None:
    sql = "select * from blocks where incident_id=? and position=?"
    return entities.Block(get(sql, (_id(incident), position)))
    
  else:
    raise TypeError("block() needs either and id or a incident & position")

def blocks(incident):
  #
  # Get all blocks associated with an incident, sorted by position (lowest to highest)
  
  sql = 'select * from blocks where incident_id=? order by position'
  return [entities.Block(row) for row in get_all(sql, _id(incident))]

#
# SQL statements used by the above creation and insertion functions. The "create table" statements below define the schema for the database.

drop_incidents_table_stmt = """
drop table if exists incidents;
"""

create_incidents_table_stmt = """
create table if not exists incidents (
  id integer primary key,
  title text,
  organization text,
  product text,
  start_ts timestamp,
  end_ts timestamp,
  author text,
  url text,
  technologies text,
  quote text,
  summary text,
  architecture text,
  root_cause text,
  failure text,
  impact text,
  how_it_happened text,
  mitigation text
);
"""

drop_blocks_table_stmt = """
drop table if exists blocks;
"""

create_blocks_table_stmt = """
create table if not exists blocks (
  id integer primary key autoincrement,
  incident_id integer,
  position integer,
  section_header text,
  content text,
  foreign key (incident_id) references incidents (id)
);
"""

insert_incident_stmt = '''
insert into incidents (
  id,
  title,
  organization,
  product,
  start_ts,
  end_ts,
  author,
  url,
  technologies,
  quote,
  summary,
  architecture,
  root_cause,
  failure,
  impact,
  how_it_happened,
  mitigation)
  values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
'''

insert_block_stmt = '''
insert into blocks (
  incident_id,
  position,
  section_header,
  content)
  values (?,?,?,?)
'''
