#!/usr/bin/env python3

from icalendar import Calendar
from urllib.request import urlretrieve
import os.path
import re

base_url = "https://cloud.sleepmap.de/remote.php/dav/public-calendars/"
calendars = {
    "artistania":
    "PW6EescRREt9Bmte?export",
    "ceminar":
    "oqm2Tq2HqtxAM95a?export",
    "mainhall":
    "i8qaBgwFdGAqGtC6?export",
    "spektrum":
    "rcwy38xSMGib4ZXi?export"
}
match_eol = re.compile('$|\n', flags=re.M)


class LACEvent:
    def __init__(self, author, type, topics, keywords, abstract, id, name,
                 location, relative_location, start, end, description):
        self.author = author
        self.type = type
        self.topics = topics
        self.keywords = keywords
        self.abstract = abstract
        self.id = id
        self.name = name
        self.location = location
        self.relative_location = relative_location
        self.start = start
        self.end = end
        self.description = description

    def __repr__(self):
        return repr((self.name, self.location, self.start, self.end))


def __get_id_from_description(description):
    match = re.search('ID: (.+?)$', description)
    if match:
        return match.group(1)
    else:
        return 0


def __get_author_from_description(description):
    match = re.search('Author: (.*)', description)
    if match:
        return match.group(1)
    else:
        return "nobody"


def __get_type_from_description(description):
    match = re.search('Type: (.*)', description)
    if match:
        return match.group(1)
    else:
        return "Presentation"


def __get_topics_from_description(description):
    match = re.search('Topics: (.*)', description)
    if match:
        return match.group(1)
    else:
        return "None"


def __get_keywords_from_description(description):
    match = re.search('Keywords: (.*)', description)
    if match:
        return match.group(1)
    else:
        return "None"


def __get_abstract_from_description(description):
    match = re.search('Abstract: (.*)\nID: ', description, re.S)
    if match:
        return match.group(1)
    else:
        return "None"


def __print_pdf_by_id(id):
    if os.path.isfile("files/pdf/"+str(id)+".pdf"):
        return "`pdf </pdf/"+str(id)+".pdf>`_"
    else:
        return ""


# download calendar by name and url
def download_calendar(name, url):
    urlretrieve(url, "files/calendar/"+name+".ics")


# save events from calendar to object
def retrieve_events_from_calendar(name, events):
    calendar = open("files/calendar/"+name+'.ics', 'rb')
    calendar_events = Calendar.from_ical(calendar.read())
    for item in calendar_events.walk():
        if item.name == 'VEVENT':
            description = str(item.get('DESCRIPTION'))
            events.append(
                    LACEvent(
                        author=__get_author_from_description(description),
                        type=__get_type_from_description(description),
                        topics=__get_topics_from_description(description),
                        keywords=__get_keywords_from_description(description),
                        abstract=__get_abstract_from_description(description),
                        id=__get_id_from_description(description),
                        name=item.get('SUMMARY'),
                        location="("+name+") "+str(item.get('LOCATION')),
                        relative_location=name,
                        start=item.get('DTSTART').dt,
                        end=item.get('DTEND').dt,
                        description=item.get('DESCRIPTION')
                        )
                    )


# link all schedules in a per day schedule in pages/schedule.rst
def write_schedule(events):
    schedule = open('pages/schedule.rst', 'w')
    days = {}
    # write header
    schedule.write('.. title: Schedule\n')
    schedule.write('.. slug: schedule\n')
    schedule.write('.. date: \n')
    schedule.write('.. tags: \n')
    schedule.write('.. category: \n')
    schedule.write('.. link: \n')
    schedule.write('.. description: \n')
    schedule.write('.. type: text\n')

    # sort by day
    for event in events:
        if event.start.date() in days.keys():
            days[event.start.date()].append(event)
        else:
            days[event.start.date()] = [event]

    # sort events by start time
    for day in sorted(days.keys()):
        days[day] = sorted(days[day], key=lambda x: (x.start,
                           x.relative_location))

    # write schedule, sorted by day, start time and location
    for day in sorted(days.keys()):
        schedule.write('\n')
        schedule.write(str(day)+"\n")
        schedule.write("==========\n")
        schedule.write("\n")
        schedule.write(".. list-table::\n")
        schedule.write("   :widths: auto\n")
        schedule.write("\n")
        for event in days[day]:
            schedule.write("   * - "
                           + str(event.start.time().isoformat('minutes'))+" - "
                           + str(event.end.time().isoformat('minutes'))+"\n")
            schedule.write("     - "+event.relative_location+"\n")
            schedule.write("     - "+event.type+"\n")
            schedule.write("     - `" + event.name +
                           " </pages/event/"+str(event.id)+"/>`_\n")

    # write links
    schedule.write("\n")
    for name, url in calendars.items():
        schedule.write("`Subscribe to " + name + 
                       " calendar </calendar/"+str(name)+".ics>`_\n")
        schedule.write("\n")


# write all events to pages/event/<id>.rst
def write_events(events):
    for event in events:
        event_page = open("pages/event/"+str(event.id)+".rst", "w")
        # write header
        event_page.write('.. title: '+event.name+'\n')
        event_page.write('.. slug: '+str(event.id)+'\n')
        event_page.write('.. date: \n')
        event_page.write('.. tags: '+event.keywords+'\n')
        event_page.write('.. category: '+event.type+'\n')
        event_page.write('.. link: \n')
        event_page.write('.. description: \n')
        event_page.write('.. type: text\n')
        event_page.write('\n')
        event_page.write('**Type**: '+str(event.type)+'\n')
        event_page.write('\n')
        event_page.write('**Day**: '+str(event.start.date())+'\n')
        event_page.write('\n')
        event_page.write('**Time**: ' +
                         str(event.start.time().isoformat('minutes'))+" - " +
                         str(event.end.time().isoformat('minutes'))+"\n")
        event_page.write('\n')
        event_page.write('**Author(s)**: '+event.author+'\n')
        event_page.write('\n')
        event_page.write('**Keywords**: '+event.keywords+'\n')
        event_page.write('\n')
        event_page.write('**Abstract**: \n'+event.abstract+'\n')
        event_page.write('\n')
        event_page.write('**Downloads**: '+__print_pdf_by_id(event.id)+'\n')


def main():
    events = []
    for name, url in calendars.items():
        download_calendar(name, base_url+url)
        retrieve_events_from_calendar(name, events)
    write_schedule(events)
    write_events(events)


if __name__ == "__main__":
    main()

