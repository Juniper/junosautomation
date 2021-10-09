from junos import Junos
from junos import Junos_Context
from junos import Junos_Configuration 
import jcs

def main():
    # Get configuration root object
    root = Junos_Configuration

    # Loop through all logical interfaces
    for element in root.findall("./interfaces/interface/unit"):
        # Missing description
        if element.find('description') == None:
            # Emit warning message to console
            jcs.emit_warning("Interface description is missing: " +
                             element.find('../name').text +
                             " Unit: " + element.find('name').text)

if __name__ == '__main__':
    main()
