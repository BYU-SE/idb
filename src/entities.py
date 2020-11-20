#
# The core entity types for IDB, covering Incidents, Annotations and Blocks (with more coming likely). Each constructor takes a properties map that can be either a row from a database or a dict.

from collections.abc import Iterable
from datetime import datetime

class Incident:
  #
  # Incident objects are a collection of attributes about a particular incident report.
  
  def __init__(self, properties):
    if type(properties) != dict:
      properties = dict(properties)
      
    self.id = properties['id']
    self.title = properties['title']
    self.organization = properties['organization']
    self.product = properties['product'] or properties['organization']
    self.start_ts = properties['start_ts']
    self.end_ts = properties['end_ts']
    self.author = properties['author']
    self.url = properties['url']
    self.technologies = properties['technologies'] or ''
    self.quote = properties.get('quote')
    
    self.properties = properties
    self.annotations = []

  def year(self):
    if type(self.start_ts) == int:
      return self.start_ts
    else:
      return self.date().year

  def date(self):
    return datetime.strptime(self.start_ts.split(' ')[0], '%Y/%m/%d')

  def annotation(self, name):
    for a in self.annotations:
      if a.name == name:
        return a
        
  def tech(self):
    return [t.strip() for t in self.technologies.split(',')]
  
  def __str__(self):
    return "%d %s" % (self.id, self.title)

class Annotation:
  # 
  # An annotation is a way to identify and paraphrase particular aspects of incident reports. Example aspects might be "root cause", "how it happened" or "lesson learned".
  
  def __init__(self, properties):
    if type(properties) != dict:
      properties = dict(properties)
    
    self.id = properties.get('id')
    self.name = properties['name']
    self.description = properties['description']
    
    self.blocks = properties.get('blocks') or []
    
    if not isinstance(self.blocks, Iterable):
      self.blocks = [self.blocks]
    
  def __str__(self):
    blocks = ",".join([str(b) for b in self.blocks])
    return "[%s] %s: %s" % (blocks, self.name, self.description)

class Block:
  #
  # A block is a paragraph of text in an incident report, and can be associated with (an informal notion of) a section in a report, captured by the section header property.
  
  def __init__(self, properties):
    if type(properties) != dict:
      properties = dict(properties)
      
    self.id = properties.get('id')
    self.incident_id = properties.get('incident_id')
    self.position = properties['position']
    self.section_header = properties['section_header']
    self.content = properties['content']
  
  def __str__(self):
    return self.content
  
  def __repr__(self):
    return "[%d %s] %s" % (self.position, self.section_header, self.content)
