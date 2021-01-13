# Incident Database (IDB)

IDB is a database of software failures (or _incidents_, as we call them) and a simple web site (that you can build locally) for browsing that database. We hope this will be a useful resource for researchers and engineers. Really anyone who is interested in software failures, should enjoy browsing IDB.

## Background

Many organizations conduct a postmortem analysis when they experience significant incidents, and in some cases they publish the results as an _incident report_. Well we've read through many of these reports (more than 40 of them so far) and extracted a uniform set of properties about each (title, organization, product, start and end dates, author, url, etc). We have also written a structured summary of each, capturing:  

* The aspects of the system architecture relevant to the incident,
* The root cause of the incident,
* What failure(s) occurred during the incident,
* The impact of that failure or those failures from the users perspective,
* A series of events describing how the incident happened, and
* How the problem was mitigated or resolved. 

## Quick start instructions

To build the database and website on your own machine you need to have Python3 installed. To get started, download or clone this repository and then run the following command:

    $ python src/build.py

With that done, just open the file html/index.html in a web browser. If you know SQL You can also explore the database directly by running the sqlite3 command and executing queries. 

    $ sqlite3 idb.db
    SQLite version 3.28.0 2019-04-15 14:49:49
    Enter ".help" for usage hints.
    sqlite> select id,title from incidents order by id;
    1|Buildkite Outage
    2|Always Be Closing: The Tale of a Go Resource Leak
    3|Unavailable Guilds & Connection Issues
    4|Incident report on memory leak caused by Cloudflare parser bug
    5|What We Learned from the Recent Mandrill Outage
    6|Postmortem of database outage of January 31
    <etc>

## Simulating failures using  Quartermaster

[Quartermaster is a modeling and simulation tool](https://github.com/BYU-SE/quartermaster). We have used Quartermaster to create simulations of many of the failures captured by the incident reports we have included in IDB. Our goal with these simulations is to create a simple model that captures the essence of the incident and allow us (and others) to explore different fault-tolerant techniques that might have mitigated or prevented the incident.

Here is the basic process for using Quartermaster for this purpose:

1. Create a model of the system that failed, but ONLY the parts of the system that are directly involved in the incident. To create a model in Quartermaster involves thinking about the system's architecture as a series of "stages" writing a small amount of code to define those stages.
2. Write the code that captures the scenario the led to the failure. If the precipitating event was a surge in traffic (like for incident X) then a small amount of code is written to define that surge.
3. Run the simulator which will then simulate the behavior of the model under that scenario, printing out a table of results at the end.

To see examples, please visit [this repository](https://github.com/BYU-SE/idb-quartermaster-models).

## Contributing

If you are interested in adding incident reports to our dataset, please consider that we are only interested in incidents that: (1) describe a software system failure or significant degradation, and (2) contain the details we need to create a structured summary, as described above. If you have some incidents that fit this description feel free to clone the repository and send us a pull request.
