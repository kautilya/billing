import Identity
import logging

class Transaction:
  def __init__(self):
    self._from = None
    self._to = None
    self._for = ""
    self._amount = 0.0
    self._status = "N"

  def __init__(self, f, t, amount, forWhat, status) :
    self._from = f
    self._to = t
    self._for = forWhat
    self._amount = amount 
    self._status = status

  def getFrom(self) :
    return self._from;

  def getTo(self) :
    return self._to;

  def getAmount(self) :
    return self._amount;

  def getDescription(self) :
    return self._for;

  def printData(self) :
    logging.info("Transaction: %s paid %f to %s for %s. Status %s\n", self._from.name(), 
        self._amount, str(self._to), self._for, 
        self._status);

