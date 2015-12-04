var dom_dict = dump_dom();
var socket = "";
(function() {
            namespace = '/test';
            socket = io.connect('http://' + document.domain + ':' + "5000" + namespace);
            socket.on('action', function(msg) {
                decode_action(msg);
            });
            socket.on('connect', function() {
                socket.emit('action event', {data: "testdata" });
            });
        })();

function getEle (action) {
    switch(action['type']) {
        case 'id':
            return document.getElementById(action['label']);
        case 'class':
            return document.getElementsByClassName(action['label'])[action['index']];
    }
}

function decode_action(action_list)
{
    for(var i =0;i<action_list.length;i++) {
        action = action_list[i];
        e = getEle(action);
        switch(action['act']) {
            case 'fill':
                e.value = action['value'];
                break;
            case 'click':
                e.click();
                break;
        }
    }
}

function dump_dom ()
{
    if (typeof(Node) == "undefined") {
        alert ("Sorry, this script doesn't work with Internet Explorer.");
        return;
    }
    dom_dict = traverse_nodes (document);
    return dom_dict;
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
        'style': window.getComputedStyle(node, null),
    };
    if (node.attributes && node.attributes.length) {
        for (var i = 0; i < node.attributes.length; ++i)
            node_info.attributes.push(traverse_nodes (node.attributes.item(i)));
    }
    if (node.childNodes && node.childNodes.length) {
        for (var i = 0; i < node.childNodes.length; ++i)
            node_info.childNodes.push(traverse_nodes (node.childNodes.item(i)));
    }
    return node_info;
}
