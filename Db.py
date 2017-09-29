import Identity
import logging
import Transaction
import time

class DbError(Exception):
  pass;

class EntityDatabase:
  def __init__(self):
    self._entities = {"bank": Identity.Entity("bank", "none", "", "none"), 
                      "donation": Identity.Entity("donation", "none", "", "none")};
    self._entityGroups = {"all": Identity.EntityGroup("all")}
    self._transactions = [];
    self._settlement = dict();
    self._title = "unknown";

  def setDefaults(self) :
    pass;

  def printData(self):
    for n, e in self._entities.iteritems():
      e.printData();
    for n, e in self._entityGroups.iteritems():
      e.printData();
    for t in self._transactions:
      t.printData();

  def addEntity(self, row) :
    logging.debug("Adding entity %s\n", ",".join(row));
    if (len(row) != 5) :
      raise DbError("Bad Entity : %s\n", ",".join(row));
    entity = Identity.Entity(row[1], row[2], row[3], row[4]);
    if (self._entities.get(entity.name(), None) == None) :
      self._entities[entity.name()] = entity
      self._entityGroups["all"].addEntity(entity);
    else :
      raise DbError("Duplicate Entity : %s\n", ",".join(row));

  def addGroup(self, row) :
    logging.debug("Adding group %s\n", ",".join(row));
    if (len(row) != 3) :
      raise DbError("Bad Group : %s\n", ",".join(row));
    if (self._entityGroups.get(row[1], None) != None) :
      raise DbError("Duplicate Group %s\n", ",".join(row));
    entityGroup = Identity.EntityGroup(row[1]);
    entities = row[2].split();
    if (len(entities) == 0) :
      raise DbError("Bad Group. Null entities: %s\n", ",".join(row));
    for e in entities : 
      entity = self._entities.get(e, None);
      if (entity == None) :
        raise DbError("Unknown entity %s in group: %s\n", e, ",".join(row));
      entityGroup.addEntity(entity);
    self._entityGroups[row[1]] = entityGroup;


  def addTransaction(self, row) :
    logging.debug("Adding transaction %s\n", ",".join(row));
    if (len(row) != 6) :
      raise DbError("Bad Transaction: %s\n", ",".join(row));
    f = self._entities.get(row[1]);
    if (f == None) :
      raise DbError("Illegal entity in transaction\n", ",".join(row));
    eOrG = row[2].split();
    if (len(eOrG) == 1 and eOrG[0] == "bank") :
      entityGroup = self._entities.get(eOrG[0]);
    else :
      entityGroup = Identity.EntityGroup(row[1]);
      for eg in eOrG :
        to = self._entities.get(eg);
        if (to == None) :
          to = self._entityGroups.get(eg);
          if (to == None) :
            raise DbError("Illegal entity in transaction\n", ",".join(row));
        entityGroup.add(to)

    t = Transaction.Transaction(f, entityGroup, float(row[3]), row[4], row[5])
    self._transactions.append(t);

  def addTitle(self, row) :
    logging.debug("Adding titiel %s\n", ",".join(row));
    if (len(row) != 2) : 
      raise DbError("Bad Title: %s\n", ",".join(row));
    self._title = row[1];

  def addComment(self, row) :
    logging.debug("Ignoring comment %s\n", ",".join(row));

  def getTitle(self) :
    return self._title;

  def badData(self, row) :
    logging.error("Bad data %s\n", ",".join(row));
    raise DbError("Bad data:", ",".join(row));

  def _initSettlementDict(self) :
    for n, e in self._entities.iteritems() :
      self._settlement[n] = 0.0;

  def calculate(self) :
    self._initSettlementDict();
    for t in self._transactions :
      if t.getFrom().name() == "bank":
        if isinstance(t.getTo(), Identity.Entity) :
          self._settlement["bank"] = self._settlement["bank"] - t.getAmount();
          self._settlement[t.getTo().name()] = self._settlement[t.getTo().name()] - t.getAmount(); 
        elif isinstance(t.getTo(), Identity.EntityGroup) :
          self._settlement["bank"] = self._settlement["bank"] - t.getAmount();
          group = t.getTo().getEntities(); #A set
          amount = t.getAmount() / (len(group)); 
          for e in group :
            self._settlement[e.name()] = self._settlement[e.name()] - amount;
        else : 
          logging.error("Bad Transaction, printed below\n");
          t.printData();
          raise DbError("Illegal transaction");
      elif isinstance(t.getTo(), Identity.Entity) and t.getTo().name() == "bank" :
        self._settlement["bank"] = self._settlement["bank"] + t.getAmount();
        self._settlement[t.getFrom().name()] = self._settlement[t.getFrom().name()] + t.getAmount(); 
      elif isinstance(t.getTo(), Identity.EntityGroup) :
        group = t.getTo().getEntities(); #A set
        amount = t.getAmount() / (len(group)); 
        self._settlement[t.getFrom().name()] = self._settlement[t.getFrom().name()] + t.getAmount(); 
        for e in group :
          self._settlement[e.name()] = self._settlement[e.name()] - amount;
      elif isinstance(t.getTo(), Identity.Entity) and t.getTo().name() == "donation"  :
        self._settlement["donation"] = self._settlement["donation"] + t.getAmount();
        self._settlement[t.getFrom().name()] = self._settlement[t.getFrom().name()] - t.getAmount();
      else:
        logging.error("Bad Transaction, printed below\n");
        t.printData();
        raise DbError("Illegal transaction");

  def getEmailList(self) :
    el = "";
    for n, e in self._entities.iteritems() :
      if e.getEmail() != "none" :
        el = el + e.name() + " <" + e.getEmail() + ">,";
      if e.getSpouseEmail() != "none" :
        el = el + e.getSpouse() + "<" + e.getSpouseEmail() + ">,";
    return el[:-1]; # Remove the last ','

  def getEmailOnlyList(self) :
    el = [];
    for n, e in self._entities.iteritems() :
      if e.getEmail() != "none" :
        el.append(e.getEmail());
      if e.getSpouseEmail() != "none" :
        el.append(e.getSpouseEmail()); 
    return el;

  def htmlreport(self, text) :
    paypalButtonPrefix = "<a href=\"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=shirish%2erai%40kautilya%2eorg&lc=US&item_name=Spago%20Expenses&amount="
    paypalButtonSuffix = "&currency_code=USD&button_subtype=services&no_note=0&bn=PP%2dBuyNowBF%3abtn_buynowCC_LG%2egif%3aNonHostedGuest\">Pay via PayPal</a>";
    output = ""
    output = output + "<html>\n"
    output = output + "  <head>\n"
    output = output + "    <style type=\"text/css\">\n"
    output = output + "      .TFtable tr:nth-child(odd){ background: #b8d1f3; }\n"
    output = output + "      .TFtable tr:nth-child(even){ background: #dae5f4; }\n"
    output = output + "    </style>\n"
    output = output + "  </head>\n"
    output = output + "  <body>\n"
    output = output + "    <h1>" + self._title + "</h1>\n"
    output = output + "    <b>" + time.strftime("%c") + "</b>\n";
    if text : 
      output = output + "<p style=\"color:blue\"/>" + text + "\n";
    output = output + "    <br\>\n";
    output = output + "    <table class=\"TFtable\">\n";
    output = output + "      <tr><td>NAME</td><td>AMOUNT</td></tr>\n";
    for n, v in self._settlement.iteritems() :
      style = ""
      paypalButton = "";
      amount = round(v, 2);
      if (abs(amount) == 0.01) :
        amount = 0.0;
      if amount < 0 :
        style = " style=\"color:red\""
        paypalButton = paypalButtonPrefix + str(abs(amount)).replace(".", "%2e") + paypalButtonSuffix;
      elif amount > 0 :
        style = " style=\"color:green\""
      output = output + "      <tr><td>" + n + "</td><td"+ style + ">" + str(amount) + "</td><td>" + paypalButton + "</td></tr>\n";
    output = output + "    </table>\n<br/>";
    output = output + "    <p/>Please make payments via PayPal to <a href=\"mailto:shirish.rai@kautilya.org\">shirish.rai@kautilya.org</a>\n<br/>\n"
    output = output + "    <h1>Transactions</h1>\n"
    output = output + "    <table class=\"TFtable\">\n";
    output = output + "      <tr><td>FROM</td><td>TO</td><td>AMOUNT</td><td>DESCRIPTION</td></tr>\n";
    for t in self._transactions :
      output = output + "      <tr><td>" + t.getFrom().name() + "</td><td>" + t.getTo().memNames() + "</td><td>" + str(t.getAmount()) + "</td><td>" + t.getDescription() + "</td></tr>\n";
    output = output + "    </table>\n";
    output = output + "  </body>\n"
    output = output + "</html>\n"
    return output;

  def report(self, text) :
    output = self._title.center(80) + "\n";
    output = output + time.strftime("%c").center(80) + "\n\n";
    if text : 
      output = output + text + "\n\n";
    output = output + '{0:20} {1:10}'.format("NAME", "AMOUNT") + "\n";
    output = output + '{0:20} {1:10}'.format("====", "======") + "\n";
    for n, v in self._settlement.iteritems() :
      amount = round(v, 2);
      if (abs(amount) == 0.01) :
        amount = 0.0;
      output = output + '{0:20} {1:5.2f}'.format(n, amount) + "\n";
    output = output + "Please pay via PayPal to shirish.rai@kautilya.org\n\n";
    output = output + "TRANSACTIONS\n"
    output = output + '{0:20} {1:60} {2:10} {3:50}'.format("FROM", "TO", "AMOUNT", "DESCRIPTION") + "\n";
    for t in self._transactions :
      output = output + '{0:20} {1:60} {2:7.2f} {3:50}'.format(t.getFrom().name(),t.getTo().memNames(), 
          t.getAmount(), t.getDescription()) + "\n";
    return output;
