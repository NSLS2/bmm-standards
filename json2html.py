#!/usr/bin/env python
import json, re, os
from mendeleev import element
from larch.xray import xray_edge


class CommonMaterials():
    '''A class for managing a JSON file of items in the BMM standards
    collection and writing a useful HTML file summarizing the collection.

    Example
    =======

    from json2html import Standards
    m = Standards()
    m.html = 'test.html'
    m.make_html()

    '''
    def __init__(self):
        self.json = 'standards.json'
        self.html = 'test.html'
        self.cssfile = 'standards.css'
        self.nosamp = '[___]'
        self.beneath_table = '''
  </div>
  <div class="color-table">
    <section class="element alkali color-guide" id="cg-alkali">Alkali Metal</section>
    <section class="element alkaline color-guide" id="cg-alkaline">Alkaline Metal</section>
    <section class="element transition color-guide" id="cg-transition">Transition Metal</section>
    <section class="element basic color-guide" id="cg-basic">Basic Metal</section>
    <section class="element semimetal color-guide" id="cg-semimetal">Semimetal</section>
    <section class="element nonmetal color-guide" id="cg-nonmetal">Nonmetal</section>
    <section class="element halogen color-guide" id="cg-halogen">Halogen</section>
    <section class="element noble color-guide" id="cg-noble">Noble Gas</section>
    <section class="element lanthanide color-guide" id="cg-lanthanide">Lanthanide</section>
    <section class="element actinide color-guide" id="cg-actinide">Actinide</section>
    <section class="element nostandards color-guide" id="cg-nostandards">No Standards</section>
  </div>
  
  </main>
'''
        self.goto_anchor = '''
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


            
    def element_with_samples(self, this):
        '''Generate an element box in the periodic table for an element
        represented in this data collection.

        '''
        tmpl = '''
   <section class="element {type}" id="{key}" onclick="goToAnchor('{name}')">
     <div class="element-number">{number}</div>
     <h2 class="element-symbol">{symbol}</h2>
     <div class="element-name">{name}</div>
     <!-- <div class="element-weight">{weight}</div> -->
   </section>
'''
        return tmpl.format(**this)
        
    def element_without_samples(self, this):
        '''Generate an element box in the periodic table for an element
        for which no data exists in this collection.

        '''
        tmpl = '''
   <section class="element {type} nolink" id="{key}">
     <div class="element-number">{number}</div>
     <h2 class="element-symbol">{symbol}</h2>
     <div class="element-name">{name}</div>
     <!-- <div class="element-weight">{weight}</div> -->
   </section>
'''
        return tmpl.format(**this)

        
    def make_html(self):
        '''Write the contents of the JSON file to a pretty html file'''
        notfound = []
        with open('standards.json', 'r') as myfile:
            data=json.loads(myfile.read())
        
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
        page = page + f'''
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
        <span class="missing">{self.nosamp}</span> means the data was measured 
        at BMM on a high-quality sample, but the sample is not in BMM's 
        collection.
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
       <a href="https://github.com/NSLS-II-BMM/bmm-standards">
          <img src="github-mark.svg" width=20px>
          GitHub repository
       </a>
     </p>
  </div>

  <div class="ptable">
'''


        ## generate the element boxes in the periodic table
        with open('pt.json', 'r') as ptjson:
            ptdata=json.loads(ptjson.read())
        for el in ptdata.keys():
            ptdata[el]["key"] = el
            if ptdata[el]["link"]:
                page = page + self.element_with_samples(ptdata[el])
            else:
                page = page + self.element_without_samples(ptdata[el])

            
        ## the color explanation table and the javascript for going to
        ## an anchor from the periodic table
        page = page + self.beneath_table
        page = page + self.goto_anchor

        ## generate a table of samples in this collection for every element
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
                page = page + f'''

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
      <div class="wrapper">

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
                formula = re.sub(r'((\d+\.\d+|\d+)\+)', r'<sup>\1</sup>', formula) #this['material'])

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
                    location = f'<span class="missing">{self.nosamp}</span>'
                    
                edge = 'K'
                if el.atomic_number > 46:
                    edge = 'L<sub>3</sub>'
                    
                if 'datafile' not in this:
                    datafile = ''
                elif this['datafile'] is False:
                    datafile = ''
                elif not os.path.isfile(f'Data/{el.symbol}/{this["datafile"]}'):
                    if this["datafile"] != '':
                        notfound.append(this["datafile"])
                    datafile = ""
                else:
                    datafile = f'{edge} : <a href="Data/{el.symbol}/{this["datafile"]}">{this["datafile"]}</a>'

                if 'datafile2' not in this:
                    datafile2 = ''
                elif this['datafile2'] is False:
                    datafile2 = ''
                elif not os.path.isfile(f'Data/{el.symbol}/{this["datafile2"]}'):
                    if this["datafile2"] != '':
                        notfound.append(this["datafile2"])
                    datafile2 = ''
                else:
                    datafile2 = f'<br>L<sub>1</sub> : <a href="Data/{el.symbol}/{this["datafile2"]}">{this["datafile2"]}</a>'

                onrefwheel = ''
                if 'refwheel' in this and this['refwheel'] is True:
                    onrefwheel = '&#10004;'

                fluo = ''
                if 'fluorescence' in this and this['fluorescence'] is True:
                    fluo = '<span style="font-family: \'Brush Script MT\', cursive;">Fl</span>'
                    
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
            page = page + '      </div>\n'

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
        if len(notfound) > 0:
            print('\nMissing or misspelled files:')
            for f in notfound:
                print(f'\t{f}')

        





def main():
    collection      = CommonMaterials()
    collection.html = 'BMM-standards.html'
    collection.make_html()

if __name__ == "__main__":
    main()
