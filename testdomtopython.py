
import domtopython

doc = domtopython.DOMDocument("test")

def nElements (n):
    for i in range(n):
        doc.data(str(i))

doc.first(
    "basic content")

doc.print_xml()

with doc.second(
        "content", " more"):
    with doc.secondfirstsub(name="some name")(
            "hello", " world"):
        nElements(1)
        nElements(2)
        doc.last()
    nElements(3)

doc.print_xml()
