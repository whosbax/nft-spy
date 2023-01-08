""" Spies Inferface Define commmon behavor """
from abc import abstractmethod, ABCMeta

class ISpy(metaclass=ABCMeta):
    """ Spy behavor """

    @abstractmethod
    def i_get_listings(self):
        """
        Get listing of collections 
            Raise: NotImplementedError: abstract
        """
        raise NotImplementedError

    @abstractmethod
    def i_get_collections(self):
        """
        Get NFT list of collection
            Raise: NotImplementedError: abstract
        """
        raise NotImplementedError

    @abstractmethod
    def i_get_sales(self):
        """
        Get collection sales
            Raise: NotImplementedError: abstract
        """
        raise NotImplementedError