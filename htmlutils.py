from os import mkdir,remove,path
from shutil import copy,move
from veloxutils import remove_non_ascii
from bs4 import BeautifulSoup as bs

def _get_article_body(doc,filename):
    f = open(filename, 'rb')
    _body=[]
    for line in f:
        try:
            _tag,_text = line.split("*")
            if _tag[:1]=="_":
                doc[_tag[1:]]=_text.rstrip()
            else:
                _text=remove_non_ascii(_text).rstrip()
                _body.append((_tag,_text))
        except Exception, e:
            print "ERROR:" + e.message + " " + line

    doc["start"] = _body

def _add_image(imagepath,outputtype="website"):
    if outputtype=="article":
        html_snippet="<img class=\"header-image\" src=\"" + path.join("articles",imagepath) + "\" " + " alt=\"\"/>"
    elif outputtype=="website":
        html_snippet="<img src=\"" + imagepath + "\" alt=\"\" />"
    elif outputtype=="docs":
        html_snippet="<img alt=\"image\" src=\"" + imagepath + "\" style=\"width:180px;height:auto;padding-top: 5pt;padding-bottom: 5pt;padding-left: 5pt;\"/>"
    return html_snippet+"\n"

def _add_video(video):
    html_snippet="<video width=\"180\" height=\"100\" controls><source src=\""+video+"\" type=\"video/mp4\"> </video>"
    return html_snippet+"\n"

def _add_buttontype(name):
    html_snippet="<td class=\"" + name + "\">"
    return html_snippet+"\n"

def _add_author(author):
    html_snippet="<td class=\"item\">" + author + "</td>"
    return html_snippet+"\n"

def _add_title(title,outputtype="webpage"):
    if outputtype=="docs":
        html_snippet="<p class=\"s8header\">"+title+"</p>"
    else:
        html_snippet="<td class=\"item_title\">" + title + "</td>"
    return html_snippet+"\n"

#def _add_sectionname(name):
#    html_snippet="<td class=\"item_section\">" + name + "</td>"
#    return html_snippet+"\n"

# content
#def _add_linkedinurl(url):
#    html_snippet="<a href=\"" + url + "\"></a>"
#    return html_snippet+"\n"

#def _add_articleurl(url):
#    html_snippet="<a href=\"" + url + "\" style=\"position:absolute; top:0; left:0; display:inline-block; width:210px; height:100px; z-index:5;\"></a>"
#    return html_snippet+"\n"

#def _add_docspath(docspath):
#    html_snippet="<a href=\"" + docspath + "\" style=\"position:absolute; top:0; left:0; display:inline-block; width:210px; height:100px; z-index:5;\"></a>"
#    return html_snippet+"\n"

def _add_content(content,article_name,hostname="www.veloxfintech.com",rendertype="website"):

    if rendertype=="website":
        if content=="default":
            content=path.join("articles",article_name)
        html_snippet="<a href=\"" + content + "\">" 

    elif rendertype=="snippet":
        if content=="default":
            content=path.join("http://",hostname,"articles",article_name)
        html_snippet="<a href=\"" + content + "\" style=\"position:absolute; top:0; left:0; display:inline-block; width:210px; height:100px; z-index:5;\">"

    elif rendertype=="docs":
        if content=="default":
            content=path.join("../articles",article_name,"index.php")
            html_snippet="<a href=\"" + content + "\" style=\"position:absolute; top:0; left:0; display:inline-block; width:210px; height:100px; z-index:5;\">"
        elif content.startswith("http://")==True or content.startswith("https://")==True:
            #html_snippet="<a href=\"" + content + "\">" 
            html_snippet="<a href=\"" + content + "\" style=\"position:absolute; top:0; left:0; display:inline-block; width:210px; height:100px; z-index:5;\">"
        else:
            _content=path.join("../articles",article_name,content)
            if path.splitext(_content)[1]==".mp4":
                html_snippet="<video width=\"180\" height=\"100\" controls><source src=\""+_content+"\" type=\"video/mp4\"> </video>"
            else:
                html_snippet="<a href=\"" + _content + "\" style=\"position:absolute; top:0; left:0; display:inline-block; width:210px; height:100px; z-index:5;\">"


    elif rendertype=="videos":
        html_snippet="<video width=\"180\" height=\"100\" controls><source src=\""+content+"\" type=\"video/mp4\"> </video>"

    elif rendertype=="news":
        html_snippet="<img alt=\"image\" src=\"" + content + "\" style=\"width:180px;height:auto;padding-top: 5pt;padding-bottom: 5pt;padding-left: 5pt;\"/>"

    elif rendertype=="articles":
        html_snippet="<img alt=\"image\" src=\"" + content + "\" style=\"width:180px;height:auto;padding-top: 5pt;padding-bottom: 5pt;padding-left: 5pt;\"/>"

    elif rendertype=="whitepaper":
        html_snippet="<a href=\"" + content + "\" style=\"position:absolute; top:0; left:0; display:inline-block; width:210px; height:100px; z-index:5;\"></a>"

    return html_snippet


# end of content

def _add_date(_date,eltype="div",cltype="date",outputtype="webpage"):
    if outputtype=="docs":
        html_snippet="<a class=\"celldate\">"+_date+"</a>" 
    else:
        html_snippet="<" + eltype + " class=\"" + cltype + "\">" + _date + "</" + eltype + ">"
    return html_snippet+"\n"

def _add_exert(_exert,outputtype="webpage"):
    if outputtype=="docs":
        html_snippet="<p class=\"cell\">" + _exert + "</p>"
    else:
        html_snippet="<p>" + _exert + "</p>"
    return html_snippet+"\n"

