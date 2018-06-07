#!/usr/bin/env python3

from icalendar import Calendar
from urllib.request import urlretrieve
import os.path
import re
import csv
import datetime

base_url = "https://cloud.sleepmap.de/remote.php/dav/public-calendars/"
calendars = {
    "nativespace":
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
                 location, relative_location, start, end, duration, day,
                 description):
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
        self.duration = duration
        self.day = day
        self.description = description

    def __repr__(self):
        return repr((self.name, self.location, self.start, self.end))

    def pretty_print_author(self):
        author_string = ""
        for pair in self.author.split('|'):
            uid, _, name = pair.partition(":")
            if author_string == "":
                author_string = name
            else:
                author_string = author_string + ", " + name
        return author_string


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


def __print_paper_link_by_id(id):
    if os.path.isfile("files/pdf/"+str(id)+"-paper.pdf"):
        return "`Paper </pdf/"+str(id)+"-paper.pdf>`_ "
    else:
        return ""


def __print_compressed_link_by_id(id):
    if os.path.isfile("files/compressed/"+str(id)+"-additional.tar.gz"):
        return "`Archive </compressed/"+str(id)+"-additional.tar.gz>`_ "
    else:
        return ""


def __get_duration(start, end):
    duration_seconds = (end - start).total_seconds()
    duration_hours, remainder = divmod(duration_seconds, 3600)
    duration_minutes, seconds = divmod(remainder, 60)
    return datetime.time(hour=int(duration_hours),
                         minute=int(duration_minutes))


# sort events by day in a days dict
def __sort_events_by_day(events, days):
    for event in events:
        if event.start.date() in days.keys():
            days[event.start.date()].append(event)
        else:
            days[event.start.date()] = [event]
    event_day = 1
    for day in sorted(days.keys()):
        for event in days[day]:
            event.day = event_day
        event_day = event_day + 1


# sort days by (start) time and relative_location in a days dict
def __sort_days_by_time(days):
    # sort events by start time
    for day in sorted(days.keys()):
        days[day] = sorted(days[day], key=lambda x: (x.start,
                           x.relative_location))


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
                        duration=__get_duration(
                            item.get('DTSTART').dt,
                            item.get('DTEND').dt),
                        day=0,
                        description=item.get('DESCRIPTION')
                        )
                    )


# link all schedules in a per day schedule in pages/schedule.rst
def write_schedule(events):
    schedule = open('pages/schedule.rst', 'w')
    days = {}
    day_counter = 1
    # write header
    schedule.write('.. title: Schedule\n')
    schedule.write('.. slug: schedule\n')
    schedule.write('.. date: \n')
    schedule.write('.. tags: \n')
    schedule.write('.. category: \n')
    schedule.write('.. link: \n')
    schedule.write('.. description: \n')
    schedule.write('.. type: text\n')

    __sort_events_by_day(events, days)
    __sort_days_by_time(days)

    # write schedule, sorted by day, start time and location
    for day in sorted(days.keys()):
        schedule.write('\n')
        schedule.write("Day "+str(day_counter)+" ("+str(day)+")\n")
        schedule.write("==================\n")
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
            schedule.write("     - "+event.pretty_print_author()+"\n")
            schedule.write("     - `" + event.name +
                           " </pages/event/"+str(event.id)+"/>`_\n")
        day_counter = day_counter + 1

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
        event_page.write('**Author(s)**: '+event.pretty_print_author()+'\n')
        event_page.write('\n')
        event_page.write('**Keywords**: '+event.keywords+'\n')
        event_page.write('\n')
        event_page.write('**Abstract**: \n'+event.abstract+'\n')
        event_page.write('\n')
        event_page.write('**Downloads**: ' +
                         __print_paper_link_by_id(event.id) +
                         __print_compressed_link_by_id(event.id)+'\n')


# write all events to files/fahrplan.csv, compatible with voctosched
def write_csv(events):
    field_names = ["Room", "Date", "Day", "Start", "Duration", "Title", "ID",
                   "Abstract", "Description", "Language", "Speakers",
                   "File URL"]
    days = {}
    __sort_events_by_day(events, days)
    __sort_days_by_time(days)
    csv_file = open("files/fahrplan.csv", "w", newline='')
    csv_writer = csv.DictWriter(
            csv_file,
            delimiter=',',
            fieldnames=field_names)
    csv_writer.writeheader()
    # write csv schedule, sorted by day, start time and location
    for date in sorted(days.keys()):
        for event in days[date]:
            csv_writer.writerow({
                "Room": event.relative_location,
                "Date": date,
                "Day": event.day,
                "Start": str(event.start.time().isoformat('minutes')),
                "Duration": event.duration.isoformat('minutes'),
                "Title": event.name,
                "ID": event.id,
                "Abstract": event.abstract,
                "Description": event.abstract,
                "Language": "en",
                "Speakers": event.author,
                "File URL": " "})


def main():
    events = []
    for name, url in calendars.items():
        download_calendar(name, base_url+url)
        retrieve_events_from_calendar(name, events)
    write_schedule(events)
    write_csv(events)
    write_events(events)


if __name__ == "__main__":
    main()

