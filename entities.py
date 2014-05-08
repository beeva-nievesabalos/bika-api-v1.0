#!flask/bin/python
import json
import ast
from flask import Flask, request, url_for, render_template, jsonify, Response
import nltk
import nltk.data
import re
import dateutil
import datetime
import calendar
from dateutil.parser import *
from datetime import *


app = Flask(__name__)

def tokenize(text):              # TOKENIZED! 
  sentences = nltk.sent_tokenize(text)    
  tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
  return tokenized_sentences

def tag(tokenized_sentences):     # TAGGED!    
  # etiqueto sintácticamente los tokens (aún con stopwords)
  #print(tokenized_sentences)
  tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
  return tagged_sentences

def chunk(tagged_sentences):      # CHUNKED!    -  NER: 
  # binary=True para que solo utilice NE en vez de la categoria 
  #print(tagged_sentences)   
  chunked_sentences = nltk.batch_ne_chunk(tagged_sentences)
  return chunked_sentences

def traverse(t): 
   entidades = []
   try: 
     t.label() 
   except AttributeError: 
     do = None
   else: 
     if t.label() == 'PERSON': 
        string = "{'name': '" + " ".join(leaf[0] for leaf in t.leaves()) + "'},"
        entidades.append(string)
        #if t.leaves() == 2:
        #  string = "'name': '" + str(t.leaves()[0][0]) + "',"
        #  string2 = "'familyName': '" + str(t.leaves()[1][0]) + "', "
        #  entidades.append(string + string2)
     if t.label() == 'GPE': 
        string = "{'addressLocality':'" + " ".join(leaf[0] for leaf in t.leaves()) +"'},"
        entidades.append(string) 
     if t.label() == 'LOCATION': 
        string = "{'location':'" + " ".join(leaf[0] for leaf in t.leaves()) +"'},"
        entidades.append(string)
     if t.label() == 'ORGANIZATION':
        string = "{'affiliation': '" + " ".join(leaf[0] for leaf in t.leaves())  + "'},"
        entidades.append(string) 
     if t.label() == 'DURATION':
        string = "{'duration': '" + " ".join(leaf[0] for leaf in t.leaves())  + "'},"
        entidades.append(string)
     if t.label() == 'DATE': 
        string = "{'date': '" + " ".join(leaf[0] for leaf in t.leaves())  + "'},"
        entidades.append(string)
     if t.label() == 'CARDINAL': 
        string = "{'cardinalNumber': '" + " ".join(leaf[0] for leaf in t.leaves())  + "'},"
        entidades.append(string) 
     if t.label() == 'PERCENT': 
        string = "{'percentNumber': '" + " ".join(leaf[0] for leaf in t.leaves())  + "'},"
        entidades.append(string)
     if t.label() == 'MONEY':
        string = "{'money': '" + " ".join(leaf[0] for leaf in t.leaves())  + "'},"
        entidades.append(string) 
     if t.label() == 'MEASURE':
        string = "{'measure': '" + " ".join(leaf[0] for leaf in t.leaves())  + "'}," 
        entidades.append(string)
     if t.label() == 'FACILITY': 
        string = "{'facility': '" + " ".join(leaf[0] for leaf in t.leaves())  + "'},"
        entidades.append(string)
     else: 
       for child in t:  
         devuelve = traverse(child)
         if  devuelve == None: do = None
         else: 
           string = ''.join(devuelve)
           entidades.append(string) 

     return entidades

def extract_entities(chunked_sentences):
  list_ent=[]

  for tree in chunked_sentences:
    devuelve = traverse(tree)
    if  devuelve == None: do = None
    else: 
       string = ''.join(devuelve)
       list_ent.append(string) 
  
  str_list_ent = ''.join(list_ent)
  return str_list_ent

def extract_address(text):
  list_address = []
  matchlist = re.findall(r'\d{1,5}\s\w.\s(\b\w*\b\s){1,2}\w*\.', text) 
  
  for match in matchlist:
    list_address.append("{'address': '"+ str(match) +"'},")

  str_list_address = ' '.join(list_address)
  return str_list_address 

