def html(x):
    return x.__html__()

def html_list(list_tag, item_tag, values, tohtml=lambda x: x.html()):
    return '<%s>%s</%s>' % (list_tag, ''.join('<%s>%s</%s>' % (item_tag, tohtml(v), item_tag) for v in values), list_tag)

def ul(values, *args, **kwargs):
    return html_list('ul', 'li', values, *args, **kwargs)

def html_set(s):
    if s:
        return '{%s}' % ', '.join(map(lambda x: x.html(), s))
    else:
        return '&empty;'

