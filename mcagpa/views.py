from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import FilesUpload
import webbrowser, os
import json
import boto3
import io
from io import BytesIO
import sys
from pprint import pprint
# Create your views here.

pageDet = {
        'author':'Kalai chelvan kn & Aravindhan',
        'title':'(Ce[G)pa]{Mca}',
        'date_posted':'27 Sep 2020'
}


context = {
            'pageDet':pageDet
        }

def home(request):
    if request.method == "POST":
        post_id = request.POST.get('post_id')
        context['postres'] = 'image got'
        # return JsonResponse(context)
        return render(request, 'mcagpa/home.html',context)
    else:
        return render(request, 'mcagpa/home.html',context)
    # return HttpResponse('<h1> This is the mcagpa home page</h1>')


def sampleresponse():
    ts = ['a321','b121','132c']
    t1 = ['aaadfss','sdfsfb','r23c']
    res = []
    res.append(ts)
    res.append(t1)
    res.append(t1)
    res.append(t1)
    return res

def fetchResult(request):
    if request.method == "POST":
        # postobj = Post.objects.get(id=post_id)
        tfile = request.FILES["img"]
        document = FilesUpload.objects.create(file = tfile)
        document.save()
        imageurl = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'+document.file.url
        boo,tabdata,gpa = maincode(imageurl)
        os.remove(imageurl)
        document.delete()
        # context['tabdata'] = gethtmltable(sampleresponse())
        if boo:
            context['gpastatus'] = "successfully calculated"
            context['gpa'] = str(gpa)
            context['tabdata'] = gethtmltable(tabdata)
        else:
            context['gpa'] = '-1'
            context['gpastatus'] = gpa
            context['tabdata'] = "Nill"
        return JsonResponse(context)

def gethtmltable(tabdata):
    th = ''
    for x in tabdata[0]:
        th += '<th>'+x+'</th>'
    tablehead = '<thead><tr>'+th+'</tr></thead>'
    tablebody = '<tbody>'
    for x in tabdata[1:]:
        td = ''
        for y in x:
            td += '<td>'+str(y)+'</td>'
        tablebody += '<tr>'+td+'</tr>'
    tablebody += '</tbody>'
    tablecaption = '<caption> Semester result </caption>'
    htmltable = '<div class="table-responsive-sm"><table class="table table-striped">'+tablecaption+tablehead+tablebody+'</table></div>'
    return htmltable

def details(request):
    return render(request, 'mcagpa/details.html',context)


# textract code

def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        # create new row
                        rows[row_index] = {}
                    # get the text value
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows


def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] =='SELECTED':
                            text +=  'X '
    return text


def get_table_csv_results(file_name):
    try:
        with open(file_name, 'rb') as file:
            img_test = file.read()
            bytes_test = bytearray(img_test)
            print('Image loaded', file_name)

        # process using image bytes
        # get the results
        client = boto3.client('textract')

        response = client.analyze_document(Document={'Bytes': bytes_test}, FeatureTypes=['TABLES'])

        # Get the text blocks
        blocks=response['Blocks']
        # pprint(blocks)

        blocks_map = {}
        table_blocks = []
        for block in blocks:
            blocks_map[block['Id']] = block
            if block['BlockType'] == "TABLE":
                table_blocks.append(block)

        if len(table_blocks) <= 0:
            return "<b> NO Table FOUND </b>"

        # driver code csv record
        csv = ''
        for index, table in enumerate(table_blocks):
            tcsv,mp = generate_table_csv(table, blocks_map, index +1)
            csv +=tcsv
            csv += '\n\n'
        return csv,mp
    except:
        return None,None
        pass
def generate_table_csv(table_result, blocks_map, table_index):
    rows = get_rows_columns_map(table_result, blocks_map)
    table_id = 'Table_' + str(table_index)

    mp = {}
    # get cells.
    csv = 'Table: {0}\n\n'.format(table_id)
    for row_index, cols in rows.items():
        for col_index, text in cols.items():
            csv += '{}'.format(text) + ","
            if row_index in mp.keys():
                mp[row_index].append(format(text))
            else:
                mp[row_index] = [format(text)]
        csv += '\n'
    csv += '\n\n\n'
    # print(mp)
    return csv,mp

