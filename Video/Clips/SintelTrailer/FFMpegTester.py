#!/bin/python
'''This will run tests of various ffmpeg codecs, bitrates, options, etc

This will iterate through multiple tests with multiple different codecs and options and give you 
retults.html when you're done.

This test is strictly single threaded, as some of the codecs will utilize multiple processors if 
they are available, thus we want to only run one test at a time (so we don't get two multi-processor 
tests at the same time, competing for CPU).
'''

#TODO:
# - Command line arguments
#   - Option to skip conversion (output file must already be in place)
#   - JSON File (input)
#   - JSON/HTML output
#   - Basic input
#   - basic test? default test?
#   - Override external_vars from the json file?
# - Concatenate all the videos for each test into one with text between clips (long-range goal)
# - Log command output to a text file for each trial
# - Unit tests - esp for the standalone functions
# - Replace manual HTML output (esp for image pages) with a templating system
# - Enable full HTML disabling
# - Javascript Page
#   - When no images selected, gray out things, write message?
#   - Tabs settings?
#   - Pressing return selects forward, rate update, or zoom update depending on cursor

import os
import os.path
from subprocess import call
import time
import shlex
import math
import cStringIO
import tokenize
import json
from optparse import OptionParser

# This function will remove comments starting with # from a string
# See: http://code.activestate.com/recipes/576704/ for any details, I removed the docstring part
def remove_comments(source):
    io_obj = cStringIO.StringIO(source)
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        ltext = tok[4]
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += (" " * (start_col - last_col))
        if token_type == tokenize.COMMENT:
            pass
        else:
            out += token_string
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
    return out

def filesize_format(size_in_bytes,base=1000):
    if size_in_bytes <= 0:
        return 0, 'B'

    byteunits = ()
    if base == 1000:
        byteunits = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    elif base == 1024:
        byteunits = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB')
    exponent = int(math.log(size_in_bytes, base))
    return float(size_in_bytes) / pow(base, exponent), byteunits[exponent]

def round_sigfigs(value, significant):
    if value == 0:
        return 0
    return round(value, int(significant - math.ceil(math.log10(abs(value)))))

def variable_combinations(variables):
    """ Finds all possible combinations of the variables
    
    Input format is a list with dictionaries for each variable (which contains a list of all
    possible values) of the format:
    [{'name':'name1','values':['value1','value2','etc.']},
    {'name':'name2','values':['value1','value2','etc.']},
    {'name':'name3','values':['value1','value2','etc.']}]

    This will run recursively to match up all the possible combinations of variables, and 
    return them in a list of dictionaries with "name":"value" pairs for each variable in 
    each dictionary. 
    The returned format will be:
    [{'name1':'value1','name2':'value1','name3':'value1'},
    {'name1':'value1','name2':'value1','name3':'value2'},
    ...
    {'name1':'value1','name2':'value1','name3':'valueX'},
    {'name1':'value1','name2':'value2','name3':'value1'},
    ...
    {'name1':'valueX','name2':'valueX','name3':'valueX'}]


    testcase
    input: [{'values': ['1', '2'], 'name': 'v1'}, {'values': ['3', '4'], 'name': 'v2'}, {'values': ['5', '6'], 'name': 'v3'}]
    output: [{'v1': '1', 'v2': '3', 'v3': '5'}, {'v1': '1', 'v2': '3', 'v3': '6'}, {'v1': '1', 'v2': '4', 'v3': '5'}, {'v1': '1', 'v2': '4', 'v3': '6'}, {'v1': '2', 'v2': '3', 'v3': '5'}, {'v1': '2', 'v2': '3', 'v3': '6'}, {'v1': '2', 'v2': '4', 'v3': '5'}, {'v1': '2', 'v2': '4', 'v3': '6'}]

    """
    combo = []
    if variables:
        var = variables[0]
        next_vars = variables[1:]
        next_combo = variable_combinations(next_vars)
        for val in var['values']:
            if next_combo:
               for c in next_combo:
                    tc = c.copy() # Othewise this would be overwritten in the next loop
                    tc[var['name']]=val
                    combo.append(tc)
            else:
                c={var['name']:val}
                combo.append(c)
    return combo

