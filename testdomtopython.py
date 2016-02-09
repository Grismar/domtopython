
import domtopython


xml = domtopython.dom_to_python('fews.xml')
print(xml)
exec(xml)

'''

doc = domtopython.DOMDocument()

with doc.test (xmlns='test'):

    def nElements (n):
        for i in range(n):
            doc.data(str(i))

    doc.first(
        "basic content")

    with doc.second(
            "content", " more"):
        with doc.secondfirstsub(name="some name")(
                "hello", " world"):
            nElements(1)
            nElements(2)
            doc.last()
        nElements(3)

doc.print_xml()

'''
