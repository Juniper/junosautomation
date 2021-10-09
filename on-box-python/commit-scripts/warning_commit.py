from junos import Junos_Configuration
import jcs

def main():
    root = Junos_Configuration
    if not(root.xpath("./chassis/source-route")):
        jcs.emit_warning("IP source-route processing is not enabled.")

if __name__ == '__main__':
    main()