def getcegcredits():
    ''' get all the credits offered for all the subjects of entire MCA course fn'''
    mp = {'MA7104': ['Mathematical Foundations of Computer Science', '4'], 'CA7104': ['Problem Solving and C Programming', '3'], 'CA7103': ['Database Management Systems', '3'], 'CA7102': ['Data Structures', '3'], 'CA7101': ['Computer Organization and Design', '3'], 'CA7111': ['Data Structures and Programming Laboratory', '2'], 'CA7112': ['Database Management Systems Laboratory', '2'], 'CA7201': ['Computer Communication and Networks', '4'], 'CA7204': ['Operating System Concepts', '3'], 'CA7205': ['Software Engineering Methodologies', '3'], 'CA7202': ['Design and Analysis of Algorithms', '3'], 'CA7203': ['Object Oriented Programming Paradigm', '3'], 'CA7211': ['OOP and Algorithms Laboratory', '2'], 'CA7212': ['OS and Network Programming Laboratory', '2'], 'CA7302': ['Embedded Systems', '3'], 'CA7301': ['Data Warehousing and Mining', '3'], 'CA7303': ['Object Oriented Analysis and Design', '3'], 'CA7304': ['Web Programming', '3'], 'CA7313': ['Web Programming Laboratory', '2'], 'CA7311': ['Case Tools Laboratory', '2'], 'CA7312': ['Soft Skills Development Lab', '1'], 'CA7401': ['Advanced Java Programming', '4'], 'IF7451': ['Unix Internals', '3'], 'CA7402': ['Mobile Computing', '3'], 'CA7411': ['Advanced Java Programming Laboratory', '2'], 'CA7412': ['Mobile Application Development Laboratory', '2'], 'CA7413': ['Technical Seminar and Report Writing', '1'], 'CA7503': ['Software Testing', '3'], 'CA7502': ['Distributed and Cloud Computing', '3'], 'CA7501': ['Cryptography and Network Security', '3'], 'CA7513': ['Software Testing Laboratory', '2'], 'CA7511': ['Cloud Computing and Security Laboratory', '2'], 'CA7512': ['Report Writing Practice Laboratory', '1'], 'CA7005': ['Distributed Systems', '3'], 'CA7014': ['High Speed Networks', '3'], 'CA7025': ['TCP/IP Design and Implementation', '3'], 'CA7001': ['Computer Graphics and Animation', '3'], 'CA7003': ['Database Tuning', '3'], 'CA7023': ['Software Quality Management', '3'], 'CA7022': ['Real Time Systems', '3'], 'CA7009': ['Fundamental of Digital Image Processing', '3'], 'CA7026': ['User Interface Design', '3'], 'CA7012': ['Grid Computing', '3'], 'CA7018': ['Internet of Things', '3'], 'CA7028': ['XML and Web Services', '3'], 'CA7011': ['Geographical Information Systems', '3'], 'CA7013': ['Healthcare Information Systems', '3'], 'CA7006': ['E-Learning Techniques', '3'], 'IF7076': ['Operations Research', '3'], 'CA7007': ['Enterprise Resource Planning', '3'], 'CA7020': ['Multimedia', '3'], 'CA7016': ['Information Management System', '3'], 'CA7019': ['M-Commerce', '3'], 'CA7024': ['Software Reliability and Metrics', '3'], 'MM7072': ['Visualisation Techniques', '3'], 'IF7071': ['Bio Informatics', '3'], 'CA7017': ['Intelligent Data Analysis', '3'], 'CA7008': ['Financial Accounting and Management', '3'], 'CA7015': ['Human Resources Management', '3'], 'CA7002': ['Customer Relationship Management', '3'], 'CA7027': ['Virtualization Techniques', '3'], 'CA7010': ['Game Programming', '3'], 'CA7021': ['Professional Practice and Ethics', '3'], 'CA7004': ['Development Frameworks and Virtual Machines', '3'], 'IF7077': ['Service Oriented Architecture', '3'], 'CA7611': ['Project Work', '12'], 'MA5102': ['Mathematical Foundations of Computer Science', '4'], 'CA5101': ['Digital Logic and Computer Organization', '3'], 'CA5102': ['Problem Solving using Python', '3'], 'CA5103': ['Database Management Systems', '3'], 'CA5111': ['Programming in Python Laboratory', '2'], 'CA5112': ['Database Management Systems Laboratory', '2'], 'CA5201': ['C Programming and Data Structures', '3'], 'CA5202': ['Operating Systems', '4'], 'CA5203': ['Software Engineering', '3'], 'CA5204': ['Advances in Databases', '4'], 'CA5205': ['Web Programming', '3'], 'CA5211': ['C Programming and Data Structures Laboratory', '2'], 'CA5212': ['Web Programming Laboratory', '2'], 'CA5301': ['Computer Communication and Networks', '4'], 'CA5302': ['Java Programming', '3'], 'CA5303': ['Advanced Data Structures and Algorithm Design', '3'], 'CA5311': ['Java Programming and Networks Laboratory', '2'], 'CA5312': ['Advance Data Structures and Algorithm Laboratory', '2'], 'CA5401': ['Data Science', '3'], 'CA5402': ['Embedded Systems and Internet of Things', '3'], 'CA5403': ['Cloud Computing', '3'], 'CA5411': ['Data Science Laboratory', '2'], 'CA5412': ['Internet of Things and Cloud Laboratory', '2'], 'CA5413': ['System Development Laboratory', '1'], 'CA5502': ['Information Security', '3'], 'CA5501': ['Mobile Application Development Techniques', '3'], 'CA5511': ['Mobile Application Development Techniques Laboratory', '2'], 'CA5512': ['Software Development Laboratory', '2'], 'CA5001': ['Blockchain Technologies', '3'], 'CA5002': ['Ethical Hacking', '3'], 'CA5003': ['Big Data with R', '3'], 'CA5004': ['Full Stack Development', '3'], 'CA5005': ['Introduction to Machine Learning', '3'], 'CA5006': ['Autonomous Ground Vehicle Systems', '3'], 'CA5007': ['E-Learning Techniques', '3'], 'CA5008': ['Software Testing', '3'], 'CA5009': ['Deep Learning Techniques and Applications', '3'], 'CA5010': ['Game Programming Techniques', '3'], 'CA5011': ['Multimedia Technologies', '3'], 'CA5012': ['Data Visualization Techniques', '3'], 'CA5013': ['UNIX Internals', '3'], 'CA5014': ['C# and .NET Programming', '3'], 'CA5015': ['Service Oriented Architectures', '3'], 'CA5016': ['Software Project Management', '3'], 'CA5017': ['Mixed Reality', '3'], 'CA5018': ['Digital Image Processing and Applications', '3'], 'CA5019': ['Text Mining Techniques', '3'], 'CA5020': ['Data Warehousing and Data Mining Techniques', '3'], 'CA5021': ['Software Quality Assurance', '3'], 'CA5022': ['Introduction to Social Network Analysis', '3'], 'CA5023': ['IoT Based Smart Systems', '3'], 'CA5024': ['Object Oriented Analysis and Design', '3'], 'CA5025': ['Artificial Intelligence', '3'], 'CA5026': ['Computer Graphics', '3'], 'CA5027': ['Human Computer Interaction', '3'], 'CA5028': ['Wireless Sensor Networks & Protocols', '3'], 'CA5029': ['Next Generation Networks', '3'], 'CA5030': ['Cybernetics', '3'], 'CA5031': ['Network Programming and Management', '3'], 'CA5032': ['Semantic Web and Applications', '3'], 'CA5033': ['Soft Computing', '3'], 'RM5151': ['Research Methodology and IPR', '2'], 'OE5091': ['Business Data Analytics', '3'], 'OE5092': ['Industrial Safety', '3'], 'OE5093': ['Operational Research', '3'], 'OE5094': ['Cost Management of Engineering Projects', '3'], 'OE5095': ['Composite Materials', '3'], 'OE5096': ['Waste to Energy', '3'], 'AX5091': ['English for Research Paper Writing', '0'], 'AX5092': ['Disaster Management', '0'], 'AX5093': ['Sanskrit for Technical Knowledge', '0'], 'AX5094': ['Value Education', '0'], 'AX5095': ['Constitution of India', '0'], 'AX5096': ['Pedagogy Studies', '0'], 'AX5097': ['Stress Management by Yoga', '0'], 'AX5098': ['Personality Development Through Life Enlightenment Skills', '0'], 'AX5099': ['Unnat Bharat Abhiyan', '0'], 'CA5313': ['Socially Relevant Project', '1'], 'CA5513': ['Summer Internship', '1'], 'CA5611': ['Project Work', '12']}
    return mp