def extract_phones(text):
  list_phones = []

  text = text.replace(' ', '')
  matchlist = re.findall(r'\d{9}', text)  #|[0-9]{3} [0-9]{3} [0-9]{3}|[0-9]{2} [0-9]{3} [0-9]{2} [0-9]{2}

  for match in matchlist:
    list_phones.append("{'telephone': '"+ str(match) +"'},")

  str_list_phones = ' '.join(list_phones)
  return str_list_phones 

def extract_email(text):
  list_emails=[]
  matchlist = re.findall(r"[0-9A-Za-z._-]+\@[0-9A-Za-z._-]+", text)

  for match in matchlist:
    list_emails.append("{'email': '"+match+"'},")

  str_list_emails = ' '.join(list_emails)
  return str_list_emails

def extract_dates(text):
  list_dates=[]

  matchlist = re.findall(r'\d{4}-\d{2}-\d{2}|\s\d{4}\s|\d{2}-\d{2}-\d{4}|\d{4}/\d{2}/\d{2}|\d{2}/\d{2}/\d{4}', text)
  months = "|".join(calendar.month_name)[1:]
  monthsmatches = re.findall("{0}\s\d+\s\-\s{0}\s\d+".format(months), text)
  if monthsmatches: 
    str_months = ''.join(monthsmatches)
    list_dates.append("{'month': '" + str_months +"'},")

  days = "|".join(calendar.day_name)[0:]
  daysmatches = re.findall("{0}\s".format(days), text)
  if daysmatches: 
    str_days = ''.join(daysmatches)
    list_dates.append("{'weekday': '" + str_days +"'},")

  for match in matchlist:
    if re.match(r'\d{4}-\d{2}-\d{2}', match):
      date = datetime.strptime(match, '%Y-%m-%d')
      list_dates.append("{'birthDate': '"+date.strftime("%d/%m/%y")+"'},")
    else: 
      if re.match(r'\s\d{4}\s', match):
        match = match.strip()
        date = datetime.strptime(match, '%Y')
        list_dates.append("{'year': '"+date.strftime("%Y")+"'},")
      else: 
        if re.match(r'\d{2}-\d{2}-\d{4}', match):
          date = datetime.strptime(match, '%d-%m-%Y')
          list_dates.append("{'birthDate': '"+date.strftime("%d/%m/%y")+"'},")
        else:
           if re.match(r'\d{4}/\d{2}/\d{2}', match):
             date = datetime.strptime(match, '%Y/%m/%d')
             list_dates.append("{'birthDate': '"+date.strftime("%d/%m/%y")+"'},")
           else:
              if re.match(r'\d{2}/\d{2}/\d{4}', match):
                 date = datetime.strptime(match, '%d/%m/%Y')
                 list_dates.append("{'birthDate': '"+date.strftime("%d/%m/%y")+"'},")

  str_list_dates = ''.join(list_dates)
  return str_list_dates

def api_entities(text, flag_json):
 
  token = tokenize(text)
  tags = tag(token)
  chunks = chunk(tags)
  #VIP
  entities = extract_entities(chunks)
  entitiesstring = "[" + ''.join(entities[:-1]) + "]"
  entitiesarrayjson = ast.literal_eval(entitiesstring)

  if flag_json:  #json
    resultado = jsonify({'entities_list': entitiesarrayjson})
  else: #string
    resultado = json.dumps({'entities_list': entitiesarrayjson})
  
  return resultado

def api_dates(text, flag_json):
 
  dates = extract_dates(text)
  datesstring = "[" + ''.join(dates[:-1]) + "]"
  datesarrayjson = ast.literal_eval(datesstring) 

  if flag_json:  #json
    resultado = jsonify({'dates_list': datesarrayjson})
  else: #string
    resultado = json.dumps({'dates_list': datesarrayjson})
  
  return resultado

def api_emails(text, flag_json):
 
  emails = extract_email(text)
  emailsstring = "[" + ''.join(emails[:-1]) + "]"
  emailsarrayjson = ast.literal_eval(emailsstring)  

  if flag_json:  #json
    resultado = jsonify({'emails_list': emailsarrayjson})
  else: #string
    resultado = json.dumps({'emails_list': emailsarrayjson})
  
  return resultado

def api_phones(text, flag_json):
  
  phones = extract_phones(text)
  phonesstring = "[" + ''.join(phones[:-1]) + "]"
  phonesarrayjson = ast.literal_eval(phonesstring)  

  if flag_json:  #json
    resultado = jsonify({'phones_list': phonesarrayjson})
  else: #string
    resultado = json.dumps({'phones_list': phonesarrayjson})
  
  return resultado

