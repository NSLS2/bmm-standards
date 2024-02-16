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
        self.beneath_table = self.slurp('tmpl/beneath_table.tmpl')
        self.goto_anchor = self.slurp('tmpl/goto_anchor.tmpl')


    def slurp(self, fname):
        with open(fname, 'r') as myfile:
            text=myfile.read()
        return text
        
            
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

        ## page header and sidebar
        page = self.slurp('tmpl/head.tmpl').format(cssfile=self.cssfile)
        page = page + self.slurp('tmpl/sidebar.tmpl').format(nosamp=self.nosamp)


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
                page = page + self.slurp('tmpl/element_table.tmpl').format(name   = el.name,
                                                                           symbol = el.symbol,
                                                                           z      = z,
                                                                           kcolor = kcolor,
                                                                           lcolor = lcolor,
                                                                           kedge  = xray_edge(el.symbol, 'K')[0],
                                                                           l1edge = xray_edge(el.symbol, 'L1')[0],
                                                                           l2edge = xray_edge(el.symbol, 'L2')[0],
                                                                           l3edge = xray_edge(el.symbol, 'L3')[0])
            else:
                continue        # no samples for thie element
            
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
                page = page + self.slurp('tmpl/element_entry.tmpl').format(missing    = missing,
                                                                           onrefwheel = onrefwheel,
                                                                           formula    = formula,
                                                                           name       = name,
                                                                           location   = location,
                                                                           fluo       = fluo,
                                                                           datafile   = datafile,
                                                                           datafile2  = datafile2)
            page = page + '            </table>\n'
            page = page + '      </div>\n'

        ##########
        # footer #
        ##########
        page = page + self.slurp('tmpl/bottom.tmpl')

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
