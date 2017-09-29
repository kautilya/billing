import logging;

class Entity:
  def __init(self):
    pass;

  def __init__(self, name, email, spouse, semail):
    self._name = name;
    self._email = email;
    self._spouse = spouse;
    self._semail = semail;

  def printData(self) :
    logging.info("Entity: %s <%s>\n", self._name, self._email);

  def name(self) :
    return self._name;

  def memNames(self) : 
    return self._name;

  def getEmail(self) :
    return self._email;

  def getSpouse(self) :
    return self._spouse;

  def getSpouseEmail(self) :
    return self._semail;

class EntityGroup:
  def __init__(self):
    pass;

  def __init__(self, name):
    self._name = name;
    self._entities = set();
    self._memNames = "";
    pass;

  def name(self) :
    return self._name;

  def memNames(self) :
    return self._memNames;

  def addEntity(self, entity):
    self._entities.add(entity);
    if (len(self._memNames) > 0) :
      self._memNames = self._memNames + " " + entity.name();
    else :
      self._memNames = self._memNames + entity.name();

  def add(self, entity):
    if isinstance(entity, Entity) :
      self.addEntity(entity);
    elif isinstance(entity, EntityGroup) :
      for e in entity._entities :
        self.addEntity(e);

  def getEntities(self) :
    return self._entities;

  def printData(self) :
    logging.info("EngityGroup: %s : %s\n", self._name, str(self._entities));

