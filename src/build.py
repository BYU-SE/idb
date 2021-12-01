#
# Script for building a database of incidents (saved to idb.db) and a static web site (in the html directory) summarizing those incidents. Note that (1) incident reports are expected to be in Markdown format, and (2) incident metadata is expected to be in YAML format. We assume that the data files are named based on their incident ID. So incident 5 should have two associated data files: 5.md and 5.yaml.
#
# Usage:
# $ python src/build.py [list of yaml files]

import sys
import os
import parse
import db
import html 

# 
# First we build the database from the files supplied on the command line, or of no files are specified then all the files in the './data/' directory are used

if len(sys.argv) > 1: # load database from specified files
  datafilenames = sys.argv[1:]
  
else: # load database from 'data/' directory
  datafilenames = [os.path.join('data', f) for f in os.listdir('data')]

# WARNING: everytime this script is run the database is dropped and recreated

db.drop_database()
db.create_database()

for filename in datafilenames: 
  path,filetype = filename.split('.')
  
  if filetype == 'yaml': 
    # insert incidents
    incident = parse.incident(filename)
    db.insert_incident(incident)
    
    # insert blocks (ie, paragraphs) for that incident
    blocks = parse.blocks(path + '.' + 'md')
    db.insert_blocks(incident, blocks)

db.connection().commit()

#
# Next we query the just built database to create a static website in the 'html' directory (creating that directory in the process, if needed)

html_dir = 'docs'
incidents_dir = html_dir + '/incidents'

for d in [html_dir, incidents_dir]:
  if not os.path.exists(d):
    os.makedirs(d)
    
incidents = db.incidents()

#
# Create an index.html file listing all incidents

with open(html_dir + '/index.html', 'w', encoding='utf8') as file:
  file.write(html.index(incidents))

#
# Create an html index file listing all incidents by the year the incident happened in

incidents_by_year = []
for year in db.years():
  incidents_by_year.append((year,
    [i for i in incidents if i.year()==year]))
    
with open(html_dir + '/years.html', 'w') as file:
  file.write(html.categorized_index(incidents_by_year, "Years"))

#
# Create an html index file listing all incidents by the organization that had the incident

incidents_by_org = []
for org in db.organizations():
  incidents_by_org.append((org, 
    [i for i in incidents if i.organization == org]))
    
with open(html_dir + '/organizations.html', 'w') as file:
  file.write(html.categorized_index(incidents_by_org, "Organizations"))    

#
# Create an html index file, listing all incidents by technologies mentioned in the incident repoert

incidents_by_tech = []
for tech in db.technologies(incidents):
  incidents_by_tech.append((tech, 
    [i for i in incidents if tech in i.tech()]))
    
with open(html_dir + '/technologies.html', 'w') as file:
  file.write(html.categorized_index(incidents_by_tech, "Technologies"))

#
# Create an html file for 

# with open(html.html_dir + '/lists.html', 'w') as file:
#   file.write(html.lists(db.organizations(), db.years(), db.technologies()))

#
# Create on html file for each incident (1.html, 2.html, etc)

for i in incidents:
  with open('%s/%d.html' % (incidents_dir, i.id), 'w') as file:
    file.write(html.detail(i))

print('Build complete')
print('- Run "sqlite3 idb.db" to query the database')
print('- Open "docs/index.html" to browse incidents')
