import jcs

if __name__ == '__main__':
    script = "system-check.py"
    change_xml = """<system><scripts><op>
                    <file><name>{0}</name></file></op>
                    </scripts></system>""".format(script)
    jcs.emit_change(change_xml, "change", "xml")
