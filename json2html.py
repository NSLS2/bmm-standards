#!/usr/bin/env python
from openpyxl import load_workbook
import json, datetime, pprint, re
from mendeleev import element

pp = pprint.PrettyPrinter(indent=4)


class Standards():
    '''A class for managing a JSON file of items in the BMM standards
    collection and writing a useful HTML file summarizing the collection.

    Example
    =======

    from json2html import Standards
    m = Standards()
    m.html       = 'test.html'
    m.singlepage = False
    m.make_html()         # write data to an html file

    '''
    def __init__(self):
        self.spreadsheet = 'Standards.xlsx'
        self.datadict = {}
        self.json = 'standards.json'
        self.html = 'test.html'
        self.singlepage = False
        self.cssfile = 'standards.css'
        

    def read_spreadsheet(self, spreadsheet=None):
        '''Read spreadsheet data, storing its contents in a dict '''
        if spreadsheet is None:
            spreadsheet = self.spreadsheet
        if spreadsheet is None:
            print('You need to specify the path to a spreadsheet')
            return()
        print(f'Reading data from {spreadsheet}')
        workbook = load_workbook(spreadsheet, read_only=True);
        worksheet = workbook.active
        self.datadict = {}
        for row in worksheet.rows:
            this = []
            i = 3
            while row[i].value is not None:
                td = {'material' : row[i].value,
                      'name' : '',
                      'location' : row[2].value,}
                this.append(td)
                i += 1
            self.datadict[row[2].value] = this
        #pp.pprint(self.datadict)

            
    def to_json(self):
        '''Save spreadsheet data to a JSON file''' 
        with open(self.json, 'w') as fp:
            json.dump(self.datadict, fp, indent=4)
        print(f'Wrote JSON to {self.json}')

        
    def make_html(self):
        '''Write the contents of the JSON file to a pretty html file'''
        with open('standards.json', 'r') as myfile:
            data=json.loads(myfile.read())
        
            
        ##########
        # header #
        ##########
        if self.singlepage is True:
            with open(self.cssfile) as x: css = x.read()
            page = f'''
<html>
  <head>
    <title>XAFS Standards at BMM</title>
    <style>
{css}
    </style>
  </head>

  <body>
  <h1>XAFS Standards at BMM</h1>'''
        else:
            page = f'''
<html>
  <head>
    <title>XAFS Standards at BMM</title>
    <link rel="stylesheet" href="{self.cssfile}" />
  </head>

  <body>
  <h1>XAFS Standards at BMM</h1>'''

        for z in range(20, 95):
            el = element(z)
            if el.symbol not in data:
                continue
            ## h1 for this switch + grid wrapper div
            page = page + f'\n\n    <h2>{el.symbol}&nbsp;&nbsp;&nbsp;({z})&nbsp;&nbsp;&nbsp;{el.name}</h2>\n      <div class="wrapper">\n'
            
            for i, this in enumerate(data[el.symbol]):
                location = ''
                if this['location'] != el.symbol:
                    location = 'location: '+this['location']
                if this['refwheel'] is True:
                    location = 'on reference wheel'
                if 'lanthanidewheel' in this and this['lanthanidewheel'] is True:
                    location = 'on lanthanide wheel'
            ## generate a div for the table explaining each port
                if i == 0:
                    text = '        <div class="box box1">' + self.oneitem(znum=z, name=el.name, symbol=el.symbol,
                                                                           material=this['material'],
                                                                           commonname=this['name'],
                                                                           location=location) + '        </div>\n'
                    #print(text, '\n')
                elif i == 1:
                    text = '        <div class="box box2">' + self.oneitem(znum=z, name=el.name, symbol=el.symbol,
                                                                           material=this['material'],
                                                                           commonname=this['name'],
                                                                           location=location) + '        </div>\n'
                    #print(text, '\n')
                else:
                    text = '        <div class="box">' + self.oneitem(znum=z, name=el.name, symbol=el.symbol,
                                                                      material=this['material'],
                                                                      commonname=this['name'],
                                                                      location=location) + '        </div>\n'
                    #print(text, '\n')
                page = page + text
            ## close the wrapper div
            page = page  + '      </div>'

        ##########
        # footer #
        ##########
        page = page + '''
  </body>
</html>

'''
        with open(self.html, 'w') as fh:
            fh.write(page)
        print(f'Wrote html to {self.html}')

    def boxify(self, word):
        '''Convert a word to be spelled by unicode points in the Enclosed
        Alphanumeric Supplement section.  "Negative Squared Latin Capital Letter X"
        See https://unicode-table.com/en/#1F173'''
        boxedword = ''
        for letter in word:
            character = f'&#{127247+ord(letter)};'
            boxedword = boxedword + character
        return(boxedword)
    
    def oneitem(self, znum=26, symbol='Fe', name='Iron', material='FeTiO3', commonname='ilmenite', location='Fe'):
        '''Generate a table that will occupy one div of the output html file.
        This table contains the data from a single standard material.
        The div looks something like this:

        +--------------------------+
        | Symbol         name      |
        |                          |
        |     stoichiometry        |
        |    name of material      |
        |  location if not here    |
        +--------------------------+

        '''
        form = '''
          <table>
            <tr>
              <td rowspan=2><span class="znum">{symbol}</span></td>
              <td align=right><span class="symbol">{name}</span></td>
            </tr>
            <tr><td></td></tr>
            <tr>
              <td colspan=3 align=center><span class="{major}">{material}</span></td>
            </tr>
            <tr>
              <td colspan=3 align=center><span class="name">{commonname}</span></td>
            </tr>
            <tr>
              <td colspan=3 align=center><span class="loc">{location}</span></td>
            </tr>
          </table>
'''

        if len(material) < 12:
            major = 'major'
        elif len(material) < 20:
            major = 'longmajor'
        else:
            major = 'verylongmajor'
        material = re.sub('(\d)', r'<sub>\g<1></sub>', material)
        return(form.format(znum       = znum,
                           name       = name,
                           symbol     = symbol,
                           material   = material,
                           major      = major,
                           commonname = commonname,
                           location   = location,
        ))
        





def main():
    m=Standards()
    #m.spreadsheet = 'Standards.xlsx'
    m.html        = 'BMM-standards.html'
    #m.html        = 'test.html'
    m.singlepage  = False
    #m.read_spreadsheet()
    #m.to_json()
    m.make_html()

if __name__ == "__main__":
    main()
