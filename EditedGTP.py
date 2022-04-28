#! /usr/bin/env python3

"""Getting to philosophy: "scrape" a Wikipedia page and follow its
first link recursively to see if you end up at the Philosophy page
https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy

"""
import urllib.request
import os
import sys

## this is the Philosophy URL -- if we reach this we terminate
philosophy_list = ['Philosophy', 'Philosophical', 'Existence']

## this is the default list of topics we experiment with
topics_default = ['https://en.wikipedia.org/wiki/Xkcd',
                  'https://en.wikipedia.org/wiki/GNU_Project',
                  'https://en.wikipedia.org/wiki/Bertrand_Russell',
                  'https://en.wikipedia.org/wiki/Plague_of_Justinian',
                  'https://en.wikipedia.org/wiki/Public_health',
                
                  'https://en.wikipedia.org/wiki/Spark_plug',
                  'https://en.wikipedia.org/wiki/Quantum_entanglement',
                  'https://en.wikipedia.org/wiki/Toilet_paper'
]

def main():
    topics = topics_default
    if len(sys.argv) > 1:
        # if user gives URLs on the command line then we use those
        # instead of the default topics
        topics = sys.argv[1:]
    if len(topics) > 1:
        graphviz_fname = 'gtp_graph.dot' # default output file
    else:
        ## if we request a single topic then we can use that as a
        ## filename
        graphviz_fname = topics[0].split('/')[-1]
    ## give an error message if the program "dot" (from the package
    ## graphviz) is not available
    if not os.path.exists('/usr/bin/dot'):
        print('Error: the program "dot" does not seem to be installed;')
        print('you can install it with "sudo apt install graphviz"')
        print('and start again')
        sys.exit(1)
    start_graphviz_file(graphviz_fname)
    ## now analyze all the topics
    for topic_url in topics:
        print('INITIAL_TOPIC: {0}'.format(url2topic(topic_url)))
        try:
            url_list = analyze_url([topic_url])
        except RecursionError:
            print('Recursion limit exceeded on %s' % topic_url)
            continue
        except RuntimeError:
            print('Recursion limit exceeded on %s' % topic_url)
            continue
        write_graph_file(url_list, graphviz_fname)
        ## now print some information about what we just did
        print('{0} went through {1} topics'.format(url2topic(topic_url), 
                                                    len(url_list)), end="")
        print(' to reach {0}'.format(url2topic(url_list[-1])))
    ## put the closing line in the graphviz file
    end_graphviz_file(graphviz_fname)
    print('graph information written to file %s' % graphviz_fname)
    ## now run graphviz (the command line is "dot") to make pdf, svg
    ## and png files
    os.system('dot -Tpdf -O %s' % graphviz_fname)
    os.system('dot -Tsvg -O %s' % graphviz_fname)
    os.system('dot -Tpng -O %s' % graphviz_fname)
    print('used "dot" to generate the files %s, %s, %s' 
          % (graphviz_fname + '.pdf', graphviz_fname + '.svg', 
             graphviz_fname + '.png'))

def analyze_url(urls_so_far):
    """This function analyzes a URL.  We first grab the "next" URL (the
    first link in the page).  If the URL is the arrival point
    (i.e. the Philosophy article) then we return right away with the
    list of URLs visited so far.  If the URL has already appeared
    before then we declare we are in a loop.  If we have had more than
    100 URLs then we return without analyzing further.  The above were
    all terminations, but if *none* of those conditions happen then we
    recursively call this function again to analyze the next URL.
    """
    url = urls_so_far[-1]           # analyze the last one added
    page_html = urllib.request.urlopen(url).read()
    next_url = analyze_page(url, str(page_html))
    
    urls_so_far.append(next_url)
    ## print it out
    print('HOP {0} -- {1}'.format(len(urls_so_far), url2topic(next_url)), end="\r")

    if url2topic(next_url).strip('/') in philosophy_list:
        return (urls_so_far)
    elif urls_so_far.count(next_url) > 1:
        return (urls_so_far + urls_so_far[-2:])
    elif len(urls_so_far) > 100:
        return (urls_so_far)
    else:
        return analyze_url(urls_so_far)

def analyze_page(master_url, page_html):
    """Finds the first href (hyptertext link) in the given page."""
    first_href = find_first_href_after_paragraph(master_url, page_html)
    #print('First href is: ')
    #print(first_href)
    first_href = 'https://en.wikipedia.org%s' % first_href
    return first_href