class TestPoints():
    def __init__(self, points, test_name):
        self.tp = {}
        self.test_name = test_name
        
        self.output_html = True
        self.output_json = False

        cmd = "mkdir -p img thumb frames"
        call(shlex.split(cmd))
        
        for point in points:
            if point.__class__ == "".__class__: # If points is just a list of strings for times
                self.tp[point] = {'sec':point}
                self.tp[pt]['title'] = test_name + "_" + point +  "s"
                self.tp[pt]['complete'] = []
            elif point.__class__ == {}.__class__:
                pt = point['sec'] 
                self.tp[pt] = {"sec":pt}
                self.tp[pt]['crop'] = {'w':point['w'],'h':point['h'],'x':point['x'],'y':point['y']}
                self.tp[pt]['title'] = test_name + "_" + point['sec'] +  "s"
                self.tp[pt]['complete'] = []
        
    def html_segment(self):
        snip = ""
        for point,info in self.tp.items():
            snip += '<a href="' + self.test_name + "_" + point + 's.html">' + self.test_name + "_" + point + 's</a><br />\n'
        return snip

    def zoom_scale(self,w,h):
        w = str(int( int(w)*self.crop_zoom_multiplier ))
        h = str(int( int(h)*self.crop_zoom_multiplier ))
        return w,h

    def grab_points(self, video_file):
        thumbs = []
        for point in self.tp.values():
            # Use ffmpeg to make a single frame png
            cmd = 'ffmpeg -i ' + video_file + ' -an -ss ' + point['sec'] + ' -an -r 1 -vframes 1 -y %d.png' 
            call(shlex.split(str(cmd)))

            img = 'img/' + video_file + "-" + point['sec'] + 's.png'
            # Move the output file to an appropriately named file in the img/ directory
            cmd = 'mv 1.png ' + img
            call(shlex.split(str(cmd)))
            # Keep the full frame in the frames dir
            frm = 'frames/'  + video_file + "-" + point['sec'] + 's.png'
            cmd = 'cp ' + img + ' ' + frm
            call(shlex.split(str(cmd)))

            # Make the img actually the cropped version
            try:
                w = point['crop']['w']
                h = point['crop']['h']
                x = point['crop']['x']
                y = point['crop']['y']
                cmd = 'mogrify -crop ' + w+'x'+h+'+'+x+'+'+y+' ' + img 
                call(shlex.split(str(cmd)))
            except KeyError:
                pass

            thumb = 'thumb/' + video_file + "-" + point['sec'] + 's.png'
            # Create a thumbnail image in the thumb/ directory
            cmd = 'convert ' + img + ' -resize 100x100 ' + thumb
            call(shlex.split(str(cmd)))

            thumbs.append({'img':img,'thumb':thumb})
            
            shot = {}
            shot['name'] = video_file
            shot['img'] = img
            shot['thumb'] = thumb
            shot['frame'] = frm
            point['complete'].append(shot)
            self.make_json(point)
            self.make_html(point)
          
        return thumbs
        
    def make_json(self, point):
        if self.output_json:
            f = open(point['title']+'.json','w')
            f.write(json.dumps(point['complete']))
            f.close()
        
    def make_html(self, point):
        if self.output_html:
            html = """
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
"""
            html += '        <title>' + point['title'] + '</title>'
            html += """
    </head>
    <body>
        <script src="jquery-1.5.2.js"></script>
        <script>
            var current_image = 0;        
            var auto = false;
            var auto_box;
            var interval_id = 0;
            
            all_options = new Array();          
"""
            index_number = 0
            for shot in point['complete']:
                html += '            all_options[' + str(index_number) + '] =  new Object();\n'
                html += '            all_options[' + str(index_number) + '].name = "' + shot['name'] + '";\n'
                html += '            all_options[' + str(index_number) + '].img = "' + shot['img'] + '";\n'
                index_number += 1
                
            html += '            var current_image = ' + str(index_number) + ';\n'
            html += '            var width = ' + str(point['crop']['w']) + ';\n'
            html += '            var height = ' + str(point['crop']['h']) + ';\n'
            html += '            var zoom_multiplier = 1;\n'
            html += """
            $(document).ready(function(){
                images = all_options;
                auto_box = document.control.automate_box;
                auto_box.checked = true;
                
                $.each(document.test_select, function(index, box){
                    $.each(all_options, function(index, test_img){
                        if( box.value == test_img.name ){
                            test_img.box = box;
                        }
                    });
                });
                
                if (all_options.length < 10){
                    select_all();
                }
                else{
                    select_none();
                }
            });
            
            function change_image(){
                if((current_image >= 0) && (current_image < images.length)){
                    img = images[current_image];
                    document.main_image.src = img.img;
                    document.getElementById('image_name').innerHTML = img.name + " Image:" + (current_image+1) + "/"+ images.length;
                }
            }
            function goback(){ //Are there better ways to do this with iterators over an array?
                current_image = current_image - 1;
                if (current_image < 0){
                    current_image = images.length-1;
                }
                change_image();
            }
            
            function goforward(){ //Are there better ways to do this with iterators over an array?
                current_image = current_image + 1;
                if (current_image >= images.length){
                    current_image = 0;
                }
                change_image();
            }
            
            function run_interval(){
                interval = document.getElementById('interval_field').value;
                if (auto_box.checked){
                    clearInterval(interval_id);
                    interval_id = setInterval(goforward, interval);
                }
                else{
                    clearInterval(interval_id);
                }
            }
            function automate(){
                run_interval();
            }
            
            function update_btn(){
                run_interval();
            }
            
            function check_changed(){
                build_list();
            }
            function select_all(){
                $.each(document.test_select, function(index, box){
                    box.checked = true;
                });
                build_list();
            }
            function select_none(){
                $.each(document.test_select, function(index, box){
                    box.checked = false;
                });
                build_list();
            }
            function change_zoom(){
                var zoom = parseFloat(document.control.zoom_field.value);
                if ((zoom != NaN) && (zoom > 0)){
                    document.main_image.width = width * zoom;
                    document.main_image.height = height * zoom;
                }
            }
                        
            function build_list(){
                images = Array();
                num_images = 0;
                
                $.each(all_options, function(index, test_img){
                    current_image = -1;
                    if( typeof test_img.box != "undefined"){
                        if(test_img.box.checked){
                            images[num_images] = test_img;
                            num_images += 1;
                            current_image = 0; // We have at least one image, initialize this                    
                        }
                    }
                    change_image();
                    run_interval();
                });
            }
            
        </script>
        
        <b id="image_name"></b> <br /> 
        <img name="main_image" src="" /><br />
        <form name="control" action="">
            <input type="button" value="Back" onClick="javascript:goback()" /> 
            <input type="button" value="Forward" onClick="javascript:goforward()" /><br />
            <input type="checkbox" name="automate_box" onClick="javascript:automate()"/> Automate &nbsp; &nbsp; &nbsp; 
            <input type="text" value="1000" size="4" id="interval_field" />ms 
            <input type="button" value="Update" onClick="javascript:update_btn()" />&nbsp; &nbsp; &nbsp;
            Zoom: <input type="text" value="1.0" size="2" name="zoom_field" />
            <input type="button" value="Update" onClick="javascript:change_zoom()"/>
        </form> 
        <form name="test_select" action"">   
            <p name="checkboxes"> Select the individual tests you would like to see above:<br />
            <a href="#" onClick="javascript:select_all()">All</a>/<a href="#" onClick="javascript:select_none()">None</a><br />
"""
            for shot in point['complete']:
                html += '                <input type="checkbox" value="' + shot['name'] + '" onClick="javascript:check_changed()"/>\n'
                html += '                ' + shot['name'] + '<br />\n'
            
            html += '            </p>\n        </form>'
    
            for shot in point['complete']:
                html += '        <p>' + shot['name'] + '<br />\n'
                html += '        <img src="' + shot['img'] + '">\n'
                html += '        </p>\n' 
                
            html += """
     </body>
</html>
"""
            f = open(point['title']+'.html','w')
            f.write(html)
            f.close()