#def _add_folder(article_folder_path):
#    html_snippet="<img class=\"header-image\" src=\"" + article_folder_path + "\" alt=\"\">"
#    return html_snippet+"\n"

#def _add_article_folder(article_folder_path):
#    #html_snippet="<img class=\"header-image\" src=\"" + article_folder_path + "\" alt=\"\">"
#    html_snippet="<a href=\"" + article_folder_path + "\">"
#    return html_snippet+"\n"

#def _add_heading(heading):
#    html_snippet="<h3 class=\"headline\">" + heading +  "\"?</h3>"
#    return html_snippet+"\n"

def _add_tags(_tag_text,outputtype="webpage"):
    if outputtype=="docs":
        html_snippet="<a class=\"cellhashtag\">" + _tag_text + "</a>"
    else:
        html_snippet=""
        _tags = _tag_text.split("#")
        for _tag in _tags:
            html_snippet=html_snippet+"<strong>#"+_tag+"</strong>"

    return html_snippet+"\n"

def _add_start(_body):
    article_body=""
    _last_tag=""
    for _tag,_text in _body:
        if _last_tag!="":
            if _tag == "li" and _last_tag != "li":
                article_body=article_body+"<ul>\n"
            elif _tag != "li" and _last_tag == "li":
                article_body=article_body+"</ul>\n"

        article_body=article_body+"<"+_tag+">"+_text+"</"+_tag+">\n"
        _last_tag=_tag

    if _last_tag=="li":
         article_body=article_body+"</ul>\n"

    return article_body

def _get_article_template(filename):
    article=[]
    index={}
    f = open(filename, 'rb')
    linecount=1
    for line in f:
        line=line.rstrip()
        if line[:2]=="<<":
            line=line.replace(" ","")
            _tag=line[2:-2]
            index[_tag]=linecount
            article.append("")
        else:
            article.append(line)
        linecount=linecount+1
    return article,index


def _create_website_folder(folder_name,article_name,image_file):
    abspath_folder=path.join(folder_name,article_name)
    if path.isdir(abspath_folder)==False:
        mkdir(abspath_folder)

    abspath_file=path.join(abspath_folder,"index.php")
    if path.isfile(abspath_file)==True:
        remove(abspath_file)

    move("/tmp/article_template.html",abspath_file)
    copy(image_file,abspath_folder)

def _get_webpage():
    webpage=[]
    copy("/var/www/html/index.php","/tmp/index.php.copy")
    f = open("/tmp/index.php.copy", 'rb')
    _body=[]
    for line in f:
        webpage.append(line)
        #webpage.append(line.rstrip())
    f.close()
    return webpage

def _find_webpage_teaser_marker(webpage):
    #<!--VELOXTAGinsight_articles-->

    markers={}
    linecount=0
    for _line in webpage:
        if _line[4:12] == "VELOXTAG":
            _line=_line.rstrip()
            payload=_line[12:-3]
            values = payload.split(",")
            markers[values[0]]={"linenum":linecount,"values":values[1:]}
        linecount=linecount+1
    return markers

def _add_webpage_marker(webpage,tag,value,linenum):
    payload="<!--VELOXTAG"+tag,value+"-->\n\r"
    webpage.insert(linenum,payload)

def _upgrade_webpage(webpage,abspath_newpage):
    f = open(abspath_newpage,'w+')
    for _line in webpage:
        f.write(_line)
        #f.write(_line+"\n")
    f.close()

def _insert_teaser(webpage,linenumber,teaser):
    linenumber=linenumber+1
    f = open(teaser, 'rb')
    _body=[]
    for line in f:
        webpage.insert(linenumber,line)
        linenumber=linenumber+1
    f.close()

def _checked_filename(imagepath):
    for _path in _get_extensions(imagepath):
        if path.isfile(_path)==True:
            return _path
    return imagepath

def _get_extensions(image_file):
    _bname=path.splitext(image_file)[0]
    return([image_file,_bname+".png",_bname+".svg",_bname+".pdf"])

def _copy_file(input_folder,output_folder,filename="Final_Website.png",skipmp4=False):

    if path.splitext(filename)[1] == ".mp4" and skipmp4==True:
        print "skipping mp4's : " + filename
    elif filename.startswith("http://")==True or filename.startswith("https://")==True:
        print "skipping as its a url :" + filename
    else:
        if filename not in ["NONE","default"]:
            input_file=path.join(input_folder,filename)

            _checkedfilename=_checked_filename(input_file)
            if _checkedfilename != -1:
                try:
                    copy(_checkedfilename,output_folder)
                except:
                    print "ERROR : cannot copy file [" + _checkedfilename + "]"
            else:
                print "ERROR : no image file present [" + ",".join(_get_extensions(input_file)) + "]"

def _copy_artefacts(artefacts,doc,input_folder_path,folder_path,skipmp4=False):
    for i in range(0,len(artefacts)):
        if doc.has_key(artefacts[i])==True :
            _copy_file(input_folder_path,folder_path,doc[artefacts[i]],skipmp4)

def _beautifyhtml(filename):
    with open(filename) as fp:
        soup = bs(fp, 'html.parser')

    return(soup.prettify())

def _get_inclusion_file(filename):
    _dict={"latest":[],"regular":[],"more":[]}
    with open(filename,"r") as fp:
        for line in fp:
            key,value,visibility,latest=line.rstrip().split(",")
            if _dict.has_key(value) == False:
                _dict[value]=[key]
            else:
                _dict[value].append(key)
            if visibility!="None":
                _dict[visibility].append(key)
            if latest=="True":
                _dict["latest"].append(key)
    return _dict


if __name__ == "__main__":

    print _beautifyhtml("/var/www/html/index.php")


