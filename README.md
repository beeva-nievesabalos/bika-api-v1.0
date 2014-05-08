BIKA API                             v1.0
BEEVA Information and Knowledge Assistant
=============
**English version**
http://54.195.222.159:5000/ 


**1. Date extraction**
Using regular expressions. 
Dates as follows:
1) Names of months >> ‘month’
2) Names of weekdays >> ‘weekday’
3) Dates as YYYY-mm-dd or YYYY/mm/dd (e.g.: 1985-03-21) and dd-mm-YYYY or dd/mm/YYYY (e.g.:
21-03-1985) >> ‘birthDate’
4) Year format YYYY >> ‘year’

Methods: GET, POST
Response: JSON array
"dates_list": [{
"weekday": "Monday"
}, {
"birthDate": "26/06/72"
}, {
"birthDate": "21/03/75"
}]



**2.Email address extraction**
Using regular expressions.

Methods: GET, POST
Response: JSON array
"emails_list": [{
"email": "jdclark@email.com."
}]

**Telephone extraction**
Using regular expressions.

Methods: GET, POST
Response: JSON array
"phones_list": [{
"telephone": "213555776"
}, {
"telephone": "666777897"
}, {
"telephone": "912345678"
}]
16/12/2013

**Entity extraction**
Using NLTK NER (Named Entity Recognition):
1) Person: Name + Surname (e.g.: John Clark, President Obama) >> ‘name’
2) Geo-political entities (e.g.: South East Asia, Palo Alto, California) >> ‘addressLocality’
3) Location (e.g.: Mount Everest, Mississippi River) >> ‘location’ (toma Mississippi River como ‘affiliation’)
4) Organization (e.g.: BBVA) >> ‘affiliation’
5) Duration (e.g.: ?) >> ‘duration’
6) Date (e.g.: June) >> ‘date’ (no extraída así)
7) Cardinal (e.g.: ?) >> ‘cardinalNumber’ (no los extrae)
8) Percent (e.g.: 18.75 %) >> ‘percentNumber’ (no los extrae)
9) Money (e.g.: GBP 10.40) >> ‘money’ (toma GBP como ‘affiliation’)
10) Measure (e.g.: ? ) >> ‘measure’ (no los extrae)
11) Facility: Human-made artifacts in the domains of architecture and civil engineering (e.g.: Stonehenge) >>
‘facility’ (toma Mississippi River como ‘name’)

Methods: GET, POST
Response: JSON array
"entities_list": [{
"name": "John Clark"
}, {
"addressLocality": "Madrid"
}, {
"addressLocality": "Spain"
}, {
"name": "Linares"
}, {
"addressLocality": "Spain"
}, {
"name": "Morgan Clark"
}, {
"affiliation": "BBVA"
}, {
"affiliation": "ERICSSON"
}, {
"affiliation": "GE"
}]

**BIKA for application forms**
=============================
Given a text, used to fill in a form, BIKA extracts the following information: entities, dates, e-mail address and
telephone numbers.

Methods: POST, GET


**POST**
Request
Headers
Body
Request Method: POST
Status Code: 200
Params: {
"callback": "jQuery11654254656562545656",
"text": "\"My name is John Clark and I'm 28. I'm a lawyer. I was born the 1972-06-26 in Madrid, Spain. I live in calle orujo,
4, 23700, Linares, Spain. In case emergency, Monday and Sunday, please contact with my wife Morgan Clark, she was born
on 21/03/1975. You can contact me by e-mail at jdclark@email.com. My phone number is 213 555 776 and home
phonenumber is 666777897 and 91 234 56 78. I work at BBVA, ERICSSON and GE.\""
}


Response
Headers
Status Code: 200
Access-Control-Allow-Origin: *
Date: Mon, 16 Dec 2013 16:17:43 GMT
Server: Werkzeug/0.9.4 Python/3.3.3
Content-Length: 822
Content-Type: application/json

Body
{
"address_list": [],
"dates_list": [{
"weekday": "Monday"
}, {
"birthDate": "26/06/72"
}, {
"birthDate": "21/03/75"
}],
"emails_list": [{
"email": "jdclark@email.com."
}],
"entities_list": [{
"name": "John Clark"
}, {
"addressLocality": "Madrid"
}, {
"addressLocality": "Spain"
}, {
"name": "Linares"
}, {
"addressLocality": "Spain"
}, {
"name": "Morgan Clark"
}, {
"affiliation": "BBVA"
}, {
"affiliation": "ERICSSON"
}, {
"affiliation": "GE"
}],
"phones_list": [{
"telephone": "213555776"
}, {
"telephone": "666777897"
}, {
"telephone": "912345678"
}]
}


**GET**
Request
Headers
Body
Request Method: GET
Status Code: 200
Params: {
"callback": "jQuery11654254656562545656",
"text": "\"My name is John Clark and I'm 28. I'm a lawyer. I was born the 1972-06-26 in Madrid, Spain. I live in calle orujo,
4, 23700, Linares, Spain. In case emergency, Monday and Sunday, please contact with my wife Morgan Clark, she was born
on 21/03/1975. You can contact me by e-mail at jdclark@email.com. My phone number is 213 555 776 and home
phonenumber is 666777897 and 91 234 56 78. I work at BBVA, ERICSSON and GE.\""
}


Response
Headers
Status Code: 200
Date: Mon, 16 Dec 2013 16:09:02 GMT
Server: Werkzeug/0.9.4 Python/3.3.3
Content-Length: 551
Content-Type: text/html; charset=utf-8


Body
jQuery11654254656562545656({"entities_list": [{"name": "John Clark"}, {"addressLocality": "Madrid"}, {"addressLocality":
"Spain"}, {"name": "Linares"}, {"addressLocality": "Spain"}, {"name": "Morgan Clark"}, {"affiliation": "BBVA"}, {"affiliation":
"ERICSSON"}, {"affiliation": "GE"}], "address_list": [], "dates_list": [{"weekday": "Monday"}, {"birthDate": "26/06/72"},
{"birthDate": "21/03/75"}], "phones_list": [{"telephone": "213555776"}, {"telephone": "666777897"}, {"telephone":
"912345678"}], "emails_list": [{"email": "jdclark@email.com."}]});

