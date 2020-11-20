#
# Support for parsing incident data files, which come in two varieties: (1) incident reports in Markdown format, and (2) incident metadata in YAML format. The main interface is:
#
#   parse.blocks(markdown_filename) # -> list of entities.Block objects
#   parse.incident(yaml_filename)   # -> entities.Incident object

import sys
import re
import yaml
import textwrap
import entities

def incident(yaml_filename):
  #
  # Parse the YAML file passed and return an entities.Incident object
  
  with open(yaml_filename) as file:
    obj = yaml.load(file, Loader=yaml.FullLoader)
    incident = entities.Incident(obj['properties'])
    incident.annotations = [entities.Annotation(a) 
      for a in obj['structured abstract']]
    return incident

def blocks(md_filename):
  #
  # Parse the Markdown file passed as an argument and return a list of entities.Block objects
  
  with open(md_filename) as file:
    blocks = []
    header = None
    
    for line in file.read().splitlines():
      line = line.rstrip()
      if line:
        if line.startswith('#'):
          header = line
        
        # check if we are in a code block, so we can just append to the previous block, rather than create a new block
        if _in_code_block(blocks, line):
          blocks[-1].content += "\n" + line
        
        else:
          blocks.append(entities.Block({
            'position':len(blocks), 'section_header':header, 'content':line}))
          
  return blocks
  
#
# helper functions
#

def _in_code_block(blocks, current):
  #
  # True if the most recently parsed block (current) is part of a large block of code (as defined by Markdown), False otherwise
  
  return len(blocks) > 0 and \
    _is_code_block(current) and \
    _is_code_block(blocks[-1].content)

def _is_code_block(block):
  #
  # True if the block is a Markdown code block (ie, indented but not part of a list, etc), False otherwise
  
  return re.match(r'\s', block) != None and \
    not re.match(r'[*>]', block.strip())
  
#
# Main
#
# When this module is called from the command line, it prints out the contents of a Markdown file with block numbers attached to each block, suitable for passing to the more or less commands

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print("USAGE: ")
    print("python src/parse.py <Markdown file name>")
    sys.exit(1)
  
  for filename in sys.argv[1:]:
    report_id = filename.split('/')[-1].split('.')[0]
    
    all_blocks = blocks(filename)
    print("%d blocks" % len(all_blocks))
    
    for index in range(len(all_blocks)):
      block = all_blocks[index]
      
      if block.content == block.section_header:
        print("%s\n" % block.content)
        
      else:
        content = block.content + (" [%d]" % index)
        # print("[%s, %d]" % (filename,index))
        if re.search(r'\n', content):
          # if this is a code block, then we just print it rather than use the text wrap function
          print(content)
        else:
          print(textwrap.fill(content,width=70,initial_indent='  ',
            subsequent_indent='  '))
            
        print()
