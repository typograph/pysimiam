from xmlparser import XMLParser

if __name__ == "__main__":
    parser = XMLParser("/home/tad/Projects/pysimiam/testfiles/parameters.xml")
    print parser.parse("parameters")