def preprocessing(mp):
    ''' Data Preprocessing fn
            - Removes pre and suf spaces
            - convert invalid grades to valid grades
    '''
    res = {}
    for x in mp.keys():
        tlist = mp[x]
        for ind,ele in enumerate(tlist):
            ele = ele.strip()
            tlist[ind] = ele
        res[x]= tlist
    # print(res)
    return res


def getcredit(s):
    grade_map = {"O" : 10, "A+" : 9, "A" : 8, "B+" : 7, "B" : 6, "RA":0}
    return grade_map[s]

def computeGPA(grades, credits):
    agg = 0
    if(len(grades) == len(credits)):
        agg = sum([getcredit(grades[i])*credits[i] for i in range(len(grades))])
        return agg/sum(credits)
    else:
        return -1

def cleangrade(s):
    grades = {'B':'B', 'B+':'B+', 'A':'A', 'A+':'A+', 'O':'O', 'o':'O','At':'A+','0':'O','Bt':'B+','RA':'RA'}
    if s in grades.keys():
        return grades[s]
    else:
        return 'RA'

def getgrades(prepro,allsubjects):
    ''' gets course code and grade from aws,  finds subject exists, then maps with the credits  '''
    tklist = prepro[1]
    indccode = tklist.index('Course Code')
    indgrade = tklist.index('Grade')
    if indccode==-1 or indgrade==-1:
        return None,None,None,None
    del prepro[1]
    resultgrades = []
    resultcredits = []
    resultname = []
    resultccode = []
    for x in prepro.keys():
        tlist = prepro[x]
        resultccode.append(tlist[indccode])
        if resultccode[-1] in allsubjects.keys():
            tname,tcredit = allsubjects[tlist[indccode]]
        else:
            tname,tcredit = 'unknown','0'
        tgrade = cleangrade(tlist[indgrade])
        resultcredits.append(int(tcredit))
        resultgrades.append(tgrade)
        resultname.append(tname)
    return resultcredits,resultgrades,resultname,resultccode

