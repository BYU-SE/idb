#
# Functions for generating static html pages for incidents (the detail()) and lists of incidents (the index function). I'm just using python format strings for now, eventually using a templating library may make more sense. I'm just reluctant to add a dependency, atm.

import re
import urllib.parse
import db

def categorized_index(categorized_incidents, title="Incidents"):
  #
  # Create an index html page listing all the given incidents, grouped by category (eg, by year or by organization)
  
  rows = []
  for category, incidents in categorized_incidents:
    rows.append(category_row_html.format_map({
      'category':category,
      'category_url':_url(category)
    }))
    rows.append(header_row_html)
    
    for i in incidents:
      rows.append(index_row_html.format_map(_properties_map(i)))
  
  content = '\n'.join(['<table>'] + rows + ['</table>'])
  
  return page_html.format_map({
    'title':title,
    'content':content,
    'css':css})
    
def index(incidents, title="Incident database"):
  #
  # Create an index html page listing the given incidents and with the given page title.
  
  incidents_html = [index_row_html.format_map(_properties_map(i)) 
    for i in incidents]
  
  content = '\n'.join(['<table>'] + [header_row_html] + incidents_html + ['</table>'])
  
  return page_html.format_map({
    'title':title,
    'content':content,
    'css':css})

def detail(incident):
  #
  # Create an html page listing the given incidents properties.
  
  properties = _properties_map(incident)
  incident_html = detail_html.format_map(properties)
  
  return page_html.format_map({
    'title':incident.title,
    'content':incident_html,
    'css':css})

#
# Private helper functions
#

def _date_str(ts):
  if type(ts) == int:
    return str(ts)
  else:
    parts = ts.split(' ')
    return parts[0]

def _url(s):
  if type(s) == str:
    return urllib.parse.quote_plus(s.strip())
  else:
    return s

def _remove_annotations(props):
  def sub(value):
    if type(value) == str:
      return re.sub(r'\s*\[\d+(,\s*\d+)*\]\s*$', '', value)
    return value
    
  return {k:sub(v) for (k,v) in props.items()}

def _properties_map(incident):
  #
  # Return a properties map for the given index, suitable for python string formats. The map will include annotations (with the name of the annotation as the key and the description as the value).
  
  props = {}
  props.update(incident.properties)
  props['year'] = incident.year()
  props['date'] = _date_str(incident.start_ts)
  
  if props['author']:
    props['author'] = 'by ' + props['author']
  else:
    props['author'] = ''
    
  link = '<a href="../technologies.html#%s">%s</a>'
  props['tech_links'] = ', '.join([
    link % (_url(tech), tech.strip()) 
    for tech in incident.technologies.split(',')
  ])
  
  props['organization_url'] = _url(incident.organization)
  
  return _remove_annotations(props)

#
# HTML templates. As mentioned above, these are simply python style string templates, expecting a dict.

css = '''
body {
  font-family: Helvetica, sans-serif;
}
a, a:visited {
  color:#03e;
}
table {
  border-collapse: collapse;
}
td {
  border: 1px solid #ddd;
  vertical-align:top;
  text-align:left;
  padding:10px;
  line-height:150%;
}
blockquote {
  font-size:125%;
  padding:0px 20px;
  margin:20px 0px;
  border-left:1px solid #ddd;
}
tr.category td {
  font-weight:bold;
  background-color:#ffd;
}
tr.head {
  font-weight:bold;
}
p.footer {
  font-size:75%;
}
'''

page_html = '''
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>{title}</title>
    <style>
      {css}
    </style>
  </head>
  <body>
  <h1>
    {title}
  </h1>
  {content}
  </body>
</html>
'''

detail_html = '''
<blockquote>
  &ldquo;{quote}&rdquo;
</blockquote>

<table>
  <tr>
    <td>
      Incident
    </td>
    <td>
      #{id} at 
      <a href="../organizations.html#{organization_url}">{organization}</a> on 
      <a href="../years.html#{year}">{date}</a> {author}
    </td>
  </tr>
  <tr>
    <td>
      Full report
    </td>
    <td>
      <a href="{url}">{url}</a>
    </td>
  </tr>

  <tr>
    <td>
      How it happened
    </td>
    <td>
      {how_it_happened}
    </td>
  </tr>
  <tr>
    <td>
      Architecture
    </td>
    <td>
      {architecture}
    </td>
  </tr>
  <tr>
    <td>
      Technologies
    </td>
    <td>
      {tech_links}
    </td>
  </tr>
  <tr>
    <td>
      Root cause
    </td>
    <td>
      {root_cause}
    </td>
  </tr>
  <tr>
    <td>
      Failure
    </td>
    <td>
      {failure}
    </td>
  </tr>
  <tr>
    <td>
      Impact
    </td>
    <td>
      {impact}
    </td>
  </tr>
  <tr>
    <td>
      Mitigation
    </td>
    <td>
      {mitigation}
    </td>
  </tr>
</table>
'''

header_row_html = '''
<tr class="head">
  <td>#</td>
  <td>Org</td>
  <td>Year</td>
  <td>Report</td>
</tr>
'''

category_row_html = '''
  <tr class="category">
    <td colspan="5">
      {category}<a id="{category_url}">&nbsp;</a>
    </td>
  </tr>
'''

index_row_html = '''
<tr>
  <td>
    {id}
  </td>
  <td>
    <a href="organizations.html#{organization_url}">{organization}</a>
  </td>
  <td>
    <a href="years.html#{year}">{year}</a>
  </td>
  <td>
  <a href="incidents/{id}.html">{title}</a>:
    &ldquo;{quote}&rdquo;
  </td>
</tr>
'''

