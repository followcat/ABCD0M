def nodefilter(node, d=None):
    x = dict(node)
    x.pop('attributes')
    x.pop('childNodes')
    if d is None:
        d = {}
    if (x['top'], x['left']) not in d:
        d[(x['top'], x['left'])] = []
    d[(x['top'], x['left'])].append(x)
    for each in node['attributes']:
        nodefilter(each, d)
    for each in node['childNodes']:
        nodefilter(each, d)
    return d


def nodecomparer(d1, d2):
    results = []
    for each in d1:
        for index in range(len(d1[each])):
            if each not in d2:
                results.append((each, index))
                continue
            else:
                if (d1[each][index]['width'] != d2[each][index]['width'] or
                    d1[each][index]['height'] != d2[each][index]['height']):
                    results.append((each, index))
                    break
                for s in d1[each][index]['style']:
                    if d1[each][index]['style'][s] != d2[each][index]['style'][s]:
                        results.append((each, index))
                        break
    return results


def init_nodeinfo(driver):
    node_function = """
    node_info = {}

    function getTop(e) { 
        var offset=e.offsetTop; 
        if(e.offsetParent!=null) offset+=getTop(e.offsetParent); 
            return offset; 
    } 

    function getLeft(e) { 
        var offset=e.offsetLeft; 
        if(e.offsetParent!=null) offset+=getLeft(e.offsetParent); 
            return offset; 
    }

    function kvnode (node)
    {
        node_info[[getTop(node), getLeft(node), node.clientWidth, node.clientHeight]] = node
        if (node.childNodes && node.childNodes.length) {
            for (var i = 0; i < node.childNodes.length; ++i)
                kvnode (node.childNodes.item(i));
        };
    }

    kvnode(document.body);
    return node_info;
    """
    node_info = driver.execute_script(node_function)
    return node_info


def MarkElements(driver, info, results):
    one_label = """
    function one_label(key) {
        var ele = node_info[key];
        ele.style.border='2px dashed red';
    }
    """
    for each in results:
        arr_str = str(each[0][0])+','+str(each[0][1])+','+\
                  str(info[each[0]][each[1]]['width'])+','+str(info[each[0]][each[1]]['height'])
        try:
            driver.execute_script(one_label+"\none_label(["+arr_str+"]);")
        except Exception as e:
            continue
