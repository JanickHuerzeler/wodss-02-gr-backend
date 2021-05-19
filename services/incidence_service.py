from data_access.canton_data_access import CantonDataAccess


class IncidenceService:


    @staticmethod
    def get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        return CantonDataAccess.get_incidences(canton, dateFrom, dateTo, bfs_nr)