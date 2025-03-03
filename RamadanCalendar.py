import http.client
import urllib.parse
from datetime import datetime, timedelta, date
import json

ramadan_start_date=datetime.strptime("2025-03-01", "%Y-%m-%d").date()
ramadan_end_date=datetime.strptime("2025-03-29", "%Y-%m-%d").date()
ramadan_days=(ramadan_end_date - ramadan_start_date).days+1
event_duration_in_minutes=45

# İller listesi
cities  = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya", "Artvin", "Aydın", "Balıkesir",
    "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli",
    "Diyarbakır", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane",
    "Hakkari", "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir", "Kars", "Kastamonu", "Kayseri", "Kırklareli",
    "Kırşehir", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş",
    "Nevşehir", "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
    "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman",
    "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük", "Kilis", "Osmaniye",
    "Düzce"
]
#Exceptions
city_center_exceptions = {
    "Hatay" : "Antakya",
    "Kocaeli": "İzmit",
    "Sakarya" : "Adapazarı"
}

request_errors=[]
for city in cities:
    region = city.capitalize()
    encoded_region = urllib.parse.quote(region)
    if(region not in city_center_exceptions):
        encoded_city = encoded_region
    else:
        encoded_city = urllib.parse.quote(city_center_exceptions[region])
    conn = http.client.HTTPSConnection("vakit.vercel.app")
    conn.request(
        "GET",
        f"/api/timesFromPlace?country=Turkey&region={encoded_region}&city={encoded_city}&date={ramadan_start_date.strftime('%Y-%m-%d')}&days={ramadan_days}&timezoneOffset=180&calculationMethod=Turkey"
    )
    res = conn.getresponse()
    data = res.read()
    json_data = json.loads(data)
    if "error" in json_data:
        request_errors.append( f"/api/timesFromPlace?country=Turkey&region={encoded_region}&city={encoded_city}&date={ramadan_start_date.strftime('%Y-%m-%d')}&days={ramadan_days}&timezoneOffset=180&calculationMethod=Turkey")
        continue
    sahur_times =[]
    iftar_times =[]
    for ramadan_day in json_data["times"].values():
        sahur_times.append(ramadan_day[0])
        iftar_times.append(ramadan_day[4])


    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Iftar and Sahur Times//TR
CALSCALE:GREGORIAN
"""

    for i in range(len(sahur_times)):
        event_date = ramadan_start_date + timedelta(days=i)
        
        imsak_time = datetime.strptime(sahur_times[i], "%H:%M").time()
        iftar_time = datetime.strptime(iftar_times[i], "%H:%M").time()
        
        imsak_end = datetime.combine(event_date, imsak_time)
        iftar_start = datetime.combine(event_date, iftar_time)
        
        imsak_start = imsak_end + timedelta(minutes=-event_duration_in_minutes)
        iftar_end = iftar_start + timedelta(minutes=event_duration_in_minutes)

        imsak_start_str = imsak_start.strftime("%Y%m%dT%H%M%S")
        imsak_end_str = imsak_end.strftime("%Y%m%dT%H%M%S")
        iftar_start_str = iftar_start.strftime("%Y%m%dT%H%M%S")
        iftar_end_str = iftar_end.strftime("%Y%m%dT%H%M%S")

        ics_content += f"""
BEGIN:VEVENT
SUMMARY:Sahur
DTSTART;TZID=Europe/Istanbul:{imsak_start_str}
DTEND;TZID=Europe/Istanbul:{imsak_end_str}
DESCRIPTION:Sahur vakti
END:VEVENT

BEGIN:VEVENT
SUMMARY:İftar
DTSTART;TZID=Europe/Istanbul:{iftar_start_str}
DTEND;TZID=Europe/Istanbul:{iftar_end_str}
DESCRIPTION:İftar vakti
END:VEVENT
"""

    ics_content += "\nEND:VCALENDAR"

    with open(str(ramadan_start_date.year)+"_"+city+"_iftar_sahur_events.ics", "w", encoding="utf-8") as file:
        file.write(ics_content)

    print(str(ramadan_start_date.year)+"_"+city+"_iftar_sahur_events.ics"+" succesfully created!")

print("Errors occured in requests below:")
print(request_errors)