#flag_json = 1 (json) = 0 (string)
def show_the_entities(text, flag_json):
 
  token = tokenize(text)
  tags = tag(token)
  chunks = chunk(tags)
  #VIP
  entities = extract_entities(chunks)
  entitiesstring = "[" + ''.join(entities[:-1]) + "]"
  entitiesarrayjson = ast.literal_eval(entitiesstring)

  dates = extract_dates(text)
  datesstring = "[" + ''.join(dates[:-1]) + "]"
  datesarrayjson = ast.literal_eval(datesstring) 

  emails = extract_email(text)
  emailsstring = "[" + ''.join(emails[:-1]) + "]"
  emailsarrayjson = ast.literal_eval(emailsstring)  
  
  phones = extract_phones(text)
  phonesstring = "[" + ''.join(phones[:-1]) + "]"
  phonesarrayjson = ast.literal_eval(phonesstring)  

  address = extract_address(text)
  addressstring = "[" + ''.join(address[:-1]) + "]"
  addressarrayjson = ast.literal_eval(addressstring)
  
  if flag_json:  #json
    resultado = jsonify({'entities_list': entitiesarrayjson, 'dates_list': datesarrayjson, 'emails_list': emailsarrayjson, 'phones_list': phonesarrayjson, 'address_list': addressarrayjson})
  else: #string
    resultado = json.dumps({'entities_list': entitiesarrayjson, 'dates_list': datesarrayjson, 'emails_list': emailsarrayjson, 'phones_list': phonesarrayjson, 'address_list': addressarrayjson})
  
  return resultado


def api_address(text):
  
  address = extract_address(text)
  addressstring = "[" + ''.join(address[:-1]) + "]"
  addressarrayjson = ast.literal_eval(addressstring)

  json_response = jsonify({'address_list': phonesarrayjson})

  return json_response

#---------------------- ROUTES --------------------------
@app.route('/')
def index():
  #return 'BIKA (BEEVA Information & Knowledge Assistant)'
  return render_template('apibika.html')

@app.route('/bika', methods=['GET', 'POST'])
def bika():
  #'POST' ya que viene de un formulario
  if request.method == 'POST':
    if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
      print("\n-------- request POST form['text'] -------")
      print(request.form['text'])
      text = str(request.form['text'])
      response = show_the_entities(text, 1) # devuelve json

      #### para evitar CORS ######
      response.headers.add_header('Access-Control-Allow-Origin', '*')
      response.headers['Content-Type'] = 'application/json'
      response.status_code = 200
      print("\n-------- JSON response -------")
      print(response)
      print("\n")

      return response
  #'GET' permite CORS usando JSONP
  if request.method == 'GET':
      print("\n-------- request GET request.args.get('....') -------")
      print("CALLBACK =" + request.args.get('callback'))
      print("TEXT =" + request.args.get('text'))
      idcallback = str(request.args.get('callback'))
      text = str(request.args.get('text'))
      json_string = show_the_entities(text, 0) #devuelve string

      respuesta = Response(idcallback + "("+ json_string + ");")
      print("\n-------- JSON response -------")
      print(respuesta)
      print("\n")
      
      return respuesta
  else:
    text = "My name is John Clark and I'm 28. I'm a lawyer. I was born the 1972-06-26 in  Madrid, Spain. I live in calle orujo, 4, 23700, Linares, Spain. In case emergency, Monday and Sunday, please contact with my wife Morgan Clark, she was born on 21/03/1975. You can contact me by e-mail at jdclark@email.com. My phone number is 213 555 776 and home phonenumber is 666777897 and 91 234 56 78. I work at BBVA, ERICSSON and GE."
   # error = 'use POST with a form(text)'
    info = show_the_entities(text)
    error = info.response
    print(info)
    print(info.response)
    return render_template('bika.html', information=error)

