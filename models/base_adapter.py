class BaseAdapter:
    """
    Base interface for all DexOS model adapters.
    """

    def generate(self, prompt, system=None):
        """
        Generate a model response.
        """
        raise NotImplementedError()

    def health_check(self):
        """
        Check if backend model is reachable.
        """
        raise NotImplementedError()

    def model_name(self):
        """
        Return the name of the model backend.
        """
        raise NotImplementedError()
