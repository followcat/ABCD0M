import re
import time
import math
import StringIO
import xml.etree.ElementTree as ET

import Image


def bounds(points_str):
    """
        >>> import screen_storage
        >>> screen_storage.bounds('[0,0][480,800]')
        [0, 0, 480, 800]
    """
    return [int(each) for each in re.findall(r'[\d]+', points_str)]


def size(bound):
    """
        >>> import screen_storage
        >>> bound = [0, 0, 480, 800]
        >>> size = screen_storage.size(bound)
        >>> size['width'], size['height']
        (480, 800)
    """
    return {'width':bound[2]-bound[0], 'height':bound[3]-bound[1]} 


def location(bound):
    """
        >>> import screen_storage
        >>> bound = [0, 0, 480, 800]
        >>> location = screen_storage.location(bound)
        >>> location['x'], location['y']
        (0, 0)
    """
    return {'x':bound[0], 'y':bound[1]}


def get_contain(driver):
    driver.switch_to.context('NATIVE_APP')
    xmlsrc = driver.page_source
    xmlobj = ET.fromstring(xmlsrc.encode('utf-8'))[0]
    return xmlobj


def get_webview(driver):
    """"""
    def area(elem):
        bound = bounds(elem.get('bounds'))
        return (bound[2]-bound[0])*(bound[3]-bound[1])
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
    return results[0]


def webviewfullscreen(driver):
    """"""
    cimgs = []
    screenshots = []
    driver.switch_to.context('WEBVIEW_1')
    driver.execute_script('window.scrollTo(0, 0);')
    time.sleep(1)

    contain = get_contain(driver)
    contain_bound = bounds(contain.get('bounds'))
    contain_size = size(contain_bound)
    webview = get_webview(driver)
    webview_bound = bounds(webview.get('bounds'))
    webview_location = location(webview_bound)

    driver.switch_to.context('WEBVIEW_1')
    total_hegiht = driver.execute_script('return document.body.scrollHeight')
    screen_height = driver.execute_script('return window.screen.height')

    scale = float(screen_height)/contain_size['height']
    scroll_height = math.ceil((contain_size['height']-webview_location['y'])*scale)
    moved = 0
    count = 0
    while True:
        last_moved = moved
        driver.switch_to.context('WEBVIEW_1')
        scrolled = driver.execute_script('return document.body.scrollTop')
        driver.execute_script('window.scrollTo(0, %d);' % (count*scroll_height))
        moved = driver.execute_script('return document.body.scrollTop') - scrolled
        time.sleep(1)
        driver.switch_to.context('NATIVE_APP')
        png = driver.get_screenshot_as_png()
        screenshots.append(png)
        count += 1
        if last_moved > moved or (last_moved > 0 and moved == 0):
            break
    the_last_moved = int(moved/scale)

    for each in range(len(screenshots)):
        img = Image.open(StringIO.StringIO(screenshots[each]))
        region = [webview_location['x'], webview_location['y'],
                  contain_size['width'], contain_size['height']]
        if each == len(screenshots)-1:
            region[1]=region[3]-the_last_moved
        cimg = img.crop(tuple(region))
        cimgs.append(cimg)
        # cimg.save('/tmp/crop_%d.png' % each)

    image_height = sum([each.size[1] for each in cimgs])
    result_image = Image.new('RGBA', (contain_size['width'], image_height))
    paste_height = 0
    for each in cimgs:
        result_image.paste(each, (0, paste_height))
        paste_height += each.size[1]
    # result_image.save('/tmp/x.png')
    return result_image


def MarkElement(id, driver):
    jscodes = """
    var ele = document.getElementById('%s');
    ele.style.border='10px dashed red';""" % (id)
    driver.execute_script(jscodes)


def DOM(driver):
    jscodes = """
    var infoarr = [
    'padding', 'paddingTop', 'paddingBottom', 'paddingRight', 'paddingLeft',
    'margin', 'marginTop', 'marginBottom', 'marginRight', 'marginLeft',
    'content',
    "border", "borderBottom", "borderBottomColor", "borderBottomLeftRadius",
    "borderBottomRightRadius", "borderBottomStyle", "borderBottomWidth",
    "borderCollapse", "borderColor", "borderImage", "borderImageOutset",
    "borderImageRepeat", "borderImageSlice", "borderImageSource",
    "borderImageWidth", "borderLeft", "borderLeftColor", "borderLeftStyle",
    "borderLeftWidth", "borderRadius", "borderRight", "borderRightColor",
    "borderRightStyle", "borderRightWidth", "borderSpacing", "borderStyle",
    "borderTop", "borderTopColor", "borderTopLeftRadius", "borderTopRightRadius",
    "borderTopStyle", "borderTopWidth", "borderWidth"];

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
        if (css == null) {
            return s;
        }
        for (var i in infoarr) {
            var key = infoarr[i];
            if (key in css) {
                s[key] = [css[key]];
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
