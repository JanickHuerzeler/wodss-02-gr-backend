class Incidence(object):

    def __init__(self, bfsNr=None, date=None, incidence=None, *args, **kwargs):

        self._bfs_nr = None
        self._date = None
        self._incidence = None

        if bfsNr is not None:
            self.bfs_nr = bfsNr
        if date is not None:
            self.date = date
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
    def date(self):
        """Gets the date of this Incidence.


        :return: The date of this Incidence.
        :rtype: date
        """
        return self._date

    @date.setter
    def date(self, date):
        """Sets the date of this Incidence.


        :param date: The date of this Incidence.
        :type: date
        """

        self._date = date

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
            'date': self._date,  # already comes as string, not format neccessary
            'incidence': self._incidence
        }
