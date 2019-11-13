class Instance:
    def __init__(self, tag, functionality, l_f, r_f):
        self.tag = tag
        self.functionality = functionality
        self.l_f = l_f
        self.r_f = r_f

    def get_functionality(self):
        return self.functionality

    def get_l(self):
        return self.l_f

    def get_r(self):
        return self.r_f

    def get_tag(self):
        return self.tag
