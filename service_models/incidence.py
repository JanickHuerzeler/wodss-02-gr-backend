from configManager import ConfigManager

class Incidence(object):

    def __init__(self, bfsNr=None, date=None, incidence=None, *args, **kwargs):
   
        self._bfs_nr = None
        self.__date = None
        self._incidence = None        

        if bfsNr is not None:
            self.bfs_nr = bfsNr
        if date is not None:
            self.__date = date
        if incidence is not None:
            self.incidence = incidence

    @property
    def bfs_nr(self):
        """Gets the bfs_nr of this Incidence.


        :return: The bfs_nr of this Incidence.
        :rtype: int
        """
        return self._bfs_nr

    @bfs_nr.setter
    def bfs_nr(self, bfs_nr):
        """Sets the bfs_nr of this Incidence.


        :param bfs_nr: The bfs_nr of this Incidence.
        :type: int
        """

        self._bfs_nr = bfs_nr

    @property
    def _date(self):
        """Gets the _date of this Incidence.


        :return: The _date of this Incidence.
        :rtype: date
        """
        return self.__date

    @_date.setter
    def _date(self, _date):
        """Sets the _date of this Incidence.


        :param _date: The _date of this Incidence.
        :type: date
        """

        self.__date = _date

    @property
    def incidence(self):
        """Gets the incidence of this Incidence.


        :return: The incidence of this Incidence.
        :rtype: float
        """
        return self._incidence

    @incidence.setter
    def incidence(self, incidence):
        """Sets the incidence of this Incidence.


        :param incidence: The incidence of this Incidence.
        :type: float
        """

        self._incidence = incidence

    
    @property
    def as_dict(self):
        """Return object data as dictionary in easily serializeable format"""                
        return {
            'bfsNr': self._bfs_nr,
            'date': self.__date, # already comes as string, not format neccessary
            'incidence': self._incidence
        }
