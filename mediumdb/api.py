class Category:
    def _get(self):
        raise NotImplemented

    def _filter(self):
        raise NotImplemented

class Topic:

    def _get(self):
        raise NotImplemented

    def _filter(self, category):
        raise NotImplemented

    def add_comment(self):
        raise NotImplemented

class Comment:

    def _get(self):
        raise NotImplemented

    def _filter(self, topic):
        raise NotImplemented
