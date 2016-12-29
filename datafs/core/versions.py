
from distutils.version import StrictVersion


class StrictDataVersion(StrictVersion):
    '''
    Examples
    --------

    .. code-block:: python

        >>> v = StrictDataVersion()
        >>> v
        StrictDataVersion ('0.0')
        >>> v.bump(prerelease='alpha')
        >>> v
        StrictDataVersion ('0.0.1a1')
        >>>
        >>> v.bump(prerelease='alpha')
        >>> v
        StrictDataVersion ('0.0.1a2')
        >>>
        >>> v.bump('minor')
        >>> v
        StrictDataVersion ('0.1')
        >>>
        >>> v.bump('minor', prerelease='beta')
        >>> v
        StrictDataVersion ('0.2b1')
        >>>
        >>> v.bump(prerelease='alpha')    # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: Cannot bump version "0.2b1" to prerelease stage "alpha" - version already in beta
        >>> v.bump('minor')
        >>> v
        StrictDataVersion ('0.2')
        >>>
        >>> v < StrictDataVersion('0.03')
        True
        >>> v > StrictDataVersion('0.1.5a13')
        True
        >>>
        >>> StrictDataVersion('0.2.0') > StrictDataVersion('0.2.0a1')
        True


    '''

    def __init__(self, vstring='0.0.0'):
        StrictVersion.__init__(self, vstring)

    def bump(self, kind=None, prerelease=None, inplace=True):

        if kind is not None:

            # if already in pre-release and we want to move to pre-release, 
            # increment version + prerelease
            if self.prerelease and prerelease:
                new_prerelease = self._increment_prerelease(None, prerelease)
                new_version = self._increment_version(self.version, kind)
            
            # if already in pre-release and we want to exit pre-release, 
            # remove prerelease
            elif self.prerelease:
                new_prerelease = None
                if self.version[2] == 0:
                    if kind == 'minor':
                        new_version = self.version
                    else:
                        new_version = self._increment_version(self.version, kind)
                else:
                    if kind == 'patch':
                        new_version = self.version
                    else:
                        new_version = self._increment_version(self.version, kind)


            else:
                new_prerelease = self._increment_prerelease(None, prerelease)
                new_version = self._increment_version(self.version, kind)
        
        elif prerelease is not None:
            if self.prerelease:
                new_prerelease = self._increment_prerelease(self.prerelease, prerelease)
                new_version = self.version
            
            else:
                new_prerelease = self._increment_prerelease(None, prerelease)
                new_version = self._increment_version(self.version, 'patch')


        if inplace == True:
            self.version = new_version
            self.prerelease = new_prerelease

        else:
            new = StrictDataVersion()
            new.version = new_version
            new.prerelease = new_prerelease

            return new

    def _increment_version(self, version, kind):
        
        if kind == 'patch':
            major, minor, patch = self.version
            new_version = (major, minor, patch+1)

        elif kind == 'minor':
            major, minor, patch = self.version
            new_version = (major, minor+1, 0)

        elif kind == 'major':
            major, minor, patch = self.version
            new_version = (major+1, 0, 0)

        elif kind is None:
            new_version = self.version

        else:
            raise ValueError('Bump kind "{}" not understood'.format(kind))

        return new_version

        

    
    def _increment_prerelease(self, current_prerelease, prerelease):

        if prerelease == 'alpha':
            if current_prerelease is None:
                new_prerelease = ('a', 1)

            else:
                if current_prerelease[0] == 'a':
                    new_prerelease = ('a', int(current_prerelease[1]) + 1)
                
                elif current_prerelease[0] == 'b':
                    msg = 'Cannot bump version "{}"'.format(self) +\
                    ' to prerelease stage "alpha"'' - version already in beta'

                    raise ValueError(msg)
                else:
                    msg = 'Version "{}" prerelease "{}" not understood'.format(
                        self, kind)

                    raise ValueError(msg)
        
        elif prerelease == 'beta':
            if current_prerelease is None:
                new_prerelease = ('b', 1)

            else:
                if current_prerelease[0] == 'a':
                    new_prerelease = ('b', 1)
                
                elif current_prerelease[0] == 'b':
                    new_prerelease = ('b', int(current_prerelease[1]) + 1)

                else:
                    msg = 'Version "{}" prerelease "{}" not understood'.format(
                        self, kind)

                    raise ValueError(msg)

        elif prerelease is None:
            new_prerelease = current_prerelease

        else:
            raise ValueError('Prerelease type "{}" not understood'.format(
                prerelease))

        return new_prerelease