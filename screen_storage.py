import StringIO

import Image


def webviewfullscreen(webdriver):
    """"""
    cimgs = []
    screenshots = []
    webdriver.switch_to.context('WEBVIEW_1')
    webdriver.execute_script('window.scrollTo(0, 0);')
    webdriver.implicitly_wait(1000)
    webdriver.switch_to.context('NATIVE_APP')
    webview = webdriver.find_element_by_class_name('android.webkit.WebView')
    size = webview.size
    location = webview.location

    view = webdriver.find_element_by_class_name('android.view.View')
    last_scoll = view.size['height']%size['height']

    webdriver.switch_to.context('WEBVIEW_1')
    total_hegiht = webdriver.execute_script('return document.body.scrollHeight')
    screen_height = webdriver.execute_script('return window.screen.height')

    times = int(total_hegiht/screen_height)
    for index in range(times+1):
        index = index + 1
        webdriver.execute_script('window.scrollTo(0, %d);' %
            (index*screen_height-location['y']/times*index))
        webdriver.switch_to.context('NATIVE_APP')
        png = webdriver.get_screenshot_as_png()
        screenshots.append(png)
        webdriver.switch_to.context('WEBVIEW_1')

    webdriver.switch_to.context('NATIVE_APP')
    for each in range(len(screenshots)):
        img = Image.open(StringIO.StringIO(screenshots[each]))
        if each == len(screenshots)-1:
            region = (location['x'], view.size['height']+view.location['y']-last_scoll,
                      size['width'], size['height'] + location['y'])
        else:
            region = (location['x'], location['y'],
                      size['width'], size['height'] + location['y'])
        cimg = img.crop(region)
        cimgs.append(cimg)
        cimg.save('/tmp/crop_%d.png' % each)

    image_height = sum([each.size[1] for each in cimgs])
    result_image = Image.new('RGBA', (view.size['width'], image_height))
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
