

class main():
    def __init__(self):
        self.onep()
    
    def onep(self):
        print("1")
        object = other()
        object.open("text")


class other():
    def __init__(self):
        print("init")

    def open(self,text):
        print("2",text)

if __name__ == "__main__":
    on = main()

    