@app.route('/entities', methods=['GET', 'POST'])
def obtain_entities():
  #'POST' ya que viene de un formulario
  if request.method == 'POST':
    if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
      print("\n-------- request POST form['text'] -------")
      print(request.form['text'])
      text = str(request.form['text'])
      response = api_entities(text, 1) # devuelve json

      #### para evitar CORS ######
      response.headers.add_header('Access-Control-Allow-Origin', '*')
      response.headers['Content-Type'] = 'application/json'
      response.status_code = 200
      print("\n-------- JSON response -------")
      print(response)
      print("\n")

      return response
  #'GET' permite CORS usando JSONP
  if request.method == 'GET':
      print("\n-------- request GET request.args.get('....') -------")
      print("CALLBACK =" + request.args.get('callback'))
      print("TEXT =" + request.args.get('text'))
      idcallback = str(request.args.get('callback'))
      text = str(request.args.get('text'))
      json_string = api_entities(text, 0) #devuelve string

      respuesta = Response(idcallback + "("+ json_string + ");")
      print("\n-------- JSON response -------")
      print(respuesta)
      print("\n")
      
      return respuesta

@app.route('/dates', methods=['GET', 'POST'])
def obtain_dates():
  #'POST' ya que viene de un formulario
  if request.method == 'POST':
    if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
      print("\n-------- request POST form['text'] -------")
      print(request.form['text'])
      text = str(request.form['text'])
      response = api_dates(text, 1) # devuelve json

      #### para evitar CORS ######
      response.headers.add_header('Access-Control-Allow-Origin', '*')
      response.headers['Content-Type'] = 'application/json'
      response.status_code = 200
      print("\n-------- JSON response -------")
      print(response)
      print("\n")

      return response
  #'GET' permite CORS usando JSONP
  if request.method == 'GET':
      print("\n-------- request GET request.args.get('....') -------")
      print("CALLBACK =" + request.args.get('callback'))
      print("TEXT =" + request.args.get('text'))
      idcallback = str(request.args.get('callback'))
      text = str(request.args.get('text'))
      json_string = api_dates(text, 0) #devuelve string

      respuesta = Response(idcallback + "("+ json_string + ");")
      print("\n-------- JSON response -------")
      print(respuesta)
      print("\n")
      
      return respuesta

@app.route('/telephones', methods=['GET', 'POST'])
def obtain_phones():
  #'POST' ya que viene de un formulario
  if request.method == 'POST':
    if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
      print("\n-------- request POST form['text'] -------")
      print(request.form['text'])
      text = str(request.form['text'])
      response = api_phones(text, 1) # devuelve json

      #### para evitar CORS ######
      response.headers.add_header('Access-Control-Allow-Origin', '*')
      response.headers['Content-Type'] = 'application/json'
      response.status_code = 200
      print("\n-------- JSON response -------")
      print(response)
      print("\n")

      return response
  #'GET' permite CORS usando JSONP
  if request.method == 'GET':
      print("\n-------- request GET request.args.get('....') -------")
      print("CALLBACK =" + request.args.get('callback'))
      print("TEXT =" + request.args.get('text'))
      idcallback = str(request.args.get('callback'))
      text = str(request.args.get('text'))
      json_string = api_phones(text, 0) #devuelve string

      respuesta = Response(idcallback + "("+ json_string + ");")
      print("\n-------- JSON response -------")
      print(respuesta)
      print("\n")
      
      return respuesta

@app.route('/emails', methods=['GET', 'POST'])
def obtain_emails():
  #'POST' ya que viene de un formulario
  if request.method == 'POST':
    if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
      print("\n-------- request POST form['text'] -------")
      print(request.form['text'])
      text = str(request.form['text'])
      response = api_emails(text, 1) # devuelve json

      #### para evitar CORS ######
      response.headers.add_header('Access-Control-Allow-Origin', '*')
      response.headers['Content-Type'] = 'application/json'
      response.status_code = 200
      print("\n-------- JSON response -------")
      print(response)
      print("\n")

      return response
  #'GET' permite CORS usando JSONP
  if request.method == 'GET':
      print("\n-------- request GET request.args.get('....') -------")
      print("CALLBACK =" + request.args.get('callback'))
      print("TEXT =" + request.args.get('text'))
      idcallback = str(request.args.get('callback'))
      text = str(request.args.get('text'))
      json_string = api_emails(text, 0) #devuelve string

      respuesta = Response(idcallback + "("+ json_string + ");")
      print("\n-------- JSON response -------")
      print(respuesta)
      print("\n")
      
      return respuesta      
 
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