def validateinput(templist,option):
    # print(templist,option)
    if option=="credits":
        # print('credits')
        cds = [0,1,2,3,4,12]
        for x in templist:
            if x not in cds:
                print(x)
                return False
        return True
    elif option=="ccode":
        # print('ccode')
        allsubs = getcegcredits()
        for x in templist:
            if x not in allsubs.keys():
                print(x)
                return False
            return True
    return False

def printresult(resultcredits,resultgrades,resultname,resultccode,gpa):
    table = []
    table.append(['Sl.No.','Course Code','Course Name','Grades Obtained','Max Credits'])
    for i in range(len(resultccode)):
        table.append([i+1,resultccode[i],resultname[i],resultgrades[i],resultcredits[i]])
    print("\nGPA obtained is ",gpa,"\n")
    tabdata = printer(table)
    return table,gpa


def printer(matrix):
    print()
    s = [[str(e) for e in row] for row in matrix]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))
    return table
    # print()

def printawsrawData(mp):
    print("------Data from aws server ==> Textract ----------")
    for x in mp.keys():
        print(mp[x])
    print("--------------------------------------------------")


def maincode(file_name):
    tabdata = None
    try:
        table_csv,mp = get_table_csv_results(file_name)
        if table_csv==None or mp==None:
            print("Invalid Image....")
            tabdata,gpa = None,'-1'
            return False,tabdata,"Not able to process the Image/Try with proper image with course code and grades"
        if len(mp)<5:
            print("Invalid data....")
            tabdata,gpa = None,'-1'
            return False,tabdata,"Recognized Subject count less than 5"
        printawsrawData(mp)
        prepro = preprocessing(mp)
        allsubjects = getcegcredits()
        resultcredits,resultgrades,resultname,resultccode = getgrades(prepro,allsubjects)

        if resultccode==None or resultcredits==None or resultgrades==None or resultname==None:
            print("Invalid data....")
            tabdata,gpa = None,'-1'
            return False,tabdata,"Column Name Course Code or Grade is not Found!!!"

        if validateinput(resultccode,'ccode') and validateinput(resultcredits,'credits'):
            print('valid data')
            gpa = computeGPA(resultgrades,resultcredits)
            tabdata,gpa = printresult(resultcredits,resultgrades,resultname,resultccode,gpa)
            return True,tabdata,gpa
        else:
            print("Invalid data....")
            tabdata,gpa = printresult(resultcredits,resultgrades,resultname,resultccode,'Nill')
            return False,tabdata,"gpa cannot be calculated due to data error"
        print("process finished")
    except:
        return False,tabdata,"Not able to process the Image/Try with proper image with course code and grades"
        pass