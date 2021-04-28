class Municipality(object):    

    def __init__(self, bfsNr=None, name=None, canton=None, area=None, population=None, *args, **kwargs):        
        

        self._bfs_nr = None
        self._name = None
        self._canton = None
        self._area = None
        self._population = None        

        if bfsNr is not None:
            self.bfs_nr = bfsNr
        if name is not None:
            self.name = name
        if canton is not None:
            self.canton = canton
        if area is not None:
            self.area = area
        if population is not None:
            self.population = population


    @property
    def bfs_nr(self):
        """Gets the bfs_nr of this Municipality.


        :return: The bfs_nr of this Municipality.
        :rtype: int
        """
        return self._bfs_nr

    @bfs_nr.setter
    def bfs_nr(self, bfs_nr):
        """Sets the bfs_nr of this Municipality.


        :param bfs_nr: The bfs_nr of this Municipality.
        :type: int
        """

        self._bfs_nr = bfs_nr

    @property
    def name(self):
        """Gets the name of this Municipality.


        :return: The name of this Municipality.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Municipality.


        :param name: The name of this Municipality.
        :type: str
        """

        self._name = name

    @property
    def canton(self):
        """Gets the canton of this Municipality.


        :return: The canton of this Municipality.
        :rtype: str
        """
        return self._canton

    @canton.setter
    def canton(self, canton):
        """Sets the canton of this Municipality.


        :param canton: The canton of this Municipality.
        :type: str
        """

        self._canton = canton

    @property
    def area(self):
        """Gets the area of this Municipality.


        :return: The area of this Municipality.
        :rtype: float
        """
        return self._area

    @area.setter
    def area(self, area):
        """Sets the area of this Municipality.


        :param area: The area of this Municipality.
        :type: float
        """

        self._area = area

    @property
    def population(self):
        """Gets the population of this Municipality.


        :return: The population of this Municipality.
        :rtype: int
        """
        return self._population

    @population.setter
    def population(self, population):
        """Sets the population of this Municipality.


        :param population: The population of this Municipality.
        :type: int
        """

        self._population = population

    @property
    def as_dict(self):
        """Return object data as dictionary in easily serializeable format"""
        return {
            'bfsNr': self._bfs_nr,
            'name': self._name,
            'canton': self._canton,
            'area': self._area,
            'population': self._population
        }
