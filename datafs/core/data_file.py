

class DataFile(object):
    '''
    Base class for DataFile objects

    Should be subclassed, along with fs filesystem classes

    '''


    def __init__(self, api, archive):
        self.api = api
        self.archive = archive

    @property
    def metadata(self):
        return self.archive.metadata

    @metadata.setter
    def metadata(self, value):
        raise AttributeError('metadata attribute cannot be set')


    def delete_local(self):
        raise NotImplementedError






