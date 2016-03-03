import re
import time
import math
import StringIO
import xml.etree.ElementTree as ET

import Image


def contain_size(driver):
    driver.switch_to.context('NATIVE_APP')
    xmlsrc = driver.page_source
    xmlobj = ET.fromstring(xmlsrc.encode('utf-8'))[0]
    bounds = [int(each) for each in re.findall(r'[\d]+', xmlobj.get('bounds'))]
    size = {'width':bounds[2]-bounds[0], 'height':bounds[3]-bounds[1]}
    return size


def webview_locate(driver):
    """"""
    def area(elem):
        bounds = [int(each) for each in re.findall(r'[\d]+', elem.get('bounds'))]
        return (bounds[2]-bounds[0])*(bounds[3]-bounds[1])
    def allview(xmlobj, save=None):
        if save is None:
            save = []
        elems = list(xmlobj)
        for each in elems:
            allview(each, save)
        if xmlobj.tag == 'android.view.View':
            save.append(xmlobj)
        return save
    driver.switch_to.context('NATIVE_APP')
    xmlsrc = driver.page_source
    xmlobj = ET.fromstring(xmlsrc.encode('utf-8'))
    results = sorted(allview(xmlobj), key=lambda each: area(each), reverse=True)
    points = [int(each) for each in re.findall(r'[\d]+', results[0].get('bounds'))]
    return {'x':points[0], 'y':points[1]}

def webviewfullscreen(driver):
    """"""
    cimgs = []
    screenshots = []
    driver.switch_to.context('WEBVIEW_1')
    driver.execute_script('window.scrollTo(0, 0);')
    time.sleep(1)
    view_size = contain_size(driver)
    webview_location = webview_locate(driver)

    driver.switch_to.context('WEBVIEW_1')
    total_hegiht = driver.execute_script('return document.body.scrollHeight')
    screen_height = driver.execute_script('return window.screen.height')

    scale = float(screen_height)/view_size['height']
    scroll_height = math.ceil((view_size['height']-webview_location['y'])*scale)
    moved = 0
    count = 0
    scrolled = 0
    times = math.ceil(float(total_hegiht/screen_height)) + 1
    while True:
        last_scrolled = moved
        driver.execute_script('window.scrollTo(0, %d);' % (count*scroll_height))
        moved = driver.execute_script('return document.body.scrollTop') - scrolled
        scrolled = driver.execute_script('return document.body.scrollTop')
        time.sleep(1)
        driver.switch_to.context('NATIVE_APP')
        png = driver.get_screenshot_as_png()
        screenshots.append(png)
        driver.switch_to.context('WEBVIEW_1')
        count += 1
        if last_scrolled > moved or (last_scrolled > 0 and moved == 0):
            break
    last_scroll = int(moved/scale)

    driver.switch_to.context('NATIVE_APP')
    for each in range(len(screenshots)):
        img = Image.open(StringIO.StringIO(screenshots[each]))
        region = [webview_location['x'], webview_location['y'],
                  view_size['width'], view_size['height']]
        if each == len(screenshots)-1:
            region[1]=region[3]-last_scroll
        cimg = img.crop(tuple(region))
        cimgs.append(cimg)
        cimg.save('/tmp/crop_%d.png' % each)

    image_height = sum([each.size[1] for each in cimgs])
    result_image = Image.new('RGBA', (view_size['width'], image_height))
    paste_height = 0
    for each in cimgs:
        result_image.paste(each, (0, paste_height))
        paste_height += each.size[1]
    result_image.save('/tmp/x.png')
    return cimgs


def DOM(driver):
    jscodes = """
    function dump_dom ()
    {
        if (typeof(Node) == "undefined") {
            alert ("Sorry, this script doesn't work with Internet Explorer.");
            return;
        }
        dom_dict = traverse_nodes (document.body);
        return dom_dict;
    }

    function css2json(css) {
        var s = {};
        for (var i in css) {
            if ((css[i])) {
                s[i] = [css[i]];
            }
        }
        return s;
    }

    function traverse_nodes (node)
    {
        var node_info = {
            'id': node.id,
            'name': node.nodeName,
            'class': node.className,
            'value': node.nodeValue,
            'nodetype': node.nodeType,
            'attributes': [],
            'childNodes': [],
            'style': css2json(window.getComputedStyle(node, null)),
        };
        if (node.attributes && node.attributes.length) {
            for (var i = 0; i < node.attributes.length; ++i)
                node_info.attributes.push(traverse_nodes (node.attributes.item(i)));
        };
        if (node.childNodes && node.childNodes.length) {
            for (var i = 0; i < node.childNodes.length; ++i)
                node_info.childNodes.push(traverse_nodes (node.childNodes.item(i)));
        };
        return node_info;
    } 

    return dom_dict = dump_dom();
    """
    style_dict = driver.execute_script(jscodes)
    return style_dict