def find_first_href_after_paragraph(master_url, page_html):
    """Find the first hyperlink after the first <p> tag in the document.
    This is becuase in wikipedia the article content actually starts
    with a <p> tag after all the warnings and other frontmatter have
    been put out.
    """
    
    
    first_p_ind = page_html.find('<p>')
    #converted = convert_link(master_url)
    #print(page_html.find(converted, first_p_ind+3))
    #print(page_html.find('<p>',first_p_ind+3))
    
    if page_html.find('<p>', first_p_ind+3) < page_html.find('<b>',first_p_ind+3):
       first_p_ind = page_html.find('<p>', first_p_ind+6)
    html_after_p = ' '
    html_after_p = find_non_list(page_html, first_p_ind,first_p_ind, 0)
    #print('NONE FLAG')
    #print(type(html_after_p))
    #last_p_ind = page_html.find('</p>', first_p_ind)
    """
    print(test-first_p_ind)
    if(test-first_p_ind < 50):
        first_p_ind = page_html.find('<p>', test)
    
    print(page_html[test+4:test+10])
    if page_html[test+5:test+9] == '\n<ul>':
       

    if page_html[first_p_ind+3:first_p_ind+6] == '<b>':
        first_p_ind = page_html.find('<p>', first_p_ind+6)
    """
    
    #html_after_p = page_html[first_p_ind:]
    #if html_after_p is None:
        #print('NONE')
    anchor_split = html_after_p.split('</a>')
    #print(anchor_split[0:20])
    
    anchor_tag = '<a href="'
    series_tag = '/wiki/Categories: '
    
    endtag = '"'
    end = 0                   # FIXME: what should the end default be?
    ## FIXME: must exclude the "warning" type of text, which might be
    ## enclosed in this kind of tags: <td class="mbox-text">
    open_parentheses_until_here = 0
    
    for i, anchor_text in enumerate(anchor_split):
        if anchor_tag in anchor_text:
            
            # ind = anchor_text.index(anchor_tag)
            base_pos = html_after_p.find(anchor_text)
            pos_after_anchor = anchor_text.find(anchor_tag)
            ## we must also exclude URLs that come up in parentheses,
            ## so we must review all the text leading up to the URL
            ## for open parentheses
            open_parentheses_until_here = count_open_parentheses(master_url, html_after_p, 
                                                                 base_pos + pos_after_anchor)
            ## trim the text
            
            anchor_text = anchor_text[pos_after_anchor + len(anchor_tag):]
            #print(anchor_text)
            try:
                end = anchor_text.index(endtag)
            except:
                break
            
        
        href_url = anchor_text[:end]
        #print(href_url)
        #print(canonicalize_topic(href_url))
        if open_parentheses_until_here > 0:
            continue            # skip anchors that are in parentheses
        ## there only some URLs we consider: those that don't start
        ## with wiki ('cause they point within wikipedia), those that
        ## end with html (otherwise we'd be getting images), ...
        if (href_url.startswith('/wiki/')
            and not href_url.endswith('.svg')
            and not href_url.startswith('/wiki/File:')
            and not href_url.startswith('/wiki/Help:')
            and not href_url.startswith('/wiki/Category:')
            and not href_url.startswith('/wiki/Wikipedia:')):
            return anchor_text[:end]
            assert(False)               # we should never get here
def write_graph_file(url_list, graphviz_fname):
    with open(graphviz_fname, 'a') as f:
        prev_topic = url2topic(url_list[0])
        for url in url_list[1:]:
            brief_topic = url2topic(url)
            f.write('    "%s" -> "%s";\n' 
                    % (canonicalize_topic(prev_topic),
                       canonicalize_topic(brief_topic)))
            prev_topic = brief_topic
            f.flush()

def start_graphviz_file(fname):
    with open(fname, 'w') as f: # zero it out
        f.write('digraph gtp {\n')

def end_graphviz_file(fname):
    with open(fname, 'a') as f:
        f.write('}\n')
def url2topic(url):
    brief_topic = url.split('/')[-1].strip('/')
    return brief_topic

def canonicalize_topic(topic):
    result = topic
    ## first change the %xx escape sequences used by http URLs back to
    ## their single characters
    result = urllib.parse.unquote(result)
    ## then remove parentheses and hashtags and dashes, replacing them
    ## with underscores
    result = result.replace('(', '_')
    result = result.replace(')', '_')
    result = result.replace('#', '_')
    result = result.replace('-', '_')
    return result


def count_open_parentheses(master_url, text, ind):
    """counts how many levels of parentheses are open leading up to this
    index in the text"""
    n_open = 0
    for i, char in enumerate(text[:ind+1]):
        if char == '(':
            n_open += 1
        if char == ')':
            n_open -= 1
    return n_open
def convert_link(url):
    newurl = url.rsplit('/', 1)[-1]
    newurl = newurl.replace('_', ' ')
    return newurl
def find_non_list(page_html, index,copy, count):
    """
    if page_html.find('<ul>', index) - index > 75 or page_html.find('<ul>', index) == -1:
        return index
    copysaved = copy
    copy = page_html.find('<p>',copysaved+3)
    print(page_html[copy:copy+10])
    print(copy)
    newid = page_html.find('<ul>', copysaved+3)
    print(newid)
    num = copy-newid
    print(num)
    
    if num < 0:
        num = num * -1
    if num < 100:
        count +=1    
        find_non_list(page_html, index,copy, count)
    else:
        return copy
    
    print('DEBUG')
    """
    copy = page_html.find('</p>' , index+3)
    
    #print('Flag')
    
    
    if page_html.find('<ul>', index, copy+4) == -1 and page_html.find('<br />', index, copy+4) == -1:
        if page_html.find('<a href', index, copy+4) == -1:
            index = page_html.find('<p>', index+3)
            return find_non_list(page_html, index, copy,count)
        else:
            #print(page_html[index:copy+40])
            #print('REUTNRENELEDEJD', index, copy)
            new_html = page_html[index:copy]
            #print(type(new_html))
            return new_html
    else:
        index = page_html.find('<p>', index+3)
        return find_non_list(page_html, index, copy,count)
main()
