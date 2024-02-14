#!/usr/bin/env python
from openpyxl import load_workbook
import json, datetime, pprint, re, os
from mendeleev import element
from larch.xray import xray_edge

pp = pprint.PrettyPrinter(indent=4)


class CommonMaterials():
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
        
            
#         ##########
#         # header #
#         ##########
#         if self.singlepage is True:
#             with open(self.cssfile) as x: css = x.read()
#             page = f'''
# <html>
#   <head>
#     <title>Common XAFS materials at BMM</title>
#     <style>
# {css}
#     </style>
#   </head>

#   <body>
#   <h1>Common XAFS materials at BMM</h1>'''
#         else:
        page = f'''
<html>
  <head>
    <title>Common XAFS materials at BMM</title>
    <link rel="stylesheet" href="{self.cssfile}" />
    <link rel="stylesheet" href="pt.css" />
  </head>

  <body>
  <main>
'''
        page = page + '''
<div class="topmatter">
</div>
<div id="divfix">
   <div id="container">
     <div id="floated">
       <image src="floor_mat.png" width=90%>
     </div>
     Common XAFS materials
    </div>
   <p>
     <span class="instructions">Click on an element to jump to that list of compounds in BMM's
     collection.</span>
   </p>
   <p>
     Compounds marked with &#10004; are permanently mounted on the reference wheel.
   </p>
   <p>
     Compounds marked with <span style="font-family: \'Brush Script MT\', cursive;">Fl</span>
     were measured in fluorescence.
   </p>
   <p>
     Edge energies in <span id="inrange">black text</span> are accessible at BMM.
     Those in <span id="outofrange">grey text</span> are not.
   </p>
   <p>
     For compounds listed as being on the reference wheel, data are
     ln(I<sub>t</sub>/I<sub>r</sub>).
   </p>
   <p>
     Some L<sub>1</sub> data may not be useful due to a small edge step.
   </p>
   <p>
     As of August 2023, collection of data on these compounds is about 80% complete.
   </p>
   <p>
     <a href="https://github.com/NSLS-II-BMM/bmm-standards">
        <img src="github-mark.svg" width=20px>
        GitHub repository
     </a>
   </p>
</div>

'''

        with open('pt.html') as pt:
            ptable = pt.read()
        page = page + ptable + '</main>\n'
        page = page + '''
        <script type="text/javascript">
            <!--
            function goToAnchor(anchor) {
               var loc = document.location.toString().split("#")[0];
               document.location = loc + "#" + anchor;
               return false;
            }
            //-->
        </script>
        <hr>
        '''    
        for z in range(20, 95):
            el = element(z)
            print(el.symbol, end=' ', flush=True)
            if el.symbol not in data:
                continue
            if xray_edge(el.symbol, 'K')[0] > 23500:
                kcolor, lcolor = 'outofrange', 'inrange'
            else:
                kcolor, lcolor = 'inrange', 'outofrange'
            if xray_edge(el.symbol, 'L3')[0] < 5000:
                lcolor = 'outofrange'
            if len(data[el.symbol]) > 0:
                page = page + f''''

    <h2 id="{el.name}">
       {el.symbol}&nbsp;
       ({z})&nbsp;{el.name}&nbsp;&nbsp;&nbsp;
       <div id="floatright">
         <span id="{kcolor}">K:&nbsp;{xray_edge(el.symbol, 'K')[0]:.0f}&nbsp;eV</span> 
         <span id="{lcolor}">L<sub>1</sub>:&nbsp;{xray_edge(el.symbol, 'L1')[0]:.0f}&nbsp;eV
         L<sub>2</sub>:&nbsp;{xray_edge(el.symbol, 'L2')[0]:.0f}&nbsp;eV
         L<sub>3</sub>:&nbsp;{xray_edge(el.symbol, 'L3')[0]:.0f}&nbsp;eV</span>
      </div>
    </h2>
      <div class="wrapper">\n'''
                page = page + '''
            <table>
              <tr>
                <th></th>
                <th width=30%>Material</th>
                <th width=25%>Common/mineral name</th>
                <th width=20%>Location</th>
                <th width=2%>&nbsp;</th>
                <th width=28%>Data&nbsp;File</th>
              </tr>
'''
            
            for i, this in enumerate(data[el.symbol]):
                missing = 'present'
                if 'missing' in this and this['missing'] is True:
                    missing = 'missing'
                formula = re.sub(r'(\d+\.\d+|\d+)(?!\+)', r'<sub>\g<1></sub>', this['material'])
                #formula = re.sub(r'(\d+\.\d+|\d+)(?=\+)', r'<sup>\g<0></sup>', this['material'])
                name = this['name']
                if len(name) > 0:
                    name = name[0].upper() + name[1:]
                location = ''
                if this['location'] != el.symbol:
                    location = this['location'] # 'location: '+
                if 'refwheel' in this and this['refwheel'] is True:
                    location = 'reference wheel'
                if 'lanthanidewheel' in this and this['lanthanidewheel'] is True:
                    location = 'lanthanide wheel'
                if location == 'sample not in collection':
                    location = f'<span class="missing">({location})</span>'
                    
                if el.atomic_number > 46:
                    edge = 'L<sub>3</sub>'
                else:
                    edge = 'K'
                    
                if 'datafile' not in this:
                    datafile = ''
                elif this['datafile'] is False:
                    datafile = ''
                else:
                    datafile = f'{edge} : <a href="Data/{el.symbol}/{this["datafile"]}">{this["datafile"]}</a>'
                if 'datafile2' not in this:
                    datafile2 = ''
                elif this['datafile2'] is False:
                    datafile2 = ''
                elif not os.path.isfile(f'Data/{el.symbol}/{this["datafile2"]}'):
                    datafile2 = ''
                else:
                    datafile2 = f'<br>L<sub>1</sub> : <a href="Data/{el.symbol}/{this["datafile2"]}">{this["datafile2"]}</a>'
                
                if 'refwheel' in this and this['refwheel'] is True:
                    onrefwheel = '&#10004;'
                else:
                    onrefwheel = ''

                if 'fluorescence' in this and this['fluorescence'] is True:
                    fluo = '<span style="font-family: \'Brush Script MT\', cursive;">Fl</span>'
                else:
                    fluo = ''
                    
                ## generate a div for the table explaining each port
                page = page + f'''
               <tr class={missing}>
                  <td>{onrefwheel}</td>
                  <td>{formula}</td>
                  <td>{name}</td>
                  <td>{location}</td>
                  <td>{fluo}</td>
                  <td>{datafile}{datafile2}</td>
               </tr>
'''
            page = page + '            </table>\n'
            page = page + '      </div>'

        ##########
        # footer #
        ##########
        page = page + '''
  <p class="copyright ctop">
    A large number of the samples on this page were provided by Martin Stennett 
    of the University of Sheffield.  This page would be much less interesting
    and much less useful without his numerous contributions.
  </p>
  <p class="copyright ctop">
    This web page, any associated software, and its collection of data
    were developed and measured by a NIST employee. Pursuant to title
    17 United States Code Section 105, works of NIST employees are not
    subject to copyright protection in the United States.  Permission
    in the United States and in foreign countries, to the extent that
    NIST may hold copyright, to use, copy, modify, create derivative
    works, and distribute this web page, software, data, and its
    documentation without fee is hereby granted on a non-exclusive
    basis, provided that this notice and disclaimer of warranty
    appears in all copies.
  </p>
  <p class="copyright">
    See the <a href='LICENSE'>license file</a> for details.
  </p>
  </body>
</html>

'''
        with open(self.html, 'w') as fh:
            fh.write(page)
        print(f'\nWrote html to {self.html}')

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
        This table contains the data from a single common material.
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

        if len(material) < 11:
            major = 'major'
        elif len(material) < 20:
            major = 'longmajor'
        else:
            major = 'verylongmajor'
        material = re.sub(r'(\d+\.\d+|\d+)', r'<sub>\g<1></sub>', material)
        return(form.format(znum       = znum,
                           name       = name,
                           symbol     = symbol,
                           material   = material,
                           major      = major,
                           commonname = commonname,
                           location   = location,
        ))
        





def main():
    m=CommonMaterials()
    #m.spreadsheet = 'Standards.xlsx'
    m.html        = 'BMM-standards.html'
    #m.html        = 'test.html'
    m.singlepage  = False
    #m.read_spreadsheet()
    #m.to_json()
    m.make_html()

if __name__ == "__main__":
    main()