class FFMpegTester():
    def __init__(self):
        self.run_number = 0

        # Hard coded options (change in future)
        self.run_conversion = True
        #self.run_conversion = False
                
        self.input_file = "test.json"
        self.output_html = True
        self.output_json = False
        
        
    def apply_variables(self, data, variables):
        for k,v in variables.items():
            data = data.replace(k,v)
        return data

    def run(self):
        f = open(self.input_file,'r')
        fstring = f.read()
        f.close()
        no_comment_string = remove_comments(fstring)
        data = json.loads(no_comment_string)  # Really just need the vars
        trim_data = {}
        trim_data['input'] = data['input']
        trim_data['tests'] = data['tests']
        data_string = json.dumps(trim_data)
        replaced_string = self.apply_variables(data_string, data['external_vars'])
        self.data = json.loads(replaced_string)
        self.data['external_vars'] = data['external_vars']
       
        self.run_tests()

    def start_html(self, name):
        self.results = open(name + ".html", "w")

        self.results.write("<html>\n<head><title>FFMpegTester Results</title></head>\n")
        self.results.write("<body>\n") 
        self.results.write("<p>Screen Capture Comparison Pages:<br />\n")

        self.results.write(self.tps.html_segment())

        self.results.write("</p>\n")
        self.results.write('<table style="text-align: left; width: 100%;" border="1" ')
        self.results.write('cellpadding="2" cellspacing="2"><tbody>\n')
        self.results.write('  <tr>\n')
        self.results.write("   <td><b>No.</b></td>\n")
        self.results.write("   <td><b>Test Title</b></td>\n")
        self.results.write("   <td><b>Command(s)</b></td>\n")
        self.results.write("   <td><b>Elapsed Time (wall clock)</b></td>\n")
        self.results.write("   <td><b>CPU Time</b></td>\n")
        self.results.write("   <td><b>File Size</b></td>\n")
        self.results.write("   <td><b>Example Images</b></td>\n")
        self.results.write("  </tr>\n")

    def finish_html(self):
        self.results.write("</tbody></table>\n</body>\n</html>\n")
        self.results.close()

    def run_tests(self):
        for infile in self.data['input']:
            self.tps = TestPoints(infile['image_points'], infile['name'])

            self.start_html(infile['name'])

            self.current_input_file = infile
            input_name = infile['name']
            input_files = ""
            for item in infile['files']:
                input_files = input_files + " -i " + item
            for test in self.data['tests']:
                self.current_test = test
                vc = ""
                try:
                    vc = variable_combinations(test['variables'])
                except KeyError:
                    vc = [{"":""}]
                for combo in vc:
                    self.current_combo = combo
                    # Append the special (and fixed) variables
                    combo['INPUT_NAME'] = input_name
                    combo['INPUT_FILES'] = input_files
                    cmds = test['commands'][:]
                    output = test['output']
                    for name, value in combo.items():
                        output = output.replace(name, value)
                        for val in range(len(cmds)):
                            cmds[val] = cmds[val].replace(name, value)
                    self.run_test_version(cmds, output)
            self.finish_html()

    def run_test_version(self, cmds, output):
        print "Starting: " + output
        self.results.write("  <tr>\n")
        self.run_number += 1
        self.results.write("   <td>" + str(self.run_number) + "</td>\n")
        self.results.write("   <td>" + self.current_test['title'] + "</td>\n")
        self.results.write("   <td>\n")
        self.results.write("    <a href=\"" + output + "\">" + output + "</a><br>\n") #Jumping the gun a bit
        # TODO start CPU timer...is it possible?
        start = time.time()
        os_start = os.times()
        for cmd in cmds:
            print cmd
            self.results.write("    " + cmd + "<br>\n") 
            c = shlex.split(str(cmd))
            if self.run_conversion: # Only do re-processing, don't actually run
                call(c)
        os_stop = os.times()
        stop = time.time()
        elapsed = stop - start
        os_elapsed = os_stop[2] - os_start[2] + os_stop[3] - os_stop[3]
        self.results.write("   </td>\n")
        self.results.write("   <td>" + str(round_sigfigs(elapsed,4)) + "s</td>\n")
        self.results.write("   <td>" + str(round_sigfigs(os_elapsed,4)) + "s</td>\n")

        # Get size of output file
        s = os.path.getsize(output)
        size, units = filesize_format(s)
        size = round_sigfigs(size, 3)
        self.results.write("   <td>" + str(size) + units + "</td>\n")

        # Create Image for each image point
        self.results.write("   <td>")
        thumbs = self.tps.grab_points(output)
        for thumb in thumbs:
            self.results.write('    <a href="' + thumb['img'] + '"><img src="' + thumb['thumb'] + '"></a>\n')
        self.results.write("   </td>\n")
        self.results.write("  </tr>\n")
        self.results.flush()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input", help="A JSON file containing the data to run", default="test.json")
    parser.add_option("-w", "--html", action="store_true", dest="output_html", default=False, help="Output HTML web-page for each image sample")
    parser.add_option("-j", "--json", action="store_true", dest="output_json", default=False, help="Output JSON for each set of images")
    parser.add_option("-c", "--no_conversion", action="store_false", dest="conversion", default=True, help="Disable the actual conversion commands, only do post-processing")

    (options, args) = parser.parse_args()
    
    t = FFMpegTester()
    
    t.run_conversion = options.conversion
    t.input_file = options.input
    t.output_html = options.output_html
    t.output_json = options.output_json
    
    t.run()

