import Identity
import Db
from optparse import OptionParser
import csv
import logging
import getpass
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def mailReport(edb,report, htmlreport, mlist) :
  passwd = getpass.getpass("kautilya mail password:");
  msg = MIMEMultipart('alternative')
  msg['Subject'] = edb.getTitle()
  msg['From'] = "shirish.rai@kautilya.org"
  msg['To'] = mlist if mlist else edb.getEmailList()

  part1 = MIMEText(report, 'plain')
  part2 = MIMEText(htmlreport, 'html')

  msg.attach(part1)
  msg.attach(part2)

  logging.debug("Email Message: \n%s\n", report);
  logging.debug("HTML Email Message: \n%s\n", htmlreport);

  mail = smtplib.SMTP_SSL("smtp.bizmail.yahoo.com", 465);
  mail.set_debuglevel(1)
  mail.login("shirish.rai@kautilya.org", passwd)
  mail.sendmail("shirish.rai@kautilya.org", mlist if mlist else edb.getEmailOnlyList(), msg.as_string());
  mail.quit()

def process(ltype, edb) :
  return {
      "e": lambda x: edb.addEntity(x),
      "t": lambda x: edb.addTransaction(x),
      "title": lambda x: edb.addTitle(x),
      "c": lambda x: edb.addComment(x),
      "g": lambda x: edb.addGroup(x),
      }.get(ltype, lambda x: edb.badData(x));

parser = OptionParser()
parser.add_option("-d", action="store", type="string", dest="database", help="Database File")
parser.add_option("-v", action="store_true", dest="debug", help="Show debug output")
parser.add_option("-m", action="store_true", dest="mail", help="email report")
parser.add_option("-l", action="store", type="string", dest="emaillist", help="Email List");
parser.add_option("-t", action="store", type="string", dest="text", help="Email Text");
(options, args) = parser.parse_args()
if not options.database:
  parser.error("Database is required. Use -d filename");

logging.basicConfig(level=(logging.DEBUG if options.debug else logging.ERROR))

edb = Db.EntityDatabase()
with open(options.database, "rb") as db:
  reader = csv.reader(db);
  try:
    for row in reader:
      entityProcessor = process(row[0], edb)
      entityProcessor(row);
  except csv.Error as e:
    sys.exit('file %s, line %d: %s' % (options.database, reader.line_num, e))

  edb.setDefaults();
  edb.printData();

  edb.calculate();
  report = edb.report(options.text);
  htmlreport = edb.htmlreport(options.text);
  print report;
  if (options.mail) :
    mailReport(edb,report,htmlreport, options.emaillist);

