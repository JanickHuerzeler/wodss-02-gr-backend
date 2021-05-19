from data_access.canton_data_access import CantonDataAccess


class MunicipalityService:
    @staticmethod
    def get_municipalities(canton):
        return CantonDataAccess.get_municipalities(canton)

    @staticmethod
    def get_municipality(canton, bfs_nr):
        return CantonDataAccess.get_municipality(canton, bfs_nr)